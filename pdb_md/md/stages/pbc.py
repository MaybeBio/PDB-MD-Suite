"""The ``pbc`` stage: periodic-boundary correction and Zn-ligand sanity check.

This stage consumes one replica's production trajectory
(``06_prod/repN/<run>_md_rN.xtc`` and ``.tpr``) and drives ``gmx trjconv``
non-interactively through the five-step PBC protocol:

1. ``whole``      - make molecules whole
2. ``cluster``    - cluster the complex (and its solvent shell)
3. ``whole``      - re-make molecules whole after clustering
4. ``nojump``     - remove jumps across the periodic boundary (via a
                    ``-dump 0`` reference frame)
5. ``center``     - center the configured group in the box

Every selection is supplied on stdin as the 0-based index of a group in the
``.ndx`` file, so the stage never blocks on a ``trjconv`` prompt.  The index is
either generated from ``02_topology/conf.gro`` (``pbc.ndx: auto``) or copied
from a user-supplied file; both are resolved through
:func:`~pdb_md.md.groups.resolve_group`, which fails as a preflight error when a
configured group is absent.  Group resolution and the index-vs-topology atom
count check happen *before* any ``gmx`` invocation so a bad index never leaves
half-written trajectories behind.

After the trajectory is corrected the stage runs ``gmx check`` to confirm the
final frame carries exactly the system atom count, then one ``gmx distance``
call measures every Zn-ligand pair listed in ``02_topology/site_atoms.json``.
A pair whose per-frame maximum exceeds ``pbc.bond_max_angstrom`` (a Zn that
escaped its coordination shell) fails the stage.  A ``pbc_report.json`` records
the group indexes, atom count and per-pair min/mean/max distance.
"""

import json
import re
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from ..config import RunConfig
from ..errors import PreflightError, StageError
from ..gromacs import read_gro
from ..groups import build_groups, read_ndx, resolve_group, write_ndx
from ..plan import RunContext
from ..state import file_fingerprint, hash_or_missing, sha256_parts

PBC_DIR = "07_pbc"
PROD_DIR = "06_prod"
TOPOLOGY_DIR = "02_topology"
CONF_GRO = "conf.gro"
SITE_ATOMS = "site_atoms.json"
REPLICA_PREFIX = "rep"

NDX_NAME = "pbc.ndx"
DISTANCE_XVG = "zn_distances.xvg"
REPORT_NAME = "pbc_report.json"

#: ``gmx check`` summary line that reports the number of atoms read.
_CHECK_ATOMS_RE = re.compile(r"Read\s+(\d+)\s+atoms")


