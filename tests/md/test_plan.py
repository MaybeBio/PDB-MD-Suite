from dataclasses import dataclass, field
from pathlib import Path
import pytest
from pdb_md.md.config import ReplicatesConfig
from pdb_md.md.errors import ConfigError, PreflightError
from pdb_md.md.plan import (build_stages, compute_actions, select_stages,
                            stage_plan, execute, RunContext)
from pdb_md.md.state import RunState

@dataclass
class Dummy:
    key: str
    deps: tuple = ()
    hash_value: str = "h"
    fail: bool = False
    def input_hash(self, cfg, root): return self.hash_value
    def artifacts(self, cfg, root): return []
    def run(self, ctx):
        if self.fail: raise RuntimeError("boom")
    def verify(self, cfg, root): pass

def test_stage_order(make_config):
    cfg = make_config(replicates=ReplicatesConfig(count=2, seeds=(1, 2)))
    keys = [k for k, _ in stage_plan(cfg)]
    assert keys[:4] == ["preprocess", "zaff", "topology", "em"]
    assert keys[4:8] == ["nvt:rep1", "npt:rep1", "prod:rep1", "pbc:rep1"]
    assert keys[8:12] == ["nvt:rep2", "npt:rep2", "prod:rep2", "pbc:rep2"]

def test_select_from_to_and_only(make_config):
    cfg = make_config()
    stages = [Dummy(k, d) for k, d in stage_plan(cfg)]
    assert [s.key for s in select_stages(stages, from_key="topology", to_key="npt:rep1")] \
        == ["topology", "em", "nvt:rep1", "npt:rep1"]
    assert [s.key for s in select_stages(stages, only="em")] == ["em"]
    with pytest.raises(ConfigError):
        select_stages(stages, only="nope")

def test_done_requires_all_deps_done(make_config, tmp_path):
    cfg = make_config()
    state = RunState(tmp_path / "state.json", "r")
    for k, _ in stage_plan(cfg):
        state.record_start(k, "h", None); state.record_done(k, [], tmp_path)
    stages = [Dummy(k, d) for k, d in stage_plan(cfg)]
    assert all(a.kind == "skip" for a in compute_actions(stages, state, cfg, tmp_path))

def test_upstream_failure_forces_downstream(make_config, tmp_path):
    cfg = make_config()
    state = RunState(tmp_path / "state.json", "r")
    for k, _ in stage_plan(cfg):
        state.record_start(k, "h", None); state.record_done(k, [], tmp_path)
    state.record_failed("zaff", "boom")
    stages = [Dummy(k, d) for k, d in stage_plan(cfg)]
    acts = {a.key: a for a in compute_actions(stages, state, cfg, tmp_path)}
    assert acts["zaff"].kind == "run" and acts["zaff"].reason == "failed"
    assert acts["topology"].reason == "upstream-rerun"

def test_execute_stops_on_failure(make_config, tmp_path):
    cfg = make_config()
    state = RunState(tmp_path / "state.json", "r")
    stages = [Dummy("preprocess", ()), Dummy("zaff", ("preprocess",), fail=True),
              Dummy("topology", ("zaff",))]
    ctx = RunContext(cfg=cfg, root=tmp_path, state=state, runner=None, force=False)
    with pytest.raises(RuntimeError):
        execute(stages, compute_actions(stages, state, cfg, tmp_path), ctx)
    assert state.get("preprocess").status == "done"
    assert state.get("zaff").status == "failed"
    assert state.get("topology") is None
