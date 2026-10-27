"""Stage protocol, dependency graph, and execution planner.

Every pipeline step implements :class:`Stage`.  :func:`stage_plan` is the
single source of truth for stage ordering and dependencies; :func:`build_stages`
turns a registry of factories into concrete stage objects; and
:func:`compute_actions` decides, per stage, whether it must run or may be
skipped.  :func:`execute` then runs the selected stages with preflight checks
and persisted state transitions.

Stage modules never import one another: :func:`build_stages` receives a
``factories`` mapping (base stage name -> factory) so the CLI can wire them up.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Protocol, Tuple

from .config import RunConfig
from .errors import ConfigError, PreflightError
from .runner import Runner
from .state import RunState


class Stage(Protocol):
    """Structural interface every pipeline stage implements."""

    key: str
    deps: Tuple[str, ...]

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        """Hash of every input this stage consumes.

        Implementations must read upstream artifacts through
        :func:`pdb_md.md.state.hash_or_missing` so that a first ``--dry-run``
        can plan before those artifacts exist.
        """
        ...

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        """Paths this stage produces."""
        ...

    def run(self, ctx: "RunContext") -> None:
        """Perform the stage's work using ``ctx.runner`` for external tools."""
        ...

    def verify(self, cfg: RunConfig, root: Path) -> None:
        """Check that the stage's outputs are valid; raise on failure."""
        ...


@dataclass
class RunContext:
    """Everything a running stage needs beyond its own configuration."""

    cfg: RunConfig
    root: Path
    state: RunState
    runner: Runner
    force: bool


@dataclass(frozen=True)
class Action:
    """The planner's verdict for one stage.

    ``kind`` is ``"run"`` or ``"skip"``; ``reason`` is one of ``new``,
    ``done``, ``hash-changed``, ``missing-artifact``, ``failed``,
    ``upstream-rerun``, or ``forced``.
    """

    key: str
    kind: str
    reason: str


# Replica stages receive their replica number; shared stages receive ``None``.
StageFactory = Callable[[RunConfig, Optional[int]], Stage]


def _replica_key(name: str, replica: int) -> str:
    return "{}:rep{}".format(name, replica)


def stage_plan(cfg: RunConfig) -> List[Tuple[str, Tuple[str, ...]]]:
    """Return the ordered ``(key, deps)`` plan for ``cfg``.

    Ordering is ``preprocess, zaff, topology, em`` followed by
    ``nvt/npt/prod/pbc`` for each replica in ``1..count``.  The ``pbc`` stage is
    omitted entirely when ``cfg.pbc.enabled`` is false.
    """

    plan: List[Tuple[str, Tuple[str, ...]]] = [
        ("preprocess", ()),
        ("zaff", ("preprocess",)),
        ("topology", ("zaff",)),
        ("em", ("topology",)),
    ]
    for n in range(1, cfg.replicates.count + 1):
        plan.append((_replica_key("nvt", n), ("em",)))
        plan.append((_replica_key("npt", n), (_replica_key("nvt", n),)))
        plan.append((_replica_key("prod", n), (_replica_key("npt", n),)))
        if cfg.pbc.enabled:
            plan.append((_replica_key("pbc", n), (_replica_key("prod", n),)))
    return plan


def _split_key(key: str) -> Tuple[str, Optional[int]]:
    """Split ``nvt:rep2`` into ``("nvt", 2)``; shared keys map to ``None``."""

    if ":rep" in key:
        base, _, replica = key.partition(":rep")
        return base, int(replica)
    return key, None


def build_stages(
    cfg: RunConfig, factories: Dict[str, StageFactory]
) -> List[Stage]:
    """Instantiate every stage in :func:`stage_plan` order.

    Factories are keyed by base name (``"nvt"``); replica stages are called as
    ``factory(cfg, n)`` and shared stages as ``factory(cfg, None)``.
    """

    stages: List[Stage] = []
    for key, _deps in stage_plan(cfg):
        base, replica = _split_key(key)
        try:
            factory = factories[base]
        except KeyError:
            raise ConfigError(
                "no stage factory registered for {!r}".format(base),
                hint="Known factories: {}.".format(
                    ", ".join(sorted(factories)) or "<none>"
                ),
            )
        stage = factory(cfg, replica)
        if stage.key != key:
            raise ConfigError(
                "factory for {!r} produced stage key {!r}, expected {!r}".format(
                    base, stage.key, key
                )
            )
        stages.append(stage)
    return stages


