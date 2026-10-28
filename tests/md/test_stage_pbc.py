import dataclasses, json
import pytest
from pdb_md.md.errors import PreflightError, StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.state import RunState
from pdb_md.md.stages.pbc import PbcStage

FAKE_GMX = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
stdin = sys.stdin.read().strip().replace("\n", ",")
pathlib.Path("calls.log").open("a").write(" ".join(args) + " ||| " + stdin + "\n")
if args[0] == "trjconv":
    pathlib.Path(args[args.index("-o") + 1]).write_text("x")
elif args[0] == "check":
    print("Read 6 atoms")
elif args[0] == "distance":
    n = args.count("-select")
    pathlib.Path(args[args.index("-oav") + 1]).write_text(
        "# gmx distance\n@ s0 legend \"d\"\n0.0 " + " ".join(["2.1"] * n) + "\n")
'''

GRO6 = ("pbc test\n6\n" + "".join(
    f"    1ALA    CA    {i}   0.0 0.0 0.0\n" for i in range(1, 7)) + "1 1 1\n")

def setup(tmp_path, make_config, write_script, body=FAKE_GMX, ndx_only_system=False):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "gmx", body)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, gmx=str(exe)))
    (tmp_path / "02_topology").mkdir()
    (tmp_path / "02_topology" / "conf.gro").write_text(GRO6)
    (tmp_path / "02_topology" / "site_atoms.json").write_text(
        json.dumps([{"zn": 4, "ligand_atoms": [1, 2, 3, 5]}]))
    d = tmp_path / "06_prod" / "rep1"; d.mkdir(parents=True)
    for ext in (".tpr", ".xtc"):
        (d / f"{cfg.run_name}_md_r1{ext}").write_text("x")
    if ndx_only_system:
        user = tmp_path / "user.ndx"
        user.write_text("[ System ]\n" + " ".join(str(i) for i in range(1, 7)) + "\n")
        cfg = dataclasses.replace(cfg, pbc=dataclasses.replace(cfg.pbc, ndx=str(user)))
    ctx = RunContext(cfg, tmp_path, RunState(tmp_path / "state.json", cfg.run_name),
                     Runner(tmp_path / "logs"), False)
    return cfg, ctx

def calls(tmp_path):
    return (tmp_path / "07_pbc" / "rep1" / "calls.log").read_text().splitlines()

def test_step_order_and_stdin(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    PbcStage(cfg, 1).run(ctx)
    trj = [ln for ln in calls(tmp_path) if ln.startswith("trjconv ")]
    # 6 次调用：whole / cluster / whole / dump0 / nojump / center
    assert [ln.split("|||")[1].strip() for ln in trj] == \
        ["0", "4,0", "0", "0", "0", "4,0"]
    dist = [ln for ln in calls(tmp_path) if ln.startswith("distance ")][0]
    assert dist.count("-select") == 4
    assert "atomnr 4 plus atomnr 1" in dist and "atomnr 4 plus atomnr 5" in dist

def test_missing_group_fails_before_commands(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script, ndx_only_system=True)
    with pytest.raises(PreflightError, match="Complex"):
        PbcStage(cfg, 1).run(ctx)
    assert not (tmp_path / "07_pbc" / "rep1" / "calls.log").exists()

def test_distance_violation_fails(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script, FAKE_GMX.replace('"2.1"', '"3.5"'))
    with pytest.raises(StageError, match="3.5"):
        PbcStage(cfg, 1).run(ctx)

def test_atom_count_mismatch_fails(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script,
                     FAKE_GMX.replace("Read 6 atoms", "Read 5 atoms"))
    with pytest.raises(StageError, match="atom"):
        PbcStage(cfg, 1).run(ctx)
