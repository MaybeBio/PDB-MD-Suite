"""End-to-end pipeline test against fake ``gmx``/``tleap``/ParmEd binaries.

The real stage graph, planner, state persistence, skip logic, failure
propagation, dry-run and ``md stage --force`` are all exercised; only the
external executables are stubbed (see ``tests/md/fixtures.py``).
"""

import json
import os
from pathlib import Path

STAGE_TOOLS = ("grompp", "mdrun", "trjconv", "check", "distance", "tleap")


def _calls_path() -> Path:
    return Path(os.environ["E2E_CALLS"])


def stage_calls():
    """Lines the fake tools appended for real stage actions only."""
    return [
        line
        for line in _calls_path().read_text(encoding="utf-8").splitlines()
        if line.startswith(STAGE_TOOLS)
    ]


def _plan(output):
    """Map each stage key in a dry-run/plan printout to ``RUN`` or ``SKIP``."""
    plan = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("RUN", "SKIP"):
            plan[parts[1]] = parts[0]
    return plan


def test_full_pipeline_then_all_skip(tmp_path, e2e_run):
    run_dir, invoke = e2e_run(n_replicas=1, fail_stage=None)
    result = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert result.exit_code == 0, result.output

    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    for key in (
        "preprocess",
        "zaff",
        "topology",
        "em",
        "nvt:rep1",
        "npt:rep1",
        "prod:rep1",
        "pbc:rep1",
    ):
        assert state["stages"][key]["status"] == "done", key

    assert (
        run_dir / "07_pbc" / "rep1" / "testrun_md_r1_5center.xtc"
    ).is_file()

    calls_before = len(stage_calls())
    second = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert second.exit_code == 0, second.output
    assert "SKIP" in second.output
    # A skip-only second run must not invoke any stage action (version probes
    # are allowed, and the fakes deliberately do not log them).
    assert len(stage_calls()) == calls_before


def test_failure_stops_downstream(tmp_path, e2e_run):
    run_dir, invoke = e2e_run(n_replicas=1, fail_stage="mdrun")
    result = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert result.exit_code == 1

    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    assert state["stages"]["prod:rep1"]["status"] == "failed"
    assert "pbc:rep1" not in state["stages"]


def test_dry_run_after_input_change(tmp_path, e2e_run):
    run_dir, invoke = e2e_run(n_replicas=1)
    first = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert first.exit_code == 0, first.output

    # ``preprocess.input_hash`` hashes the *source* structure, so touching it
    # must make preprocess (and therefore every downstream stage) RUN.
    source = run_dir / "inputs" / "complex.pdb"
    source.write_text(
        source.read_text(encoding="utf-8") + "REMARK changed\n",
        encoding="utf-8",
    )

    calls_before = len(stage_calls())
    result = invoke(["md", "run", str(run_dir / "run.yaml"), "--dry-run", "--yes"])
    assert result.exit_code == 0, result.output

    plan = _plan(result.output)
    assert plan["preprocess"] == "RUN"
    for key in (
        "zaff",
        "topology",
        "em",
        "nvt:rep1",
        "npt:rep1",
        "prod:rep1",
        "pbc:rep1",
    ):
        assert plan[key] == "RUN", key

    # Dry run never invokes a tool and never mutates state.json.
    assert len(stage_calls()) == calls_before
    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    assert state["stages"]["preprocess"]["status"] == "done"
    assert state["stages"]["prod:rep1"]["status"] == "done"


def test_failure_output_and_state(tmp_path, e2e_run):
    run_dir, invoke = e2e_run(n_replicas=1, fail_stage="mdrun")
    result = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert result.exit_code == 1

    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    record = state["stages"]["prod:rep1"]
    assert record["status"] == "failed"
    assert record["error"] and "exit code 1" in record["error"]
    assert "pbc:rep1" not in state["stages"]

    # The per-command log keeps the full command line and the tool output tail.
    log = (run_dir / "logs" / "prod.log").read_text(encoding="utf-8")
    assert "mdrun" in log and "-deffnm" in log and "06_prod" in log
    assert "production mdrun failed" in log


def test_stage_force_reruns_only_that_stage(tmp_path, e2e_run):
    run_dir, invoke = e2e_run(n_replicas=1)
    first = invoke(["md", "run", str(run_dir / "run.yaml"), "--yes"])
    assert first.exit_code == 0, first.output

    before = stage_calls()
    result = invoke(["md", "stage", "nvt:rep1", str(run_dir), "--force"])
    assert result.exit_code == 0, result.output

    new_calls = stage_calls()[len(before):]
    assert len(new_calls) == 2, new_calls
    assert new_calls[0].startswith("grompp") and "04_nvt" in new_calls[0]
    assert new_calls[1].startswith("mdrun") and "04_nvt" in new_calls[1]

    state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    assert state["stages"]["nvt:rep1"]["status"] == "done"
