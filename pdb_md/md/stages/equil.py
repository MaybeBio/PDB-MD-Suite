"""The replica ``nvt`` / ``npt`` equilibration stages.

Both stages are per-replica: :class:`NvtStage` runs replica ``n``'s NVT
equilibration from the last energy-minimised structure, and :class:`NptStage`
continues that NVT run under a barostat.  Each replica gets its own directory
(``04_nvt/repN`` / ``05_npt/repN``) and its own seeded ``.mdp`` copy: NVT must
regenerate velocities with the replica's ``replicates.seeds`` entry, but the
user's source ``.mdp`` is never modified -- :func:`write_seeded_mdp` writes a
new ``nvt_rN.mdp`` next to the run.

Paths handed to ``gmx`` are absolute and the run root is the working directory,
matching the ``em`` stage, so outputs land in stable locations regardless of the
caller's cwd.  ``verify`` re-reads the artifacts and re-runs the same semantic
checks through ``StageError`` (never ``ConfigError``), so a hand-edited stage is
rejected rather than silently trusted.
"""

import re
from pathlib import Path
from typing import List, Optional, Sequence

from ..config import RunConfig
from ..errors import StageError
from ..mdp import check_mdp, read_mdp, replace_key
from ..plan import RunContext
from ..state import hash_or_missing, sha256_parts

EM_DIR = "03_em"
TOPOLOGY_DIR = "02_topology"
TOPOL = "topol.top"
NVT_DIR = "04_nvt"
NPT_DIR = "05_npt"
REPLICA_PREFIX = "rep"

#: ``#ifdef POSRES`` directives, tolerating interior whitespace and case.
_POSRES_IFDEF_RE = re.compile(r"^\s*#\s*ifdef\s+POSRES\b", re.MULTILINE | re.IGNORECASE)
#: ``#include "posre_*.itp"`` directives; group 1 is the include path.
_POSRE_INCLUDE_RE = re.compile(
    r'^\s*#include\s+"([^"]*posre_[^"]*\.itp)"', re.MULTILINE | re.IGNORECASE
)


def last_em_gro(cfg: RunConfig, root: Path) -> Path:
    """The last chained energy-minimisation structure, ``03_em/emN.gro``."""
    return Path(root) / EM_DIR / "em{}.gro".format(len(cfg.mdp.em))


def write_seeded_mdp(src: Path, dst: Path, seed: int) -> None:
    """Copy ``src`` to ``dst`` with ``gen_seed`` replaced by ``seed``.

    The source ``.mdp`` is never modified.  Raises
    :class:`~pdb_md.md.errors.ConfigError` (via :func:`replace_key`) when
    ``gen_seed`` is missing or ambiguous.
    """
    dst = Path(dst)
    text = Path(src).read_text(encoding="utf-8")
    new_text = replace_key(text, "gen_seed", str(seed))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new_text, encoding="utf-8")


