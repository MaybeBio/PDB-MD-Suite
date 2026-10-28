"""The ``em`` stage: chained GROMACS energy minimisation.

Each ``cfg.mdp.em`` entry is minimised in turn.  The first pass starts from
``02_topology/conf.gro``; every later pass continues from the previous pass's
minimised structure, so ``em1.gro -> em2.gro -> ...`` forms a chain.  Both
``grompp`` and ``mdrun`` run with the run root as their working directory and
every path handed to ``gmx`` is absolute, so the ``03_em/`` outputs land in a
stable place regardless of the caller's cwd.

``run`` validates each output structure inline (existence, atom count against
``conf.gro`` and a raw-text scan for non-finite coordinates), then writes
``03_em/em_report.json``.  ``verify`` re-reads the artifacts and re-runs the
same checks through the shared helpers, so a hand-edited stage is rejected.

A missing ``-DFLEXIBLE`` define when ``topol.top`` contains ``[ settles ]`` is
recorded as a warning in the report; it never changes the exit status.
"""

import json
import re
from pathlib import Path
from typing import List, Optional, Sequence

from ..config import RunConfig
from ..errors import StageError
from ..gromacs import read_gro
from ..mdp import read_mdp
from ..plan import RunContext
from ..state import hash_or_missing, sha256_parts

STAGE_DIR = "03_em"
TOPOLOGY_DIR = "02_topology"
TOPOL = "topol.top"
CONF_GRO = "conf.gro"
REPORT_NAME = "em_report.json"

#: Non-finite coordinates in a ``.gro``.  :func:`read_gro` deliberately ignores
#: the coordinate columns, so the check must be a raw-text scan.
_NONFINITE_RE = re.compile(r"nan|inf", re.IGNORECASE)
#: ``[ settles ]`` section header, tolerating interior whitespace and case.
_SETTLES_RE = re.compile(r"\[\s*settles\s*\]", re.IGNORECASE)


