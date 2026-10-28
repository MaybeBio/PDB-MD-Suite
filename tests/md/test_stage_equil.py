import dataclasses
import pytest
from pdb_md.md.config import ReplicatesConfig
from pdb_md.md.errors import ConfigError, StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.stages.equil import NptStage, NvtStage, write_seeded_mdp
from pdb_md.md.state import RunState

FAKE_GMX = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
pathlib.Path("calls.log").open("a").write(" ".join(args) + "\n")
if args[0] == "mdrun":
    pre = args[args.index("-deffnm") + 1]
    for ext in ("tpr", "edr", "log", "cpt"):
        pathlib.Path(pre + "." + ext).write_text("x\n")
    pathlib.Path(pre + ".gro").write_text("x\n3\n" + "".join(
        f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in (1, 2, 3)) + "1 1 1\n")
'''

def setup(tmp_path, make_config, write_script, top="[ molecules ]\nprot 1\n"):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "gmx", FAKE_GMX)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, gmx=str(exe)))
    (tmp_path / "02_topology").mkdir()
    (tmp_path / "02_topology" / "topol.top").write_text(top)
    (tmp_path / "02_topology" / "conf.gro").write_text(
        "x\n3\n" + "".join(f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in (1, 2, 3)) + "1 1 1\n")
    ctx = RunContext(cfg, tmp_path, RunState(tmp_path / "state.json", cfg.run_name),
                     Runner(tmp_path / "logs"), False)
    return cfg, ctx

def test_seed_is_replaced_per_replica(tmp_path, make_config):
    cfg = make_config(replicates=ReplicatesConfig(count=2, seeds=(10001, 20002)))
    write_seeded_mdp(cfg.path(cfg.mdp.nvt), tmp_path / "nvt_r2.mdp", 20002)
    text = (tmp_path / "nvt_r2.mdp").read_text()
    assert "gen_seed = 20002" in text and "gen_seed = 1\n" not in text

def test_missing_gen_seed_fails(tmp_path, make_config):
    cfg = make_config()
    src = cfg.path(cfg.mdp.nvt)
    src.write_text("\n".join(ln for ln in src.read_text().splitlines()
                             if not ln.strip().startswith("gen_seed")))
    with pytest.raises(ConfigError, match="gen_seed"):
        write_seeded_mdp(src, tmp_path / "nvt_r1.mdp", 1)

def test_nvt_and_npt_commands(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    NvtStage(cfg, 1).run(ctx)
    NptStage(cfg, 1).run(ctx)
    g = [ln for ln in (tmp_path / "calls.log").read_text().splitlines() if ln.startswith("grompp ")]
    assert len(g) == 2
    nvt, npt = g[0], g[1]
    assert f"-r {tmp_path}/03_em/em2.gro" in nvt
    assert f"-t {tmp_path}/04_nvt/rep1/nvt.cpt" in npt
    assert f"-r {tmp_path}/04_nvt/rep1/nvt.gro" in npt

def test_npt_continuation_check(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    npt = cfg.path(cfg.mdp.npt)
    npt.write_text(npt.read_text().replace("continuation = yes", "continuation = no"))
    with pytest.raises(StageError, match="continuation"):
        NptStage(cfg, 1).run(ctx)
