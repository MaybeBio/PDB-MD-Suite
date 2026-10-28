"""Typer commands for the ``pdb-md md`` end-to-end pipeline.

The heavy lifting lives in :mod:`pdb_md.md.plan` (stage graph, planner,
executor), :mod:`pdb_md.md.state` (persistence and locking), and the individual
stage modules.  This layer only wires them together, prints the plan, and maps
:class:`~pdb_md.md.errors.MdError` instances onto their documented exit codes.
"""

from pathlib import Path
from typing import Dict, List, Optional

import typer

from .config import RunConfig, load_config
from .doctor import run_doctor
from .errors import ConfigError, MdError, PreflightError, StageError
from .templates import TEMPLATE, _DEFAULT_VALUES, render_template, write_config
from .plan import (
    Action,
    RunContext,
    Stage,
    StageFactory,
    build_stages,
    compute_actions,
    execute,
    select_stages,
)
from .runner import Runner
from .state import RunLock, RunState, sha256_file
from .stages.em import EmStage
from .stages.equil import NptStage, NvtStage
from .stages.pbc import PbcStage
from .stages.preprocess import PreprocessStage
from .stages.prod import ProdStage
from .stages.topology import TopologyStage
from .stages.zaff import ZaffStage

md_app = typer.Typer(
    no_args_is_help=True,
    help="End-to-end GROMACS MD pipeline for DNA + zinc-finger complexes.",
)


def stage_factories() -> Dict[str, StageFactory]:
    """Return the registry that :func:`build_stages` uses to construct stages."""

    return {
        "preprocess": lambda cfg, replica: PreprocessStage(cfg),
        "zaff": lambda cfg, replica: ZaffStage(cfg),
        "topology": lambda cfg, replica: TopologyStage(cfg),
        "em": lambda cfg, replica: EmStage(cfg),
        "nvt": lambda cfg, replica: NvtStage(cfg, replica),
        "npt": lambda cfg, replica: NptStage(cfg, replica),
        "prod": lambda cfg, replica: ProdStage(cfg, replica),
        "pbc": lambda cfg, replica: PbcStage(cfg, replica),
    }


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _report_error(exc: MdError) -> None:
    """Print ``exc`` in its most informative form to stderr.

    :class:`StageError` must use ``str()``: its inherited ``render()`` drops the
    command, cwd, exit code, and output tail that make a failed subprocess
    debuggable.  Every other error uses :meth:`MdError.render`.
    """

    if isinstance(exc, StageError):
        typer.echo(str(exc), err=True)
    else:
        typer.echo(exc.render(), err=True)


def _echo_actions(actions: List[Action]) -> None:
    """Print the plan table: one ``RUN|SKIP  <key>  <reason>`` line per action."""

    for action in actions:
        typer.echo(
            "{:<4}  {}  {}".format(action.kind.upper(), action.key, action.reason)
        )


def _tool_version(runner: Runner, argv: List[str]) -> str:
    """Return the first line of ``argv``'s output, or ``"unknown"``.

    Version capture is best-effort: a broken tool must not abort a run whose
    plan is otherwise executable.
    """

    try:
        output = runner.run_capture(argv, check=False)
    except Exception:  # noqa: BLE001 - any failure means "unknown"
        return "unknown"
    for line in output.splitlines():
        line = line.strip()
        if line:
            return line
    return "unknown"


def _tool_versions(cfg: RunConfig, runner: Runner) -> Dict[str, str]:
    """Capture the versions of every external tool used by the pipeline."""

    return {
        "gmx": _tool_version(runner, [cfg.tools.gmx, "--version"]),
        "tleap": _tool_version(runner, [cfg.tools.tleap, "--version"]),
        "parmed_python": _tool_version(
            runner,
            [cfg.tools.parmed_python, "-c", "import parmed; print(parmed.__version__)"],
        ),
    }


def _execute_selection(
    cfg: RunConfig,
    state: RunState,
    stages: List[Stage],
    actions: List[Action],
    force: bool,
) -> None:
    """Run the selected stages, persisting state even when one raises."""

    ctx = RunContext(cfg, cfg.root, state, Runner(cfg.root / "logs"), force)
    try:
        execute(stages, actions, ctx)
    finally:
        # execute() records done/failed but deliberately does not save.
        state.save()


def _confirm_production(assume_yes: bool, stages: List[Stage]) -> None:
    """Require explicit confirmation before production MD starts."""

    if assume_yes:
        return
    if not any(stage.key.startswith("prod:rep") for stage in stages):
        return
    try:
        confirmed = typer.confirm("Production MD will run. Continue?")
    except typer.Abort:
        raise PreflightError(
            "use --yes",
            hint="Pass --yes to skip the production confirmation.",
        )
    if not confirmed:
        raise PreflightError(
            "use --yes",
            hint="Pass --yes to skip the production confirmation.",
        )


