"""The ``zaff`` stage: two ``tleap`` passes that build the AMBER topology.

Pass 1 loads the ZAFF-prepared structure, bonds each Zn to its four ligands and
solvates the box.  Its ``leap.log`` supplies the water count and net charge
that drive the SPLIT ion arithmetic.  Pass 2 reloads the solvated topology and
adds the neutralizing/salting ions.  The stage then writes
``01_zaff/zaff_report.json``, which later stages read for the LEaP residue
positions (``position``) and the ion counts (``salt.counter``/``salt.coion``).

All ``tleap`` output lives in ``01_zaff/`` because the command runs with that
directory as its working directory; the rendered scripts therefore use
relative ``saveamberparm``/``savepdb`` names.
"""

import json
import re
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from ..config import RunConfig
from ..coords import read_pdb
from ..errors import ConfigError, StageError
from ..plan import RunContext
from ..state import hash_or_missing, sha256_parts
from ..tleap import (
    compute_split_counts,
    count_prmtop_atoms,
    parse_leap_log,
    render_pass1_script,
    render_pass2_script,
)
from ..zinc import SiteCheck, preflight_structure, validate_sites

STAGE_DIR = "01_zaff"
REPORT_NAME = "zaff_report.json"
PASS1_SCRIPT = "tleap_zaff.in"
PASS2_SCRIPT = "tleap_zaff_pass2.in"
LEAP_LOG = "leap.log"
LEAP_PASS1_LOG = "leap_pass1.log"

#: Lines of ``leap.log`` echoed when its parse yields nothing usable.
_LOG_HINT = re.compile(r"charge|Added|solvate", re.IGNORECASE)


