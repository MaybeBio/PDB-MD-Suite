"""The ``prod`` stage: production molecular dynamics per replica.

:class:`ProdStage` continues replica ``n``'s NPT equilibration into production
MD.  Each replica owns ``06_prod/repN`` and an output prefix
``<run_name>_md_rN``.  The NPT checkpoint is required: production continues from
``npt.cpt`` (via ``grompp -t``) and must never silently restart from scratch,
so a missing or empty ``npt.gro`` / ``npt.cpt`` fails the stage before
``grompp`` runs.

An interrupted production run is resumed at the ``mdrun`` level: when
``<prefix>.cpt`` already exists and the run is not forced, ``mdrun`` is given
``-cpi`` with that checkpoint.  Paths handed to ``gmx`` are absolute and the run
root is the working directory, matching the other stages.  ``verify`` requires
every output to exist and be non-empty; it deliberately does not parse the
``.xtc`` magic -- a non-empty ``.edr`` / ``.log`` is the frame check.
"""

from pathlib import Path
from typing import List, Optional, Sequence

from ..config import RunConfig
from ..errors import StageError
from ..plan import RunContext
from ..state import hash_or_missing, sha256_parts

PROD_DIR = "06_prod"
NPT_DIR = "05_npt"
TOPOLOGY_DIR = "02_topology"
TOPOL = "topol.top"
REPLICA_PREFIX = "rep"
#: Extensions every production run must leave behind, in reporting order.
OUTPUT_EXTS = ("tpr", "xtc", "edr", "log", "cpt")


class ProdStage:
    """Production MD of one replica, continuing that replica's NPT run."""

    def __init__(self, cfg: RunConfig, replica: int):
        self.cfg = cfg
        self.replica = replica
        self.key = "prod:rep{}".format(replica)
        self.deps = ("npt:rep{}".format(replica),)

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        root = Path(root)
        npt_dir = _stage_dir(root, NPT_DIR, self.replica)
        return sha256_parts(
            [
                # Produced by ``npt:repN`` / ``topology``, so these may be
                # absent on a first ``--dry-run``.
                hash_or_missing(npt_dir / "npt.gro", root),
                hash_or_missing(npt_dir / "npt.cpt", root),
                hash_or_missing(root / TOPOLOGY_DIR / TOPOL, root),
                hash_or_missing(cfg.path(cfg.mdp.prod), root),
                list(cfg.mdrun.args),
                cfg.stage_maxwarn("prod"),
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = _stage_dir(root, PROD_DIR, self.replica)
        prefix = _prefix(cfg, self.replica)
        return [
            stage_dir / "{}.{}".format(prefix, ext) for ext in OUTPUT_EXTS
        ]

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        n = self.replica
        prefix = _prefix(cfg, n)
        stage_dir = _stage_dir(root, PROD_DIR, n)
        npt_dir = _stage_dir(root, NPT_DIR, n)
        npt_gro = npt_dir / "npt.gro"
        npt_cpt = npt_dir / "npt.cpt"

        # Production continues from NPT: both the structure and checkpoint are
        # mandatory.  Fail rather than silently starting production from
        # scratch with no equilibration.
        for path in (npt_gro, npt_cpt):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "production MD input is missing or empty: {}".format(path),
                    hint="Run the npt:rep{} stage first.".format(n),
                    cwd=ctx.root,
                )

        stage_dir.mkdir(parents=True, exist_ok=True)
        tpr = stage_dir / "{}.tpr".format(prefix)

        ctx.runner.run(
            [
                cfg.tools.gmx,
                "grompp",
                "-f",
                str(cfg.path(cfg.mdp.prod)),
                "-c",
                str(npt_gro),
                "-t",
                str(npt_cpt),
                "-p",
                str(root / TOPOLOGY_DIR / TOPOL),
                "-o",
                str(tpr),
                "-maxwarn",
                str(cfg.stage_maxwarn("prod")),
            ],
            log_name="prod",
            cwd=ctx.root,
        )

        cpt = stage_dir / "{}.cpt".format(prefix)
        mdrun_argv = [cfg.tools.gmx, "mdrun", "-deffnm", str(stage_dir / prefix)]
        if cpt.exists() and not ctx.force:
            # Resume an interrupted production run unless a restart is forced.
            mdrun_argv.extend(["-cpi", str(cpt)])
        mdrun_argv.extend(cfg.mdrun.args)
        ctx.runner.run(mdrun_argv, log_name="prod", cwd=ctx.root)

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = _stage_dir(root, PROD_DIR, self.replica)
        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "prod artifact is missing or empty: {}".format(path),
                    cwd=stage_dir,
                )


def _prefix(cfg: RunConfig, replica: int) -> str:
    """The ``-deffnm`` prefix shared by every output of replica ``replica``."""
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
