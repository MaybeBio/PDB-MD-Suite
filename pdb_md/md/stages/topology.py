"""The ``topology`` stage: AMBER -> GROMACS conversion and topology checks.

This stage runs the ParmEd conversion script with ``tools.parmed_python`` to
turn ``01_zaff/<run>_solv.prmtop``/``.inpcrd`` into ``02_topology/topol_raw.top``
and ``02_topology/conf.gro``.  It then:

* adds the heavy-atom position restraints that ParmEd does not emit (via the
  existing :func:`pdb_md.restrain.restrain_topology`) and writes the patched
  ``topol.top``;
* checks that the topology's atom total equals the number of atoms in
  ``conf.gro``;
* maps each zinc site reported by ``01_zaff/zaff_report.json`` to 1-based atom
  numbers in ``conf.gro`` and stores them in ``site_atoms.json`` for later
  stages;
* writes ``topology_report.json`` (solutes, atom count, restraint files).

``verify`` re-reads those artifacts only and re-runs the same consistency
checks, so a stage that was edited by hand after it ran is rejected.
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from pdb_md.restrain import restrain_topology

from .. import parmed_convert
from ..config import RunConfig
from ..errors import StageError
from ..gromacs import read_gro, read_top, total_atoms
from ..plan import RunContext
from ..state import hash_or_missing, sha256_parts
from ..tleap import prmtop_residue_atoms
from ..zinc import map_site_atoms

STAGE_DIR = "02_topology"
ZAFF_DIR = "01_zaff"
ZAFF_REPORT = "zaff_report.json"
TOPOL = "topol.top"
TOPOL_RAW = "topol_raw.top"
CONF_GRO = "conf.gro"
SITE_ATOMS = "site_atoms.json"
REPORT_NAME = "topology_report.json"


class TopologyStage:
    """Convert the solvated AMBER topology to GROMACS and validate it."""

    key = "topology"
    deps = ("zaff",)

    def __init__(self, cfg: RunConfig):
        # ``run`` reads configuration from this binding, not ``ctx.cfg`` (see
        # the ``zaff`` stage for the rationale).
        self.cfg = cfg

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        zaff_dir = Path(root) / ZAFF_DIR
        return sha256_parts(
            [
                # Produced by the ``zaff`` dependency, so any of these may be
                # absent on a first ``--dry-run``.
                hash_or_missing(
                    zaff_dir / "{}_solv.prmtop".format(cfg.run_name), root
                ),
                hash_or_missing(
                    zaff_dir / "{}_solv.inpcrd".format(cfg.run_name), root
                ),
                hash_or_missing(zaff_dir / ZAFF_REPORT, root),
                asdict(cfg.topology),
                asdict(cfg.system.species),
                cfg.tools.parmed_python,
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = Path(root) / STAGE_DIR
        paths = [
            stage_dir / TOPOL,
            stage_dir / CONF_GRO,
            stage_dir / TOPOL_RAW,
            stage_dir / SITE_ATOMS,
            stage_dir / REPORT_NAME,
        ]
        # Posre files are only known after conversion has run; before then the
        # glob is empty and the planner simply sees the stage as incomplete.
        paths.extend(sorted(stage_dir.glob("posre_*.itp")))
        return paths

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        stage_dir = root / STAGE_DIR
        zaff_dir = root / ZAFF_DIR

        prmtop = zaff_dir / "{}_solv.prmtop".format(cfg.run_name)
        inpcrd = zaff_dir / "{}_solv.inpcrd".format(cfg.run_name)
        report_path = zaff_dir / ZAFF_REPORT
        topol_raw = stage_dir / TOPOL_RAW
        topol = stage_dir / TOPOL
        gro_path = stage_dir / CONF_GRO

        # The ParmEd helper writes straight to the paths given on the command
        # line, so the output directory must exist before it runs.
        stage_dir.mkdir(parents=True, exist_ok=True)

        script = Path(parmed_convert.__file__)
        ctx.runner.run(
            [
                cfg.tools.parmed_python,
                str(script),
                "--prmtop",
                str(prmtop),
                "--inpcrd",
                str(inpcrd),
                "--top",
                str(topol_raw),
                "--gro",
                str(gro_path),
            ],
            log_name="topology",
            cwd=stage_dir,
        )

        for path in (topol_raw, gro_path):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "ParmEd did not produce a non-empty {}".format(path),
                    hint="Check the topology command log.",
                    cwd=stage_dir,
                )

        try:
            topology = read_top(topol_raw)
            gro = read_gro(gro_path)
            solutes = _solute_names(topology, cfg)
            zaff_report = _read_json(report_path)
            sites = zaff_report.get("zinc_sites", [])
            residue_atoms = prmtop_residue_atoms(prmtop)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise _stage_error(
                "cannot read the converted topology or zaff report: {}".format(
                    exc
                ),
                cwd=stage_dir,
            )

        if not solutes:
            raise _stage_error(
                "no solute moleculetype found in the converted topology",
                hint=(
                    "Every moleculetype's residues are in "
                    "system.species.solvent_resnames / salt ions; check the "
                    "conversion."
                ),
                cwd=stage_dir,
            )

        restrain_topology(topol_raw, solutes, cfg.topology.posre_fc, topol)

        try:
            n_atoms = total_atoms(read_top(topol))
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot read the restrained topology: {}".format(exc),
                cwd=stage_dir,
            )
        if n_atoms != len(gro.atoms):
            raise _stage_error(
                "atom count mismatch: topology {}, conf.gro {}".format(
                    n_atoms, len(gro.atoms)
                ),
                hint=(
                    "The ParmEd conversion disagrees with the coordinate file; "
                    "check the topology command log."
                ),
                cwd=stage_dir,
            )

        try:
            site_atoms = map_site_atoms(sites, residue_atoms, gro.atoms)
        except StageError as exc:
            raise _stage_error(exc.message, hint=exc.hint, cwd=stage_dir)

        sites_payload = [
            {"zn": item.zn, "ligand_atoms": list(item.ligand_atoms)}
            for item in site_atoms
        ]
        (stage_dir / SITE_ATOMS).write_text(
            json.dumps(sites_payload, indent=2) + "\n", encoding="utf-8"
        )

        report: Dict[str, object] = {
            "solutes": solutes,
            "n_atoms": n_atoms,
            "posres": sorted(
                path.name for path in stage_dir.glob("posre_*.itp")
            ),
            "sites": sites_payload,
        }
        (stage_dir / REPORT_NAME).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = root / STAGE_DIR
        zaff_dir = root / ZAFF_DIR

        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "topology artifact is missing or empty: {}".format(path),
                    cwd=stage_dir,
                )

        try:
            topology = read_top(stage_dir / TOPOL)
            gro = read_gro(stage_dir / CONF_GRO)
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot read the topology artifacts: {}".format(exc),
                cwd=stage_dir,
            )

        try:
            n_atoms = total_atoms(topology)
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot count the topology atoms: {}".format(exc),
                cwd=stage_dir,
            )
        if n_atoms != len(gro.atoms):
            raise _stage_error(
                "atom count mismatch: topology {}, conf.gro {}".format(
                    n_atoms, len(gro.atoms)
                ),
                cwd=stage_dir,
            )

        solutes = _solute_names(topology, cfg)
        if not solutes:
            raise _stage_error(
                "no solute moleculetype found in {}".format(TOPOL),
                cwd=stage_dir,
            )
        for name in solutes:
            itp = stage_dir / "posre_{}.itp".format(name)
            if not itp.is_file() or itp.stat().st_size == 0:
                raise _stage_error(
                    "solute moleculetype {!r} has no position-restraint file: "
                    "{}".format(name, itp),
                    cwd=stage_dir,
                )

        metal_names = set(cfg.system.species.metal_resnames)
        if not any(
            atom.resname in metal_names
            for moleculetype in topology.moleculetypes
            for atom in moleculetype.atoms
        ):
            raise _stage_error(
                "no moleculetype in {} contains a metal residue ({})".format(
                    TOPOL, ", ".join(sorted(metal_names)) or "<none>"
                ),
                cwd=stage_dir,
            )

        try:
            site_atoms = _read_json(stage_dir / SITE_ATOMS)
            zaff_sites = _read_json(zaff_dir / ZAFF_REPORT).get(
                "zinc_sites", []
            )
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot read the site mapping: {}".format(exc), cwd=stage_dir
            )

        if len(site_atoms) != len(zaff_sites):
            raise _stage_error(
                "site_atoms.json has {} sites but {} reports {}".format(
                    len(site_atoms), ZAFF_REPORT, len(zaff_sites)
                ),
                cwd=stage_dir,
            )

        for index, (mapped, report_site) in enumerate(
            zip(site_atoms, zaff_sites)
        ):
            self._check_site(index, mapped, report_site, gro, cfg, stage_dir)

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _check_site(
        index: int,
        mapped: dict,
        report_site: dict,
        gro,
        cfg: RunConfig,
        stage_dir: Path,
    ) -> None:
        """Confirm mapped atom numbers name the right atoms in ``conf.gro``.

        Residue names for the zinc atom come from this run's configuration;
        ligand names/atoms come from the zaff report because that reflects the
        post-``tleap`` residue naming the converted ``conf.gro`` carries.
        """
        if index >= len(cfg.zinc_sites):
            raise _stage_error(
                "zinc site {} is missing from the configuration".format(
                    index + 1
                ),
                cwd=stage_dir,
            )
        zn_resname = cfg.zinc_sites[index].zn.resname

        zn_number = mapped.get("zn")
        if not isinstance(zn_number, int) or not (
            1 <= zn_number <= len(gro.atoms)
        ):
            raise _stage_error(
                "zinc site {}: Zn atom number {!r} is out of range for "
                "conf.gro ({} atoms)".format(
                    index + 1, zn_number, len(gro.atoms)
                ),
                cwd=stage_dir,
            )
        zn_atom = gro.atoms[zn_number - 1]
        if zn_atom.name != "ZN" or zn_atom.resname != zn_resname:
            raise _stage_error(
                "zinc site {}: conf.gro atom {} is {}/{}, expected ZN/{}"
                .format(
                    index + 1,
                    zn_number,
                    zn_atom.resname,
                    zn_atom.name,
                    zn_resname,
                ),
                cwd=stage_dir,
            )

        ligand_numbers = mapped.get("ligand_atoms") or []
        report_ligands = report_site.get("ligands") or []
        if len(ligand_numbers) != len(report_ligands):
            raise _stage_error(
                "zinc site {}: site_atoms.json has {} ligand atoms but the "
                "zaff report lists {}".format(
                    index + 1, len(ligand_numbers), len(report_ligands)
                ),
                cwd=stage_dir,
            )
        for position, (number, ligand) in enumerate(
            zip(ligand_numbers, report_ligands)
        ):
            if not isinstance(number, int) or not (
                1 <= number <= len(gro.atoms)
            ):
                raise _stage_error(
                    "zinc site {}: ligand atom number {!r} is out of range "
                    "for conf.gro ({} atoms)".format(
                        index + 1, number, len(gro.atoms)
                    ),
                    cwd=stage_dir,
                )
            atom = gro.atoms[number - 1]
            if (
                atom.name != ligand.get("atom")
                or atom.resname != ligand.get("resname")
            ):
                raise _stage_error(
                    "zinc site {}: conf.gro atom {} is {}/{}, expected {}/{}"
                    .format(
                        index + 1,
                        number,
                        atom.resname,
                        atom.name,
                        ligand.get("resname"),
                        ligand.get("atom"),
                    ),
                    cwd=stage_dir,
                )


def _solute_names(topology, cfg: RunConfig) -> List[str]:
    """Moleculetypes with at least one residue that is not solvent or ion."""
    excluded = set(cfg.system.species.solvent_resnames)
    excluded.add(cfg.system.salt.cation)
    excluded.add(cfg.system.salt.anion)
    return [
        moleculetype.name
        for moleculetype in topology.moleculetypes
        if any(atom.resname not in excluded for atom in moleculetype.atoms)
    ]


def _read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


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
