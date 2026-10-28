import yaml
from typer.testing import CliRunner
from pdb_md.cli import app


def test_template_flag_writes_parseable_yaml(tmp_path):
    out = tmp_path / "run.yaml"
    r = CliRunner().invoke(app, ["md", "init", "-o", str(out), "--template"])
    assert r.exit_code == 0
    data = yaml.safe_load(out.read_text())
    assert data["schema_version"] == 1
    assert data["topology"]["posre_fc"] == 1000.0
    assert data["pbc"]["groups"]["output"] == "System"


def test_wizard_uses_answers(tmp_path):
    out = tmp_path / "run.yaml"
    answers = "myrun\ninputs/x.pdb\ngmx\ntleap\npython\nmdp/em1.mdp\nmdp/em2.mdp\nmdp/nvt.mdp\nmdp/npt.mdp\nmdp/md.mdp\n3\n0.15\n"
    r = CliRunner().invoke(app, ["md", "init", "-o", str(out)], input=answers)
    assert r.exit_code == 0
    data = yaml.safe_load(out.read_text())
    assert data["run_name"] == "myrun" and data["replicates"]["count"] == 3


def test_refuses_overwrite_without_force(tmp_path):
    out = tmp_path / "run.yaml"; out.write_text("x")
    r = CliRunner().invoke(app, ["md", "init", "-o", str(out), "--template"])
    assert r.exit_code == 2 and "--force" in r.output
