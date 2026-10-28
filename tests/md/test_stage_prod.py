import dataclasses
import pytest
from pdb_md.md.errors import StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.stages.prod import ProdStage
from pdb_md.md.state import RunState

FAKE_GMX = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
pathlib.Path("calls.log").open("a").write(" ".join(args) + "\n")
for flag, exts in (("-o", ("tpr",)), ("-deffnm", ("tpr", "gro", "xtc", "edr", "log", "cpt"))):
    if flag in args:
        pre = args[args.index(flag) + 1]
        for ext in exts:
            pathlib.Path(pre + "." + ext).write_text("x\n")
'''

def setup(tmp_path, make_config, write_script, force=False, with_npt_cpt=True):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "gmx", FAKE_GMX)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, gmx=str(exe)))
    (tmp_path / "02_topology").mkdir()
    (tmp_path / "02_topology" / "topol.top").write_text("[ molecules ]\nprot 1\n")
    d = tmp_path / "05_npt" / "rep1"; d.mkdir(parents=True)
    (d / "npt.gro").write_text("x\n3\n" + "".join(
        f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in (1, 2, 3)) + "1 1 1\n")
    if with_npt_cpt:
        (d / "npt.cpt").write_text("x")
    ctx = RunContext(cfg, tmp_path, RunState(tmp_path / "state.json", cfg.run_name),
                     Runner(tmp_path / "logs"), force)
    return cfg, ctx

def test_prod_uses_mdp_prod_and_resumes(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    prefix = f"{cfg.run_name}_md_r1"
    (tmp_path / "06_prod" / "rep1").mkdir(parents=True)
    (tmp_path / "06_prod" / "rep1" / f"{prefix}.cpt").write_text("x")
    ProdStage(cfg, 1).run(ctx)
    lines = (tmp_path / "calls.log").read_text().splitlines()
    g = [ln for ln in lines if ln.startswith("grompp ")][0]
    assert str(cfg.path(cfg.mdp.prod)) in g and "-t " in g
    md = [ln for ln in lines if ln.startswith("mdrun ")][0]
    assert f"-cpi {tmp_path}/06_prod/rep1/{prefix}.cpt" in md

def test_force_restarts_without_cpi(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script, force=True)
    prefix = f"{cfg.run_name}_md_r1"
    (tmp_path / "06_prod" / "rep1").mkdir(parents=True)
    (tmp_path / "06_prod" / "rep1" / f"{prefix}.cpt").write_text("x")
    ProdStage(cfg, 1).run(ctx)
    md = [ln for ln in (tmp_path / "calls.log").read_text().splitlines() if ln.startswith("mdrun ")][0]
    assert "-cpi" not in md

def test_missing_npt_cpt_fails(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script, with_npt_cpt=False)
    with pytest.raises(StageError, match="npt.cpt"):
        ProdStage(cfg, 1).run(ctx)