def select_stages(
    stages: List[Stage],
    from_key: Optional[str] = None,
    to_key: Optional[str] = None,
    only: Optional[str] = None,
    replica: Optional[int] = None,
) -> List[Stage]:
    """Return an ordered slice of ``stages``.

    ``from_key`` / ``to_key`` are inclusive and must exist.  ``only`` selects a
    single stage and takes precedence over ``from_key`` / ``to_key``.  When
    ``replica`` is given, only shared stages (in range) and stages belonging to
    that replica are kept.
    """

    keys = [stage.key for stage in stages]

    if only is not None:
        if only not in keys:
            raise ConfigError(
                "unknown stage {!r}".format(only),
                hint="Known stages: {}.".format(", ".join(keys) or "<none>"),
            )
        selected = [stages[keys.index(only)]]
    else:
        start = 0
        end = len(stages) - 1
        if from_key is not None:
            if from_key not in keys:
                raise ConfigError(
                    "unknown --from stage {!r}".format(from_key),
                    hint="Known stages: {}.".format(", ".join(keys) or "<none>"),
                )
            start = keys.index(from_key)
        if to_key is not None:
            if to_key not in keys:
                raise ConfigError(
                    "unknown --to stage {!r}".format(to_key),
                    hint="Known stages: {}.".format(", ".join(keys) or "<none>"),
                )
            end = keys.index(to_key)
        selected = list(stages[start : end + 1]) if start <= end else []

    if replica is not None:
        suffix = ":rep{}".format(replica)
        selected = [
            stage
            for stage in selected
            if ":rep" not in stage.key or stage.key.endswith(suffix)
        ]
    return selected


def _own_action(
    stage: Stage, state: RunState, cfg: RunConfig, root: Path, force: bool
) -> Action:
    """Decide run/skip for ``stage`` ignoring its dependencies."""

    if force:
        return Action(stage.key, "run", "forced")

    artifacts = stage.artifacts(cfg, root)
    input_hash = stage.input_hash(cfg, root)
    if state.is_done(stage.key, input_hash, artifacts):
        return Action(stage.key, "skip", "done")

    record = state.get(stage.key)
    if record is None or record.status in ("pending", "running"):
        reason = "new"
    elif record.status == "failed":
        reason = "failed"
    elif record.input_hash != input_hash:
        reason = "hash-changed"
    else:
        reason = "missing-artifact"
    return Action(stage.key, "run", reason)


def compute_actions(
    stages: List[Stage],
    state: RunState,
    cfg: RunConfig,
    root: Path,
    force: bool = False,
) -> List[Action]:
    """Return one :class:`Action` per stage, in the same order.

    A stage is skipped only when it is done (status, unchanged input hash, all
    artifacts present) *and* every dependency in this list is also skipped.
    If any dependency runs, this stage runs too with reason ``upstream-rerun``.
    ``force`` makes every stage run with reason ``forced``.
    """

    actions: List[Action] = []
    by_key: Dict[str, Action] = {}
    for stage in stages:
        action = _own_action(stage, state, cfg, root, force)
        if action.kind == "skip":
            for dep in stage.deps:
                dep_action = by_key.get(dep)
                if dep_action is not None and dep_action.kind == "run":
                    action = Action(stage.key, "run", "upstream-rerun")
                    break
        actions.append(action)
        by_key[stage.key] = action
    return actions


def _dep_settled(state: RunState, dep: str) -> bool:
    """True when ``dep`` is recorded done and its artifacts still exist.

    The dependency's own stage object is not available here, so its recorded
    input hash and artifact list are used to drive the normal ``is_done``
    check.
    """

    record = state.get(dep)
    if record is None or record.status != "done":
        return False
    return state.is_done(
        dep, record.input_hash, [Path(item) for item in record.artifacts]
    )


def execute(stages: List[Stage], actions: List[Action], ctx: RunContext) -> None:
    """Run every stage whose action is ``run``.

    Before anything runs, each selected stage's dependencies must either appear
    earlier in ``stages`` (so they run or are skipped beforehand) or be settled
    in ``ctx.state``; otherwise :class:`PreflightError` is raised.  Each run is
    recorded as started, then after ``run`` + ``verify`` as done; any exception
    marks the stage failed and is re-raised unchanged.
    """

    by_key = {action.key: action for action in actions}
    positions = {stage.key: index for index, stage in enumerate(stages)}

    for index, stage in enumerate(stages):
        for dep in stage.deps:
            dep_index = positions.get(dep)
            if dep_index is not None and dep_index < index:
                continue
            if _dep_settled(ctx.state, dep):
                continue
            raise PreflightError(
                "stage {!r} depends on {!r}, which is neither selected before "
                "it nor recorded done".format(stage.key, dep),
                hint="Include {!r} in the selection or run it first.".format(dep),
            )

    for stage in stages:
        action = by_key.get(stage.key)
        if action is None or action.kind != "run":
            continue
        input_hash = stage.input_hash(ctx.cfg, ctx.root)
        ctx.state.record_start(stage.key, input_hash, None)
        try:
            stage.run(ctx)
            stage.verify(ctx.cfg, ctx.root)
            ctx.state.record_done(
                stage.key,
                stage.artifacts(ctx.cfg, ctx.root),
                ctx.root,
            )
        except Exception as exc:
            ctx.state.record_failed(stage.key, str(exc))
            raise