class NvtStage:
    """NVT equilibration of one replica, starting from the ``em`` chain's end."""

    def __init__(self, cfg: RunConfig, replica: int):
        self.cfg = cfg
        self.replica = replica
        self.key = "nvt:rep{}".format(replica)
        self.deps = ("em",)

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        root = Path(root)
        topology_dir = root / TOPOLOGY_DIR
        posre = [
            hash_or_missing(path, root)
            for path in sorted(topology_dir.glob("posre_*.itp"))
        ]
        return sha256_parts(
            [
                # Produced by ``topology``/``em``, so these may be absent on a
                # first ``--dry-run``.
                hash_or_missing(topology_dir / TOPOL, root),
                hash_or_missing(last_em_gro(cfg, root), root),
                *posre,
                hash_or_missing(cfg.path(cfg.mdp.nvt), root),
                cfg.replicates.seeds[self.replica - 1],
                cfg.stage_maxwarn("nvt"),
                list(cfg.mdrun.args),
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = _stage_dir(root, NVT_DIR, self.replica)
        seeded_mdp = stage_dir / "nvt_r{}.mdp".format(self.replica)
        return [
            seeded_mdp,
            stage_dir / "nvt.tpr",
            stage_dir / "nvt.gro",
            stage_dir / "nvt.edr",
            stage_dir / "nvt.log",
            stage_dir / "nvt.cpt",
        ]

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        n = self.replica
        stage_dir = _stage_dir(root, NVT_DIR, n)
        stage_dir.mkdir(parents=True, exist_ok=True)

        seed = cfg.replicates.seeds[n - 1]
        seeded = stage_dir / "nvt_r{}.mdp".format(n)
        write_seeded_mdp(cfg.path(cfg.mdp.nvt), seeded, seed)
        # The copy must remain a valid NVT mdp after the seed substitution.
        check_mdp(seeded, "nvt")

        ctx.runner.run(
            [
                cfg.tools.gmx,
                "grompp",
                "-f",
                str(seeded),
                "-c",
                str(last_em_gro(cfg, root)),
                "-r",
                str(last_em_gro(cfg, root)),
                "-p",
                str(root / TOPOLOGY_DIR / TOPOL),
                "-o",
                str(stage_dir / "nvt.tpr"),
                "-maxwarn",
                str(cfg.stage_maxwarn("nvt")),
            ],
            log_name="nvt",
            cwd=ctx.root,
        )

        mdrun_argv = [cfg.tools.gmx, "mdrun", "-deffnm", str(stage_dir / "nvt")]
        mdrun_argv.extend(cfg.mdrun.args)
        ctx.runner.run(mdrun_argv, log_name="nvt", cwd=ctx.root)

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = _stage_dir(root, NVT_DIR, self.replica)
        _check_nonempty(self.artifacts(cfg, root), stage_dir, "nvt")

        seeded = stage_dir / "nvt_r{}.mdp".format(self.replica)
        parsed = _read_mdp(seeded, stage_dir)
        if parsed.get("gen_vel", "").lower() != "yes":
            raise _stage_error(
                "{}: 'gen_vel' must be 'yes' for an NVT stage".format(
                    seeded.name
                ),
                cwd=stage_dir,
            )
        if "-DPOSRES" not in parsed.get("define", ""):
            raise _stage_error(
                "{}: 'define' must contain '-DPOSRES'".format(seeded.name),
                cwd=stage_dir,
            )

        _check_posres(root)


class NptStage:
    """NPT equilibration of one replica, continuing that replica's NVT run."""

    def __init__(self, cfg: RunConfig, replica: int):
        self.cfg = cfg
        self.replica = replica
        self.key = "npt:rep{}".format(replica)
        self.deps = ("nvt:rep{}".format(replica),)

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        root = Path(root)
        topology_dir = root / TOPOLOGY_DIR
        nvt_dir = _stage_dir(root, NVT_DIR, self.replica)
        posre = [
            hash_or_missing(path, root)
            for path in sorted(topology_dir.glob("posre_*.itp"))
        ]
        return sha256_parts(
            [
                # Produced by ``topology``/``nvt:repN``, so these may be absent
                # on a first ``--dry-run``.
                hash_or_missing(topology_dir / TOPOL, root),
                hash_or_missing(nvt_dir / "nvt.gro", root),
                hash_or_missing(nvt_dir / "nvt.cpt", root),
                *posre,
                hash_or_missing(cfg.path(cfg.mdp.npt), root),
                cfg.stage_maxwarn("npt"),
                list(cfg.mdrun.args),
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        stage_dir = _stage_dir(root, NPT_DIR, self.replica)
        return [
            stage_dir / "npt.tpr",
            stage_dir / "npt.gro",
            stage_dir / "npt.edr",
            stage_dir / "npt.log",
            stage_dir / "npt.cpt",
        ]

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        n = self.replica
        stage_dir = _stage_dir(root, NPT_DIR, n)
        stage_dir.mkdir(parents=True, exist_ok=True)

        npt_mdp = cfg.path(cfg.mdp.npt)
        # Continuation and position restraints are what make NPT the second
        # half of equilibration; fail the stage (not the config) when absent.
        parsed = _read_mdp(npt_mdp, stage_dir)
        if parsed.get("continuation", "").lower() != "yes":
            raise _stage_error(
                "{}: 'continuation' must be 'yes' for an NPT stage".format(
                    npt_mdp.name
                ),
                hint="NPT must continue from the NVT run (continuation = yes).",
                cwd=stage_dir,
            )
        if "-DPOSRES" not in parsed.get("define", ""):
            raise _stage_error(
                "{}: 'define' must contain '-DPOSRES'".format(npt_mdp.name),
                cwd=stage_dir,
            )

        nvt_dir = _stage_dir(root, NVT_DIR, n)
        ctx.runner.run(
            [
                cfg.tools.gmx,
                "grompp",
                "-f",
                str(npt_mdp),
                "-c",
                str(nvt_dir / "nvt.gro"),
                "-r",
                str(nvt_dir / "nvt.gro"),
                "-t",
                str(nvt_dir / "nvt.cpt"),
                "-p",
                str(root / TOPOLOGY_DIR / TOPOL),
                "-o",
                str(stage_dir / "npt.tpr"),
                "-maxwarn",
                str(cfg.stage_maxwarn("npt")),
            ],
            log_name="npt",
            cwd=ctx.root,
        )

        mdrun_argv = [cfg.tools.gmx, "mdrun", "-deffnm", str(stage_dir / "npt")]
        mdrun_argv.extend(cfg.mdrun.args)
        ctx.runner.run(mdrun_argv, log_name="npt", cwd=ctx.root)

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        stage_dir = _stage_dir(root, NPT_DIR, self.replica)
        _check_nonempty(self.artifacts(cfg, root), stage_dir, "npt")

        npt_mdp = cfg.path(cfg.mdp.npt)
        parsed = _read_mdp(npt_mdp, stage_dir)
        if parsed.get("continuation", "").lower() != "yes":
            raise _stage_error(
                "{}: 'continuation' must be 'yes' for an NPT stage".format(
                    npt_mdp.name
                ),
                cwd=stage_dir,
            )
        if "-DPOSRES" not in parsed.get("define", ""):
            raise _stage_error(
                "{}: 'define' must contain '-DPOSRES'".format(npt_mdp.name),
                cwd=stage_dir,
            )

        _check_posres(root)


def _stage_dir(root: Path, base: str, replica: int) -> Path:
    return Path(root) / base / "{}{}".format(REPLICA_PREFIX, replica)


def _read_mdp(path: Path, cwd: Path) -> dict:
    """Read an mdp, converting an I/O failure into a :class:`StageError`."""
    try:
        return read_mdp(path)
    except OSError as exc:
        raise _stage_error(
            "cannot read the mdp file {}: {}".format(path, exc), cwd=cwd
        )


def _check_nonempty(
    artifacts: Sequence[Path], stage_dir: Path, stage: str
) -> None:
    """Every artifact must exist and be non-empty."""
    for path in artifacts:
        if not path.is_file() or path.stat().st_size == 0:
            raise _stage_error(
                "{} artifact is missing or empty: {}".format(stage, path),
                cwd=stage_dir,
            )


def _check_posres(root: Path) -> None:
    """The topology must define ``POSRES`` and reference every posre itp.

    Shared by both equilibration stages: position restraints are applied by
    ``-DPOSRES`` and their parameters live in ``posre_*.itp`` files that
    ``topol.top`` must ``#include``.
    """
    topology_dir = Path(root) / TOPOLOGY_DIR
    topol = topology_dir / TOPOL
    try:
        text = topol.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise _stage_error(
            "cannot read the topology {}: {}".format(topol, exc),
            hint="Run the topology stage first.",
            cwd=topology_dir,
        )

    if not _POSRES_IFDEF_RE.search(text):
        raise _stage_error(
            "{} contains no '#ifdef POSRES' block; position restraints are "
            "not enabled".format(TOPOL),
            cwd=topology_dir,
        )

    for include in _POSRE_INCLUDE_RE.findall(text):
        itp = topology_dir / include
        if not itp.is_file() or itp.stat().st_size == 0:
            raise _stage_error(
                "{} includes {!r} but it is missing or empty: {}".format(
                    TOPOL, include, itp
                ),
                cwd=topology_dir,
            )


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
