import dataclasses, json
import pytest
from pdb_md.md.errors import StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.stages.topology import TopologyStage
from pdb_md.md.state import RunState

FAKE_PARMED = r'''#!/usr/bin/env python3
import sys, pathlib
args = sys.argv[1:]
top = pathlib.Path(args[args.index("--top") + 1]); gro = pathlib.Path(args[args.index("--gro") + 1])
top.write_text("[ moleculetype ]\nprot 3\n[ atoms ]\n1 ZN 1 ZN4 ZN 1 0 65\n"
               "2 CA 2 ALA CA 2 0 12\n3 N 2 ALA N 3 0 14\n"
               "[ moleculetype ]\nSOL 2\n[ atoms ]\n1 OW 1 SOL OW 1 0 16\n"
               "[ molecules ]\nprot 1\nSOL 2\n")
gro.write_text("x\n5\n    1ZN4    ZN    1   0.0 0.0 0.0\n"
               "    2ALA    CA    2   0.1 0.0 0.0\n    2ALA     N    3   0.2 0.0 0.0\n"
               "    1SOL    OW    4   1.0 0.0 0.0\n    1SOL    OW    5   1.1 0.0 0.0\n1 1 1\n")
'''

# 与 FAKE_PARMED 的 conf.gro 同序：ZN4/ZN | ALA/CA,N | SOL/OW | SOL/OW
PRMTOP5 = ("%FLAG POINTERS\n%FORMAT(10I8)\n       5       4       1       0\n"
           "%FLAG ATOM_NAME\n%FORMAT(20a4)\nZN  CA  N   OW  OW  \n"
           "%FLAG RESIDUE_POINTER\n%FORMAT(10I8)\n       1       2       4       5\n")

ZAFF_REPORT = {"n_atoms_input": 5, "n_sites": 1,
    "zinc_sites": [{"index": 1, "center_id": 4,
        "zn": {"position": 1, "resid": 1, "atom_index": 1},
        "ligands": [
            {"position": 2, "resid": 2, "resname": "ALA", "atom": "CA", "atom_index": 2, "distance": 2.1},
            {"position": 2, "resid": 2, "resname": "ALA", "atom": "N", "atom_index": 3, "distance": 2.1},
            {"position": 3, "resid": 3, "resname": "SOL", "atom": "OW", "atom_index": 4, "distance": 2.1},
            {"position": 4, "resid": 4, "resname": "SOL", "atom": "OW", "atom_index": 5, "distance": 2.1}],
        "extra_near": [], "bond_violations": []}],
    "salt": {"counter": 0, "coion": 0, "counter_name": "NA", "coion_name": "CL",
             "water_count": 2, "net_charge": 0},
    "warnings": []}

def setup(tmp_path, make_config, write_script, body=FAKE_PARMED):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "parmed", body)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, parmed_python=str(exe)))
    (tmp_path / "01_zaff").mkdir()
    (tmp_path / "01_zaff" / f"{cfg.run_name}_solv.prmtop").write_text(PRMTOP5)
    (tmp_path / "01_zaff" / f"{cfg.run_name}_solv.inpcrd").write_text("x")
    (tmp_path / "01_zaff" / "zaff_report.json").write_text(json.dumps(ZAFF_REPORT))
    ctx = RunContext(cfg, tmp_path, RunState(tmp_path / "state.json", cfg.run_name),
                     Runner(tmp_path / "logs"), False)
    return cfg, ctx

def test_stage_generates_posre_and_checks_counts(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    TopologyStage(cfg).run(ctx)
    TopologyStage(cfg).verify(cfg, tmp_path)
    itp = (tmp_path / "02_topology" / "posre_prot.itp").read_text()
    assert len([ln for ln in itp.splitlines() if ln.strip() and not ln.startswith((";", "["))]) == 3
    report = json.loads((tmp_path / "02_topology" / "topology_report.json").read_text())
    assert report["solutes"] == ["prot"]
    assert json.loads((tmp_path / "02_topology" / "site_atoms.json").read_text()) == \
        [{"zn": 1, "ligand_atoms": [2, 3, 4, 5]}]

def test_atom_count_mismatch_fails(tmp_path, make_config, write_script):
    body = FAKE_PARMED.replace("x\\n5\\n", "x\\n4\\n").replace(
        "    1SOL    OW    5   1.1 0.0 0.0\\n", "")
    cfg, ctx = setup(tmp_path, make_config, write_script, body)
    with pytest.raises(StageError, match="atom count"):
        TopologyStage(cfg).run(ctx)