class EmStage:
    """Chained energy minimisation of the topology stage's coordinates."""

    key = "em"
    deps = ("topology",)

    def __init__(self, cfg: RunConfig):
        # ``run`` reads configuration from this binding, not ``ctx.cfg`` (see
        # the ``zaff`` stage for the rationale).
        self.cfg = cfg

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        root = Path(root)
        topology_dir = root / TOPOLOGY_DIR
        em_mdps = [hash_or_missing(cfg.path(mdp), root) for mdp in cfg.mdp.em]
        posre = [
            hash_or_missing(path, root)
            for path in sorted(topology_dir.glob("posre_*.itp"))
        ]
        return sha256_parts(
            [
                # Produced by the ``topology`` dependency, so any of these may
                # be absent on a first ``--dry-run``.
                hash_or_missing(topology_dir / TOPOL, root),
                hash_or_missing(topology_dir / CONF_GRO, root),
                *posre,
                *em_mdps,
                cfg.stage_maxwarn("em"),
                list(cfg.mdrun.args),
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = Path(root) / STAGE_DIR
        paths: List[Path] = []
        for i in range(1, len(cfg.mdp.em) + 1):
            for ext in ("tpr", "gro", "edr", "log"):
                paths.append(stage_dir / "em{}.{}".format(i, ext))
        paths.append(stage_dir / REPORT_NAME)
        return paths

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        stage_dir = root / STAGE_DIR
        topology_dir = root / TOPOLOGY_DIR
        topol = topology_dir / TOPOL
        conf_gro = topology_dir / CONF_GRO

        # The fake/real mdrun writes into ``03_em/`` and gmx is invoked with
        # the run root as cwd, so the directory must exist first.
        stage_dir.mkdir(parents=True, exist_ok=True)

        try:
            topol_text = topol.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise _stage_error(
                "cannot read the topology input {}: {}".format(topol, exc),
                hint="Run the topology stage first.",
                cwd=stage_dir,
            )
        expected_atoms = _expected_atom_count(conf_gro, stage_dir)

        maxwarn = str(cfg.stage_maxwarn("em"))
        previous = conf_gro
        for i, mdp in enumerate(cfg.mdp.em, 1):
            tpr = stage_dir / "em{}.tpr".format(i)
            ctx.runner.run(
                [
                    cfg.tools.gmx,
                    "grompp",
                    "-f",
                    str(cfg.path(mdp)),
                    "-c",
                    str(previous),
                    "-r",
                    str(previous),
                    "-p",
                    str(topol),
                    "-o",
                    str(tpr),
                    "-maxwarn",
                    maxwarn,
                ],
                log_name="em",
                cwd=ctx.root,
            )

            prefix = stage_dir / "em{}".format(i)
            mdrun_argv = [cfg.tools.gmx, "mdrun", "-deffnm", str(prefix)]
            mdrun_argv.extend(cfg.mdrun.args)
            ctx.runner.run(mdrun_argv, log_name="em", cwd=ctx.root)

            previous = stage_dir / "em{}.gro".format(i)
            _check_gro(previous, expected_atoms, stage_dir)

        report = {"warnings": _flexible_warnings(cfg, topol_text)}
        (stage_dir / REPORT_NAME).write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = root / STAGE_DIR

        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "em artifact is missing or empty: {}".format(path),
                    cwd=stage_dir,
                )

        expected_atoms = _expected_atom_count(
            root / TOPOLOGY_DIR / CONF_GRO, stage_dir
        )
        for i in range(1, len(cfg.mdp.em) + 1):
            _check_gro(
                stage_dir / "em{}.gro".format(i), expected_atoms, stage_dir
            )


def _expected_atom_count(conf_gro: Path, cwd: Path) -> int:
    """Atom count of the topology stage's ``conf.gro`` (the reference count)."""
    try:
        return len(read_gro(conf_gro).atoms)
    except (OSError, ValueError) as exc:
        raise _stage_error(
            "cannot read the topology input {}: {}".format(conf_gro, exc),
            hint="Run the topology stage first.",
            cwd=cwd,
        )


def _check_gro(path: Path, expected_atoms: int, cwd: Path) -> None:
    """Validate one minimisation output: present, finite, atom count matches."""
    if not path.is_file() or path.stat().st_size == 0:
        raise _stage_error(
            "em output is missing or empty: {}".format(path),
            hint="Check the em command log.",
            cwd=cwd,
        )

    text = path.read_text(encoding="utf-8", errors="replace")
    if _NONFINITE_RE.search(text):
        raise _stage_error(
            "{} contains non-finite coordinates (nan/inf); energy minimisation "
            "diverged".format(path.name),
            hint="Reduce the initial emstep or inspect the starting structure.",
            cwd=cwd,
        )

    try:
        n_atoms = len(read_gro(path).atoms)
    except (OSError, ValueError) as exc:
        raise _stage_error(
            "cannot read the em output {}: {}".format(path, exc), cwd=cwd
        )
    if n_atoms != expected_atoms:
        raise _stage_error(
            "atom count mismatch: {} has {} atoms but {} has {}".format(
                path.name, n_atoms, CONF_GRO, expected_atoms
            ),
            cwd=cwd,
        )


def _flexible_warnings(cfg: RunConfig, topol_text: str) -> List[str]:
    """Warnings for a ``[ settles ]`` topology minimised without ``-DFLEXIBLE``.

    Rigid water geometries cannot relax without ``-DFLEXIBLE``, so GROMACS
    warns during minimisation.  Surfacing it here does not change the exit
    status.
    """
    if not cfg.mdp.em:
        return []
    if "-DFLEXIBLE" in read_mdp(cfg.path(cfg.mdp.em[0])).get("define", ""):
        return []
    if not _SETTLES_RE.search(topol_text):
        return []
    return [
        "WARNING: {} contains [ settles ] but {} does not define -DFLEXIBLE; "
        "GROMACS will warn that rigid waters cannot be minimised "
        "(-DFLEXIBLE is recommended for energy minimisation).".format(
            TOPOL, cfg.mdp.em[0]
        )
    ]


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
