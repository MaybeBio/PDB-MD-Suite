import dataclasses, json
import pytest
from pdb_md.md.errors import StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.stages.em import EmStage
from pdb_md.md.state import RunState

FAKE_GMX = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
pathlib.Path("calls.log").open("a").write(" ".join(args) + "\n")
if args[0] == "mdrun":
    pre = args[args.index("-deffnm") + 1]
    for ext in ("tpr", "edr", "log"):
        pathlib.Path(pre + "." + ext).write_text("x\n")
    pathlib.Path(pre + ".gro").write_text("x\n3\n" + "".join(
        f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in (1, 2, 3)) + "1 1 1\n")
'''

def setup(tmp_path, make_config, write_script, body=FAKE_GMX, top="[ molecules ]\nprot 1\n"):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "gmx", body)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, gmx=str(exe)))
    (tmp_path / "02_topology").mkdir()
    (tmp_path / "02_topology" / "topol.top").write_text(top)
    (tmp_path / "02_topology" / "conf.gro").write_text(
        "x\n3\n" + "".join(f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in (1, 2, 3)) + "1 1 1\n")
    ctx = RunContext(cfg, tmp_path, RunState(tmp_path / "state.json", cfg.run_name),
                     Runner(tmp_path / "logs"), False)
    return cfg, ctx

def test_em_chain_and_maxwarn(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    EmStage(cfg).run(ctx)
    g = [ln for ln in (tmp_path / "calls.log").read_text().splitlines() if ln.startswith("grompp ")]
    assert len(g) == 2 and all("-maxwarn 0" in ln for ln in g)
    assert f"-c {tmp_path}/02_topology/conf.gro" in g[0]
    assert f"-c {tmp_path}/03_em/em1.gro" in g[1]
    assert (tmp_path / "03_em" / "em2.gro").exists()

def test_nan_in_gro_fails(tmp_path, make_config, write_script):
    body = FAKE_GMX.replace("0.0 0.0 0.0\\n\" for i in (1, 2, 3)", "nan 0.0 0.0\\n\" for i in (1, 2, 3)")
    cfg, ctx = setup(tmp_path, make_config, write_script, body)
    with pytest.raises(StageError, match="nan|NaN"):
        EmStage(cfg).run(ctx)

def test_missing_flexible_warns_not_fails(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script, top="[ settles ]\n[ molecules ]\nprot 1\n")
    EmStage(cfg).run(ctx)
    report = json.loads((tmp_path / "03_em" / "em_report.json").read_text())
    assert report["warnings"]