# ---------------------------------------------------------------------------
# ``md init``
# ---------------------------------------------------------------------------


def _prompt_values() -> Dict[str, str]:
    """Prompt for the configurable template values, in a fixed order.

    ``cation``/``anion`` are deliberately not asked; they keep their defaults.
    The replicate count drives both ``replicates`` and the generated ``seeds``.
    """

    values: Dict[str, str] = {}
    values["run_name"] = typer.prompt(
        "run name", default=_DEFAULT_VALUES["run_name"]
    )
    values["structure"] = typer.prompt(
        "structure pdb", default=_DEFAULT_VALUES["structure"]
    )
    values["gmx"] = typer.prompt("gmx executable", default=_DEFAULT_VALUES["gmx"])
    values["tleap"] = typer.prompt(
        "tleap executable", default=_DEFAULT_VALUES["tleap"]
    )
    values["parmed_python"] = typer.prompt(
        "parmed python", default=_DEFAULT_VALUES["parmed_python"]
    )
    values["em1_mdp"] = typer.prompt(
        "em1 mdp", default=_DEFAULT_VALUES["em1_mdp"]
    )
    values["em2_mdp"] = typer.prompt(
        "em2 mdp", default=_DEFAULT_VALUES["em2_mdp"]
    )
    values["nvt_mdp"] = typer.prompt(
        "nvt mdp", default=_DEFAULT_VALUES["nvt_mdp"]
    )
    values["npt_mdp"] = typer.prompt(
        "npt mdp", default=_DEFAULT_VALUES["npt_mdp"]
    )
    values["prod_mdp"] = typer.prompt(
        "prod mdp", default=_DEFAULT_VALUES["prod_mdp"]
    )
    while True:
        raw_count = typer.prompt(
            "replicates count", default=_DEFAULT_VALUES["replicates"]
        )
        try:
            count = int(raw_count)
            break
        except ValueError:
            typer.echo("Please enter an integer.", err=True)
    values["replicates"] = str(count)
    values["seeds"] = ", ".join(str(10000 * i + i) for i in range(1, count + 1))
    values["salt_concentration"] = typer.prompt(
        "salt concentration (M)", default=_DEFAULT_VALUES["salt_concentration"]
    )
    return values


