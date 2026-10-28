"""Environment preflight checks for ``pdb-md md doctor``.

Every check is returned as a :class:`Check` so the CLI can print an OK/FAIL
line per prerequisite.  When any check fails :func:`run_doctor` raises a single
:class:`~pdb_md.md.errors.PreflightError` (exit code 3) aggregating all of the
failed checks, rather than stopping at the first problem.

External tools are only ever reached through :class:`~pdb_md.md.runner.Runner`;
this module never imports gromacs, tleap, or parmed itself, so a missing tool
is reported as a failed check instead of an ``ImportError``.
"""

import shutil
from dataclasses import dataclass
from typing import List

from .config import RunConfig
from .coords import read_pdb
from .errors import ConfigError, PreflightError
from .runner import Runner
from .zinc import preflight_structure, validate_sites

#: Minimum free space the run directory must offer, in bytes (1 GiB).
MIN_FREE_BYTES = 1024 ** 3


@dataclass(frozen=True)
class Check:
    """Outcome of one preflight probe."""

    name: str
    ok: bool
    detail: str


def _first_line(text: str) -> str:
    """Return the first non-blank line of ``text``, stripped."""

    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _tool_failure(name: str, argv: List[str], exc: BaseException) -> Check:
    return Check(
        name,
        False,
        "cannot run {!r}: {}".format(argv[0], exc),
    )


def _check_gmx(cfg: RunConfig, runner: Runner) -> Check:
    argv = [cfg.tools.gmx, "--version"]
    try:
        output = runner.run_capture(argv, check=False)
    except OSError as exc:
        return _tool_failure("gmx", argv, exc)
    detail = _first_line(output) or "no version output"
    return Check("gmx", True, detail)


def _check_tleap(cfg: RunConfig, runner: Runner) -> Check:
    argv = [cfg.tools.tleap, "-h"]
    try:
        output = runner.run_capture(argv, check=False)
    except OSError as exc:
        return _tool_failure("tleap", argv, exc)
    ok = "tleap" in output or "AmberTools" in output
    detail = _first_line(output) or "no output"
    if not ok:
        detail = "output does not mention tleap/AmberTools"
    return Check("tleap", ok, detail)


def _check_parmed(cfg: RunConfig, runner: Runner) -> Check:
    argv = [
        cfg.tools.parmed_python,
        "-c",
        "import parmed; print(parmed.__version__)",
    ]
    try:
        output = runner.run_capture(argv, check=False)
    except OSError as exc:
        return _tool_failure("parmed", argv, exc)
    version = _first_line(output)
    if not version:
        return Check("parmed", False, "parmed is not importable in {}".format(argv[0]))
    return Check("parmed", True, version)


def _check_mdp(cfg: RunConfig) -> Check:
    # load_config already parsed and validated every mdp file; report the count.
    count = len(cfg.mdp.em) + 3  # em files + nvt + npt + prod
    return Check("mdp", True, "{} mdp file(s) validated".format(count))


def _check_structure(cfg: RunConfig) -> Check:
    path = cfg.path(cfg.input.structure)
    try:
        table = read_pdb(path)
        preflight_structure(table)
        validate_sites(table, list(cfg.zinc_sites), cfg.coordination_check)
    except (PreflightError, ConfigError, OSError, ValueError) as exc:
        message = getattr(exc, "message", None) or str(exc)
        return Check("structure", False, message)
    return Check(
        "structure",
        True,
        "{} atoms, {} residues".format(len(table.atoms), len(table.residues)),
    )


def _check_disk(cfg: RunConfig) -> Check:
    try:
        free = shutil.disk_usage(cfg.root).free
    except OSError as exc:
        return Check("disk", False, "cannot stat {}: {}".format(cfg.root, exc))
    ok = free >= MIN_FREE_BYTES
    detail = "{:.1f} GiB free (need 1 GiB)".format(free / float(MIN_FREE_BYTES))
    return Check("disk", ok, detail)


def _check_gpu(cfg: RunConfig, runner: Runner) -> Check:
    if "gpu" not in cfg.mdrun.args:
        return Check("gpu", True, "cpu-only")
    path = runner.which("nvidia-smi")
    if path:
        return Check("gpu", True, path)
    return Check(
        "gpu",
        False,
        "mdrun.args requests gpu but nvidia-smi was not found on PATH",
    )


def run_doctor(cfg: RunConfig, runner: Runner) -> List[Check]:
    """Probe the environment and return one :class:`Check` per prerequisite.

    Raises :class:`PreflightError` (exit code 3) when any check fails, listing
    every failure so the user can fix them in one pass.
    """

    checks = [
        _check_gmx(cfg, runner),
        _check_tleap(cfg, runner),
        _check_parmed(cfg, runner),
        _check_mdp(cfg),
        _check_structure(cfg),
        _check_disk(cfg),
        _check_gpu(cfg, runner),
    ]
    failed = [check for check in checks if not check.ok]
    if failed:
        lines = [
            "  - {}: {}".format(check.name, check.detail) for check in failed
        ]
        raise PreflightError(
            "preflight checks failed:\n" + "\n".join(lines),
            hint="Fix the failed checks above before running the pipeline.",
        )
    return checks