class ZaffStage:
    """First pipeline stage: AMBER topology via two ``tleap`` passes."""

    key = "zaff"
    deps = ("preprocess",)

    def __init__(self, cfg: RunConfig):
        # ``run(ctx)`` reads configuration from this binding, not ``ctx.cfg``;
        # the CLI and tests may hand the stage a config that diverges from the
        # context's (e.g. a fallback override).
        self.cfg = cfg

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        return sha256_parts(
            [
                # Produced by the ``preprocess`` dependency, so it may be absent
                # on a first ``--dry-run``.
                hash_or_missing(Path(root) / "00_input/structure.pdb", root),
                asdict(cfg.forcefield),
                asdict(cfg.system.solvate),
                asdict(cfg.system.salt),
                [asdict(site) for site in cfg.zinc_sites],
                asdict(cfg.coordination_check),
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = Path(root) / STAGE_DIR
        prefix = cfg.run_name
        paths = [
            stage_dir / PASS1_SCRIPT,
            stage_dir / PASS2_SCRIPT,
            stage_dir / LEAP_LOG,
            stage_dir / LEAP_PASS1_LOG,
        ]
        paths.extend(self._topology_paths(stage_dir, prefix))
        paths.append(stage_dir / REPORT_NAME)
        return paths

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        stage_dir = root / STAGE_DIR
        prefix = cfg.run_name
        state = root / "00_input/structure.pdb"

        # 1. Parse and preflight the structure that ``preprocess`` produced.
        table = read_pdb(state)
        preflight_structure(table)
        sites = validate_sites(table, list(cfg.zinc_sites), cfg.coordination_check)

        # 2. Refuse (or warn about) Zn-ligand bonds outside the window before
        #    invoking tleap at all.
        warnings: List[str] = []
        violations = [
            violation for site in sites for violation in site.bond_violations
        ]
        if violations:
            if cfg.coordination_check.on_violation == "warn":
                warnings.extend(violations)
            else:
                raise _stage_error(
                    "zinc coordination bond violations:\n{}".format(
                        "\n".join("  - " + v for v in violations)
                    ),
                    hint=(
                        "Fix the structure or set "
                        "coordination_check.on_violation: warn to continue."
                    ),
                    cwd=stage_dir,
                )

        stage_dir.mkdir(parents=True, exist_ok=True)

        # 3. Pass 1: dry complex -> solvated box.
        pass1 = render_pass1_script(cfg, table, sites, prefix)
        (stage_dir / PASS1_SCRIPT).write_text(pass1)
        ctx.runner.run(
            [cfg.tools.tleap, "-f", PASS1_SCRIPT],
            log_name="zaff",
            cwd=stage_dir,
        )

        # 4. Read the pass-1 log for the water count / net charge.
        leap_log = stage_dir / LEAP_LOG
        if not leap_log.exists():
            raise _stage_error(
                "pass 1 did not write {}/{}".format(STAGE_DIR, LEAP_LOG),
                hint="Check the tleap command log for why pass 1 failed.",
                cwd=stage_dir,
            )
        shutil.copyfile(leap_log, stage_dir / LEAP_PASS1_LOG)
        log_text = leap_log.read_text(encoding="utf-8", errors="replace")
        info = parse_leap_log(log_text)

        water_count = info.water_count
        net_charge = info.net_charge
        if water_count is None:
            water_count = cfg.system.salt.water_count
        if net_charge is None:
            net_charge = cfg.system.salt.net_charge
        if water_count is None or net_charge is None:
            tail = [
                line
                for line in log_text.splitlines()
                if _LOG_HINT.search(line)
            ][-10:]
            missing = []
            if water_count is None:
                missing.append("system.salt.water_count")
            if net_charge is None:
                missing.append("system.salt.net_charge")
            raise _stage_error(
                "could not determine the water count / net charge from "
                "{}/{}; set {} in run.yaml to override".format(
                    STAGE_DIR, LEAP_LOG, " and ".join(missing)
                ),
                hint=(
                    "The pass-1 leap.log lacked the expected 'Added ... "
                    "residues' / 'unperturbed charge' lines."
                ),
                cwd=stage_dir,
                tail=tail,
            )

        # 5. SPLIT ion counts -> pass 2 (ions only; box is already solvated).
        counts = compute_split_counts(
            water_count,
            net_charge,
            cfg.system.salt.concentration_M,
            cfg.system.salt.cation,
            cfg.system.salt.anion,
        )
        pass2 = render_pass2_script(cfg, counts, prefix)
        (stage_dir / PASS2_SCRIPT).write_text(pass2)
        ctx.runner.run(
            [cfg.tools.tleap, "-f", PASS2_SCRIPT],
            log_name="zaff",
            cwd=stage_dir,
        )

        # 6. Every topology/coordinate/PDB file must exist and be non-empty,
        #    and solvation may only ever add atoms.
        topology = self._topology_paths(stage_dir, prefix)
        for path in topology:
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "tleap did not produce a non-empty {}".format(path),
                    hint="Check the tleap command log.",
                    cwd=stage_dir,
                )
        dry_atoms = count_prmtop_atoms(
            stage_dir / "{}_dry.prmtop".format(prefix)
        )
        solv_atoms = count_prmtop_atoms(
            stage_dir / "{}_solv.prmtop".format(prefix)
        )
        if solv_atoms <= dry_atoms:
            raise _stage_error(
                "solvated topology has {} atoms but the dry complex has {}; "
                "solvateBox did not add solvent".format(solv_atoms, dry_atoms),
                hint="Check the tleap command log for solvateBox errors.",
                cwd=stage_dir,
            )

        # 7. Write the report later stages consume.
        report = {
            "n_atoms_input": len(table.atoms),
            "n_sites": len(sites),
            "zinc_sites": [
                _site_report(site, cfg.zinc_sites[site.index - 1])
                for site in sites
            ],
            "salt": {
                "counter": counts.counter,
                "coion": counts.coion,
                "counter_name": counts.counter_name,
                "coion_name": counts.coion_name,
                "water_count": water_count,
                "net_charge": net_charge,
            },
            "warnings": warnings,
        }
        (stage_dir / REPORT_NAME).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    def verify(self, cfg: RunConfig, root: Path) -> None:
        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "zaff artifact is missing or empty: {}".format(path),
                    cwd=Path(root) / STAGE_DIR,
                )

        report_path = Path(root) / STAGE_DIR / REPORT_NAME
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot parse {}: {}".format(report_path, exc),
                cwd=Path(root) / STAGE_DIR,
            )

        salt = report.get("salt") or {}
        counter = salt.get("counter")
        coion = salt.get("coion")
        water_count = salt.get("water_count")
        net_charge = salt.get("net_charge")
        for name, value in (
            ("counter", counter),
            ("coion", coion),
            ("water_count", water_count),
            ("net_charge", net_charge),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise _stage_error(
                    "zaff report salt.{} is not an integer: {!r}".format(
                        name, value
                    ),
                    cwd=Path(root) / STAGE_DIR,
                )
        if counter < 0 or coion < 0:
            raise _stage_error(
                "zaff report salt counts must be non-negative "
                "(counter={}, coion={})".format(counter, coion),
                cwd=Path(root) / STAGE_DIR,
            )

        try:
            expected = compute_split_counts(
                water_count,
                net_charge,
                cfg.system.salt.concentration_M,
                cfg.system.salt.cation,
                cfg.system.salt.anion,
            )
        except ConfigError as exc:
            raise _stage_error(
                "zaff report salt counts are invalid: {}".format(exc.message),
                cwd=Path(root) / STAGE_DIR,
            )
        if (counter, coion) != (expected.counter, expected.coion):
            raise _stage_error(
                "zaff report salt counts (counter={}, coion={}) do not match "
                "water_count={} / net_charge={} (expected {}, {})".format(
                    counter,
                    coion,
                    water_count,
                    net_charge,
                    expected.counter,
                    expected.coion,
                ),
                cwd=Path(root) / STAGE_DIR,
            )

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _topology_paths(stage_dir: Path, prefix: str) -> List[Path]:
        paths: List[Path] = []
        for suffix in ("dry", "solv"):
            for ext in ("prmtop", "inpcrd", "pdb"):
                paths.append(stage_dir / "{}_{}.{}".format(prefix, suffix, ext))
        return paths


def _site_report(site: SiteCheck, config_site) -> Dict[str, object]:
    """Serialise one :class:`SiteCheck` for ``zaff_report.json``.

    ``atom_index`` is a position in the *input* structure (report-only); every
    cross-stage reference uses the LEaP residue ``position``.
    """
    return {
        "index": site.index,
        "center_id": site.center_id,
        "zn": {
            "position": site.zn_position,
            "resid": config_site.zn.resid,
            "atom_index": site.zn_atom_index,
        },
        "ligands": [
            {
                "position": ligand.position,
                "resid": ligand.ref.resid,
                "resname": ligand.ref.resname,
                "atom": ligand.ref.atom,
                "atom_index": ligand.atom_index,
                "distance": ligand.distance,
            }
            for ligand in site.ligands
        ],
        "extra_near": [asdict(extra) for extra in site.extra_near],
        "bond_violations": list(site.bond_violations),
    }


def _stage_error(
    message: str,
    cwd: Optional[Path] = None,
    hint: Optional[str] = None,
    tail: Optional[Sequence[str]] = None,
) -> StageError:
    """Build a :class:`StageError` for failures that are not a subprocess exit."""
    return StageError(
        message,
        argv=[],
        cwd=cwd,
        returncode=0,
        tail=list(tail or []),
        hint=hint,
    )
