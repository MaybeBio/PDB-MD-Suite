import json
from typer.testing import CliRunner
from pdb_md.cli import app
from pdb_md.md.config import load_config
from pdb_md.md.state import RunState

def test_dry_run_prints_plan(tmp_path, minimal_yaml, write_script):
    p = minimal_yaml(tmp_path, tools={"gmx": str(write_script(tmp_path / "gmx", "#!/bin/sh\nexit 0\n"))})
    result = CliRunner().invoke(app, ["md", "run", str(p), "--dry-run"])
    assert result.exit_code == 0
    assert "RUN" in result.output and "zaff" in result.output

def test_config_error_exit_2(tmp_path):
    p = tmp_path / "run.yaml"; p.write_text("schema_version: 1\n")
    assert CliRunner().invoke(app, ["md", "run", str(p), "--dry-run"]).exit_code == 2

def test_unknown_stage_exit_2(tmp_path, minimal_yaml):
    p = minimal_yaml(tmp_path)
    assert CliRunner().invoke(app, ["md", "stage", "nope", str(tmp_path)]).exit_code == 2

def test_status_json(tmp_path, minimal_yaml):
    cfg = load_config(minimal_yaml(tmp_path))
    st = RunState(cfg.root / "state.json", cfg.run_name)
    st.set_config_hash("abc")
    st.record_start("zaff", "h", "logs/zaff.log")
    st.save()
    result = CliRunner().invoke(app, ["md", "status", str(cfg.root), "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["run_name"] == cfg.run_name
    assert data["stages"]["zaff"]["status"] == "running"

def test_doctor_missing_tool_exit_3(tmp_path, minimal_yaml):
    p = minimal_yaml(tmp_path, tools={"gmx": "/nonexistent/gmx"})
    assert CliRunner().invoke(app, ["md", "doctor", str(p)]).exit_code == 3


def test_only_implies_force(monkeypatch, tmp_path, minimal_yaml):
    from pdb_md.md import cli as mdcli

    p = minimal_yaml(tmp_path)
    seen = {}

    def fake_compute_actions(stages, state, cfg, root, force=False):
        seen["force"] = force
        return []

    monkeypatch.setattr(mdcli, "compute_actions", fake_compute_actions)

    assert mdcli.execute_run(p, True, True, None, None, "zaff", None, False) == 0
    assert seen["force"] is True

    assert mdcli.execute_run(p, True, True, None, None, None, None, False) == 0
    assert seen["force"] is False