class PbcStage:
    """PBC correction of one replica, driven non-interactively by ``trjconv``."""

    def __init__(self, cfg: RunConfig, replica: int):
        self.cfg = cfg
        self.replica = replica
        self.key = "pbc:rep{}".format(replica)
        self.deps = ("prod:rep{}".format(replica),)

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        root = Path(root)
        prefix = _prefix(cfg, self.replica)
        prod_dir = _stage_dir(root, PROD_DIR, self.replica)

        parts: List[object] = [
            # Produced by ``prod:repN``, so these may be absent on a first
            # ``--dry-run``.
            hash_or_missing(
                prod_dir / "{}.xtc".format(prefix), root, file_fingerprint
            ),
            hash_or_missing(
                prod_dir / "{}.tpr".format(prefix), root, file_fingerprint
            ),
            hash_or_missing(root / TOPOLOGY_DIR / SITE_ATOMS, root),
            asdict(cfg.pbc),
            asdict(cfg.system.species),
        ]
        if cfg.pbc.ndx != "auto":
            parts.append(hash_or_missing(cfg.path(cfg.pbc.ndx), root))
        return sha256_parts(parts)

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = _stage_dir(Path(root), PBC_DIR, self.replica)
        prefix = _prefix(cfg, self.replica)
        return [
            stage_dir / NDX_NAME,
            stage_dir / "{}_1whole.xtc".format(prefix),
            stage_dir / "{}_2cluster.xtc".format(prefix),
            stage_dir / "{}_3whole.xtc".format(prefix),
            stage_dir / "{}_frame0.gro".format(prefix),
            stage_dir / "{}_4nojump.xtc".format(prefix),
            stage_dir / "{}_5center.xtc".format(prefix),
            stage_dir / DISTANCE_XVG,
            stage_dir / REPORT_NAME,
        ]

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        n = self.replica
        prefix = _prefix(cfg, n)
        stage_dir = _stage_dir(root, PBC_DIR, n)
        prod_dir = _stage_dir(root, PROD_DIR, n)
        tpr = prod_dir / "{}.tpr".format(prefix)
        prod_xtc = prod_dir / "{}.xtc".format(prefix)
        conf_gro = root / TOPOLOGY_DIR / CONF_GRO
        site_path = root / TOPOLOGY_DIR / SITE_ATOMS

        stage_dir.mkdir(parents=True, exist_ok=True)

        # 1. Index file: build it from conf.gro or copy the user's file.  The
        # topology ``conf.gro`` is also the reference for the atom count.
        try:
            conf = read_gro(conf_gro)
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot read {}: {}".format(conf_gro, exc), cwd=stage_dir
            )
        expected_atoms = len(conf.atoms)

        ndx = stage_dir / NDX_NAME
        if cfg.pbc.ndx == "auto":
            write_ndx(build_groups(conf, cfg.system.species), ndx)
        else:
            source = cfg.path(cfg.pbc.ndx)
            try:
                shutil.copyfile(str(source), str(ndx))
            except OSError as exc:
                raise _stage_error(
                    "cannot copy user index {}: {}".format(source, exc),
                    cwd=stage_dir,
                )

        # 2. Resolve every configured group and validate the index against the
        # topology atom count.  This must happen before any gmx call so a bad
        # index fails cleanly without partial trajectory output.
        cluster_idx = self._resolve(ndx, cfg.pbc.groups.cluster)
        center_idx = self._resolve(ndx, cfg.pbc.groups.center)
        out_idx, out_atoms = resolve_group(ndx, cfg.pbc.groups.output)
        all_groups = read_ndx(ndx)
        # The whole-system group is normally named ``System``.  A user index
        # may use a different name for its final output group, so fall back to
        # the configured output selection in that case.
        system_atoms = all_groups.get("System", out_atoms)
        if len(system_atoms) != expected_atoms:
            raise PreflightError(
                "index System group has {} atoms but {} has {}".format(
                    len(system_atoms), conf_gro, expected_atoms
                ),
                hint=(
                    "Regenerate pbc.ndx from the topology conf.gro or point "
                    "pbc.ndx at a matching index file."
                ),
            )

        # 3. The five-step protocol (six trjconv invocations).  Outputs are
        # bare filenames relative to the stage directory; prod inputs are
        # absolute.
        whole1 = "{}_1whole.xtc".format(prefix)
        cluster2 = "{}_2cluster.xtc".format(prefix)
        whole3 = "{}_3whole.xtc".format(prefix)
        frame0 = "{}_frame0.gro".format(prefix)
        nojump4 = "{}_4nojump.xtc".format(prefix)
        center5 = "{}_5center.xtc".format(prefix)

        self._trjconv(
            ctx,
            stage_dir,
            ["-s", str(tpr), "-f", str(prod_xtc), "-n", str(ndx),
             "-pbc", "whole", "-o", whole1],
            out_idx,
        )
        self._trjconv(
            ctx,
            stage_dir,
            ["-s", str(tpr), "-f", whole1, "-n", str(ndx),
             "-pbc", "cluster", "-o", cluster2],
            cluster_idx,
            out_idx,
        )
        self._trjconv(
            ctx,
            stage_dir,
            ["-s", str(tpr), "-f", cluster2, "-n", str(ndx),
             "-pbc", "whole", "-o", whole3],
            out_idx,
        )
        self._trjconv(
            ctx,
            stage_dir,
            ["-s", str(tpr), "-f", whole3, "-n", str(ndx),
             "-dump", "0", "-o", frame0],
            out_idx,
        )
        self._trjconv(
            ctx,
            stage_dir,
            ["-s", frame0, "-f", whole3, "-n", str(ndx),
             "-pbc", "nojump", "-o", nojump4],
            out_idx,
        )
        self._trjconv(
            ctx,
            stage_dir,
            ["-s", str(tpr), "-f", nojump4, "-n", str(ndx),
             "-center", "-o", center5],
            center_idx,
            out_idx,
        )

        # 4. Atom-count sanity check on the final trajectory.
        check_output = ctx.runner.run_capture(
            [cfg.tools.gmx, "check", "-f", center5], cwd=stage_dir
        )
        match = _CHECK_ATOMS_RE.search(check_output)
        if match is None:
            raise _stage_error(
                "could not parse an atom count from 'gmx check' output",
                cwd=stage_dir,
                tail=check_output.splitlines()[-50:],
            )
        checked_atoms = int(match.group(1))
        if checked_atoms != expected_atoms:
            raise _stage_error(
                "gmx check reports {} atoms in {}, expected {} (System)".format(
                    checked_atoms, center5, expected_atoms
                ),
                cwd=stage_dir,
                tail=check_output.splitlines()[-50:],
            )

        # 5. Zn-ligand distance check over the corrected trajectory.
        pairs, select_args = self._read_distance_pairs(site_path, stage_dir)
        ctx.runner.run(
            [cfg.tools.gmx, "distance", "-s", str(tpr), "-f", center5]
            + select_args
            + ["-oav", DISTANCE_XVG],
            log_name="pbc",
            cwd=stage_dir,
        )
        stats = self._read_distance_stats(
            stage_dir / DISTANCE_XVG,
            pairs,
            stage_dir,
            cfg.pbc.bond_max_angstrom,
        )

        # 6. Report.
        report: Dict[str, object] = {
            "steps": list(cfg.pbc.steps),
            "groups": {
                "cluster": {
                    "name": cfg.pbc.groups.cluster,
                    "index": cluster_idx,
                },
                "center": {
                    "name": cfg.pbc.groups.center,
                    "index": center_idx,
                },
                "output": {
                    "name": cfg.pbc.groups.output,
                    "index": out_idx,
                },
            },
            "n_atoms": expected_atoms,
            "bond_max_angstrom": cfg.pbc.bond_max_angstrom,
            "distance_pairs": stats,
        }
        (stage_dir / REPORT_NAME).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = _stage_dir(root, PBC_DIR, self.replica)
        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "pbc artifact is missing or empty: {}".format(path),
                    cwd=stage_dir,
                )

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _resolve(ndx: Path, name: str) -> int:
        """Return the 0-based index of ``name`` in ``ndx``."""
        index, _atoms = resolve_group(ndx, name)
        return index

    def _trjconv(
        self,
        ctx: RunContext,
        stage_dir: Path,
        args: Sequence[str],
        *selections: int,
    ) -> None:
        """Run one ``trjconv`` invocation, feeding group indexes on stdin."""
        stdin_text = "".join("{}\n".format(index) for index in selections)
        ctx.runner.run(
            [self.cfg.tools.gmx, "trjconv"] + list(args),
            log_name="pbc",
            cwd=stage_dir,
            stdin_text=stdin_text,
        )

    @staticmethod
    def _read_distance_pairs(
        site_path: Path, stage_dir: Path
    ) -> Tuple[List[Tuple[int, int, int, int]], List[str]]:
        """Read ``site_atoms.json`` and build the ``-select`` arguments.

        Returns ``(pairs, select_args)`` where each pair is
        ``(site_number, zn_atom, ligand_atom, ligand_position)``.
        """
        try:
            raw_sites = json.loads(site_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise _stage_error(
                "cannot read {}: {}".format(site_path, exc), cwd=stage_dir
            )
        if not isinstance(raw_sites, list):
            raise _stage_error(
                "{} must be a JSON list".format(site_path), cwd=stage_dir
            )

        pairs: List[Tuple[int, int, int, int]] = []
        select_args: List[str] = []
        try:
            for site_number, site in enumerate(raw_sites, 1):
                zn = int(site["zn"])
                for ligand_position, ligand in enumerate(
                    site["ligand_atoms"], 1
                ):
                    ligand = int(ligand)
                    pairs.append(
                        (site_number, zn, ligand, ligand_position)
                    )
                    select_args.extend(
                        [
                            "-select",
                            "atomnr {} plus atomnr {}".format(zn, ligand),
                        ]
                    )
        except (KeyError, TypeError, ValueError) as exc:
            raise _stage_error(
                "malformed {}: {}".format(site_path, exc), cwd=stage_dir
            )

        if not pairs:
            raise _stage_error(
                "{} lists no Zn-ligand pairs".format(site_path), cwd=stage_dir
            )
        return pairs, select_args

    @staticmethod
    def _read_distance_stats(
        xvg_path: Path,
        pairs: Sequence[Tuple[int, int, int, int]],
        stage_dir: Path,
        limit: float,
    ) -> List[Dict[str, object]]:
        """Parse the distance ``xvg`` and enforce ``pbc.bond_max_angstrom``."""
        try:
            text = xvg_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise _stage_error(
                "cannot read {}: {}".format(xvg_path, exc), cwd=stage_dir
            )

        n_pairs = len(pairs)
        rows: List[List[float]] = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("@"):
                continue
            fields = line.split()
            if len(fields) != n_pairs + 1:
                raise _stage_error(
                    "{}: expected time plus {} distance columns, got {}".format(
                        xvg_path.name, n_pairs, len(fields)
                    ),
                    cwd=stage_dir,
                )
            try:
                values = [float(field) for field in fields]
            except ValueError:
                raise _stage_error(
                    "{}: non-numeric value in line {!r}".format(
                        xvg_path.name, line
                    ),
                    cwd=stage_dir,
                )
            # Drop the time column; the remaining columns are the pairs.
            rows.append(values[1:])

        if not rows:
            raise _stage_error(
                "{} contains no distance data".format(xvg_path.name),
                cwd=stage_dir,
            )

        return _pair_stats(rows, pairs, stage_dir, limit)


def _pair_stats(
    rows: Sequence[Sequence[float]],
    pairs: Sequence[Tuple[int, int, int, int]],
    stage_dir: Path,
    limit: float,
) -> List[Dict[str, object]]:
    """Compute per-pair min/mean/max and raise on any over-limit maximum."""
    stats: List[Dict[str, object]] = []
    violations: List[str] = []
    for column, (site_number, zn, ligand, ligand_position) in enumerate(pairs):
        values = [row[column] for row in rows]
        minimum = min(values)
        maximum = max(values)
        mean = sum(values) / len(values)
        stats.append(
            {
                "site": site_number,
                "zn": zn,
                "ligand": ligand,
                "min": minimum,
                "mean": mean,
                "max": maximum,
            }
        )
        if maximum > limit:
            violations.append(
                "site {} ligand {}: {:.2f} A > {:.2f} A".format(
                    site_number, ligand_position, maximum, limit
                )
            )
    if violations:
        raise _stage_error("; ".join(violations), cwd=stage_dir)
    return stats


def _prefix(cfg: RunConfig, replica: int) -> str:
    """The output prefix shared by every file of replica ``replica``."""
    return "{}_md_r{}".format(cfg.run_name, replica)


def _stage_dir(root: Path, base: str, replica: int) -> Path:
    return Path(root) / base / "{}{}".format(REPLICA_PREFIX, replica)


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