@md_app.command("init")
def init_cmd(
    output: Path = typer.Option("run.yaml", "--output", "-o", help="Path to write."),
    template: bool = typer.Option(
        False, "--template", help="Write the template with defaults, no prompts."
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing file."),
):
    """Generate a run.yaml template or walk through an interactive setup."""

    try:
        if template:
            values = dict(_DEFAULT_VALUES)
        else:
            values = dict(_DEFAULT_VALUES)
            values.update(_prompt_values())
        write_config(output, values, force)
        typer.echo("Next: pdb-md md doctor {}".format(output))
    except MdError as exc:
        _report_error(exc)
        raise typer.Exit(exc.exit_code)


# ---------------------------------------------------------------------------
# ``md run``
# ---------------------------------------------------------------------------


def execute_run(
    config_path: Path,
    dry_run: bool,
    assume_yes: bool,
    from_key: Optional[str],
    to_key: Optional[str],
    only: Optional[str],
    replica: Optional[int],
    force: bool,
) -> int:
    """Plan and optionally execute a run; return a process exit code."""

    config_path = Path(config_path)
    cfg = load_config(config_path)

    with RunLock(cfg.root / ".lock"):
        state = RunState.load(cfg.root / "state.json", cfg.run_name)
        state.set_config_hash(sha256_file(config_path))

        stages = build_stages(cfg, stage_factories())
        stages = select_stages(
            stages, from_key=from_key, to_key=to_key, only=only, replica=replica
        )
        # ``--only`` is sugar for ``--from X --to X`` *with* default force.
        actions = compute_actions(
            stages, state, cfg, cfg.root, force=force or only is not None
        )
        _echo_actions(actions)

        if dry_run:
            # A dry run must never invoke an external tool.
            return 0

        runner = Runner(cfg.root / "logs")
        state.set_tool_versions(_tool_versions(cfg, runner))
        state.save()

        _confirm_production(assume_yes, stages)
        _execute_selection(cfg, state, stages, actions, force)
    return 0


@md_app.command("run")
def run_cmd(
    config: Path = typer.Argument(..., help="Path to run.yaml."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print the plan without running anything."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip the production MD confirmation."
    ),
    from_key: Optional[str] = typer.Option(
        None, "--from", help="First stage key to run (inclusive)."
    ),
    to_key: Optional[str] = typer.Option(
        None, "--to", help="Last stage key to run (inclusive)."
    ),
    only: Optional[str] = typer.Option(
        None, "--only", help="Run exactly this stage key."
    ),
    replica: Optional[int] = typer.Option(
        None, "--replica", help="Restrict to one replica number."
    ),
    force: bool = typer.Option(
        False, "--force", help="Re-run stages even when their outputs are current."
    ),
):
    """Plan (and unless --dry-run, execute) the configured MD pipeline."""

    try:
        code = execute_run(
            config, dry_run, yes, from_key, to_key, only, replica, force
        )
    except MdError as exc:
        _report_error(exc)
        raise typer.Exit(exc.exit_code)
    raise typer.Exit(code)


# ---------------------------------------------------------------------------
# ``md status``
# ---------------------------------------------------------------------------


@md_app.command("status")
def status_cmd(
    run_dir: Optional[Path] = typer.Argument(
        None, help="Run directory holding state.json (default: cwd)."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Print state.json verbatim."
    ),
):
    """Show the persisted stage status for a run directory."""

    run_dir = Path(run_dir) if run_dir is not None else Path.cwd()
    path = run_dir / "state.json"
    if not path.exists():
        typer.echo("no state.json in {}".format(run_dir))
        return

    if json_output:
        typer.echo(path.read_text(encoding="utf-8"))
        return

    state = RunState.load(path, run_dir.name)
    typer.echo("run: {}".format(state.run_name))
    for key, record in state.stages.items():
        typer.echo(
            "{:<14}  {:<8}  {}".format(key, record.status, record.started_at or "")
        )


# ---------------------------------------------------------------------------
# ``md stage``
# ---------------------------------------------------------------------------


@md_app.command("stage")
def stage_cmd(
    stage: str = typer.Argument(..., help="Stage key, e.g. nvt:rep1."),
    run_dir: Path = typer.Argument(..., help="Run directory containing run.yaml."),
    force: bool = typer.Option(
        False, "--force", help="Re-run the stage even when it is current."
    ),
):
    """Run one stage (plus whatever prerequisites are recorded done)."""

    try:
        cfg = load_config(run_dir / "run.yaml")
        with RunLock(cfg.root / ".lock"):
            state = RunState.load(cfg.root / "state.json", cfg.run_name)
            stages = select_stages(
                build_stages(cfg, stage_factories()), only=stage
            )
            actions = compute_actions(stages, state, cfg, cfg.root, force=True)
            _echo_actions(actions)
            _execute_selection(cfg, state, stages, actions, True)
    except MdError as exc:
        _report_error(exc)
        raise typer.Exit(exc.exit_code)


# ---------------------------------------------------------------------------
# ``md pbc``
# ---------------------------------------------------------------------------


@md_app.command("pbc")
def pbc_cmd(
    run_dir: Path = typer.Argument(..., help="Run directory containing run.yaml."),
    replica: str = typer.Option(
        "all", "--replica", help="'all' or a replica number."
    ),
    force: bool = typer.Option(
        False, "--force", help="Re-run even when the outputs are current."
    ),
):
    """Run the PBC-correction stage(s) for a completed production run."""

    try:
        cfg = load_config(run_dir / "run.yaml")
        with RunLock(cfg.root / ".lock"):
            state = RunState.load(cfg.root / "state.json", cfg.run_name)
            stages = [
                stage
                for stage in build_stages(cfg, stage_factories())
                if stage.key.split(":")[0] == "pbc"
            ]
            if replica != "all":
                suffix = ":rep{}".format(replica)
                stages = [stage for stage in stages if stage.key.endswith(suffix)]
            actions = compute_actions(stages, state, cfg, cfg.root, force=force)
            _echo_actions(actions)
            _execute_selection(cfg, state, stages, actions, force)
    except MdError as exc:
        _report_error(exc)
        raise typer.Exit(exc.exit_code)


# ---------------------------------------------------------------------------
# ``md doctor``
# ---------------------------------------------------------------------------


@md_app.command("doctor")
def doctor_cmd(
    config: Path = typer.Argument(..., help="Path to run.yaml."),
):
    """Check that every external prerequisite for this run is available."""

    try:
        cfg = load_config(config)
        runner = Runner(cfg.root / "logs")
        checks = run_doctor(cfg, runner)
    except MdError as exc:
        _report_error(exc)
        raise typer.Exit(exc.exit_code)

    for check in checks:
        typer.echo(
            "{:<4}  {}: {}".format(
                "OK" if check.ok else "FAIL", check.name, check.detail
            )
        )
