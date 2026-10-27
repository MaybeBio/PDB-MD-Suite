import pytest
from pdb_md.md.coords import read_pdb
from pdb_md.md.errors import ConfigError, PreflightError

PDB = """\
ATOM      1  N   ALA A  10      0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A  10      1.000   0.000   0.000  1.00  0.00           C
TER
ATOM      3  P   DA  A   5      0.000   4.000   0.000  1.00  0.00           P
TER
HETATM    4 ZN   ZN4 B 365       1.500   0.000   0.000  1.00  0.00          Zn
TER
END
"""

def write(tmp_path, text, name="s.pdb"):
    p = tmp_path / name; p.write_text(text); return p

def test_positions_follow_file_order_not_resid(tmp_path):
    t = read_pdb(write(tmp_path, PDB))
    assert [r.position for r in t.residues] == [1, 2, 3]
    assert t.locate("A", 5).position == 2
    assert t.locate("B", 365).position == 3

def test_ter_flags(tmp_path):
    t = read_pdb(write(tmp_path, PDB))
    assert t.has_ter
    assert all(r.ter_after for r in t.residues)

def test_duplicate_chain_resid_by_insertion_code(tmp_path):
    text = PDB.replace(
        "HETATM    4 ZN   ZN4 B 365       1.500   0.000   0.000  1.00  0.00          Zn",
        "HETATM    4 ZN   ZN4 B 365A      1.500   0.000   0.000  1.00  0.00          Zn",
    )
    text += "HETATM    5 ZN   ZN4 B 365B      9.000   0.000   0.000  1.00  0.00          Zn\nTER\n"
    t = read_pdb(write(tmp_path, text))
    with pytest.raises(PreflightError) as ei:
        t.locate("B", 365)
    assert "insertion code" in str(ei.value) and "365A" in str(ei.value)

def test_missing_residue_reports_candidates(tmp_path):
    t = read_pdb(write(tmp_path, PDB))
    with pytest.raises(PreflightError, match="chain A"):
        t.locate("A", 99)

def test_resname_overflow_detected(tmp_path):
    text = "ATOM      1  CA  HISAA   1       0.000   0.000   0.000  1.00  0.00           C\nTER\nEND\n"
    assert read_pdb(write(tmp_path, text)).resname_overflow

def test_only_first_model(tmp_path):
    text = "MODEL        1\n" + PDB + "ENDMDL\nMODEL        2\n" + PDB.replace("ALA A  10", "ALA A  11") + "ENDMDL\n"
    t = read_pdb(write(tmp_path, text))
    assert len(t.residues) == 3

def test_distance(tmp_path):
    t = read_pdb(write(tmp_path, PDB))
    zn = t.atom(type("R", (), {"chain": "B", "resid": 365, "atom": "ZN"})())
    ca = t.atom(type("R", (), {"chain": "A", "resid": 10, "atom": "CA"})())
    assert t.distance(zn, ca) == pytest.approx(0.5)
