import json
import dataclasses, json
import pytest
from pathlib import Path
from pdb_md.md.errors import StageError
from pdb_md.md.stages.zaff import ZaffStage
from pdb_md.md.plan import RunContext
from pdb_md.md.state import RunState
from pdb_md.md.runner import Runner
from tests.md.fixtures import PDB_WITH_ZN

FAKE_TLEAP = r'''#!/usr/bin/env python3
import re, sys, pathlib
script = pathlib.Path(sys.argv[sys.argv.index("-f") + 1]).read_text()
pathlib.Path("calls.log").open("a").write("tleap\n")
for pre in re.findall(r"saveamberparm mol (\S+)\.prmtop", script):
    n = 200 if pre.endswith("_solv") else 100
    pathlib.Path(pre + ".prmtop").write_text("%%FLAG POINTERS\n %d 200\n" % n)
    pathlib.Path(pre + ".inpcrd").write_text("x\n")
    pathlib.Path(pre + ".pdb").write_text("x\n")
with open("leap.log", "w") as fh:
    if re.search(r"saveamberparm mol \S+_solv", script):
        fh.write("Added 5000 residues.\nTotal unperturbed charge: -8.000000\n")
    else:
        fh.write("Total unperturbed charge: -8.000000\n")
'''

def setup(tmp_path, make_config, write_script, tleap_body=FAKE_TLEAP):
    cfg = make_config(root=tmp_path)
    exe = write_script(tmp_path / "tleap", tleap_body)
    cfg = dataclasses.replace(cfg, tools=dataclasses.replace(cfg.tools, tleap=str(exe)))
    (tmp_path / "00_input").mkdir()
    (tmp_path / "00_input" / "structure.pdb").write_text(PDB_WITH_ZN)
    (tmp_path / "01_zaff").mkdir()
    state = RunState(tmp_path / "state.json", cfg.run_name)
    ctx = RunContext(cfg=cfg, root=tmp_path, state=state,
                     runner=Runner(tmp_path / "logs"), force=False)
    return cfg, ctx

def test_two_passes_and_report(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    ZaffStage(cfg).run(ctx)
    report = json.loads((tmp_path / "01_zaff" / "zaff_report.json").read_text())
    assert (report["salt"]["counter"], report["salt"]["coion"]) == (17, 9)
    assert (tmp_path / "01_zaff" / "leap_pass1.log").exists()
    p2 = (tmp_path / "01_zaff" / "tleap_zaff_pass2.in").read_text()
    assert "addionsrand" in p2 and "solvateBox" not in p2

def test_missing_log_fields_fall_back_to_config(tmp_path, make_config, write_script):
    body = FAKE_TLEAP.replace('fh.write("Added 5000 residues.\\nTotal unperturbed charge: -8.000000\\n")',
                              'fh.write("nothing useful\\n")')
    cfg, ctx = setup(tmp_path, make_config, write_script, body)
    cfg = dataclasses.replace(cfg, system=dataclasses.replace(
        cfg.system, salt=dataclasses.replace(cfg.system.salt, water_count=5000, net_charge=-8)))
    ZaffStage(cfg).run(ctx)   # 覆盖值生效，不应抛错

def test_missing_override_fails(tmp_path, make_config, write_script):
    body = FAKE_TLEAP.replace('fh.write("Added 5000 residues.\\nTotal unperturbed charge: -8.000000\\n")',
                              'fh.write("nothing useful\\n")')
    cfg, ctx = setup(tmp_path, make_config, write_script, body)
    with pytest.raises(StageError, match="leap.log"):
        ZaffStage(cfg).run(ctx)

def test_long_bond_fails_before_tleap(tmp_path, make_config, write_script):
    cfg, ctx = setup(tmp_path, make_config, write_script)
    # 把结构中的配体 1 移到 3.4 A 之外，或直接改 zinc_sites 的坐标夹具
    (tmp_path / "00_input" / "structure.pdb").write_text(PDB_WITH_ZN.replace(" 2.100   0.000   0.000", " 3.400   0.000   0.000", 1))
    with pytest.raises(StageError, match="3.4"):
        ZaffStage(cfg).run(ctx)
    assert not (tmp_path / "01_zaff" / "calls.log").exists()
