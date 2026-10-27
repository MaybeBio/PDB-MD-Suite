import pytest

from pdb_md.md.coords import read_pdb
from pdb_md.md.config import CoordinationCheck, ResidueRef, ZincSite
from pdb_md.md.errors import PreflightError
from pdb_md.md.zinc import validate_sites, preflight_structure


def write(tmp_path, text, name="s.pdb"):
    p = tmp_path / name
    p.write_text(text)
    return p


def pdb(tmp_path, zn="0.000", sg="2.100", extra=False, ter=True):
    # 配体 1 在 x=sg，Zn 在 x=zn，二者距离 = |zn - sg|
    text = (
        f"ATOM      1  SG  CY4 A   1      {sg}   0.000   0.000  1.00  0.00           S\n"
        "ATOM      2  SG  CY4 A   2      2.100   0.000   0.000  1.00  0.00           S\n"
        "ATOM      3  NE2 HD2 A   3      0.000   2.100   0.000  1.00  0.00           N\n"
        "ATOM      4  NE2 HD2 A   4      0.000   0.000   2.100  1.00  0.00           N\n"
        + ("ATOM      9  SG  CYS A   5      0.000   2.200   0.000  1.00  0.00           S\n" if extra else "")
        + "TER\n"
        f"HETATM    5 ZN   ZN4 B 365    {zn:>8}   0.000   0.000  1.00  0.00          Zn\n"
        + ("TER\n" if ter else "")
    )
    return write(tmp_path, text)


def site():
    return ZincSite(
        center_id=4,
        coordination_number=4,
        zn=ResidueRef("B", 365, "ZN4", "ZN"),
        ligands=tuple(
            [
                ResidueRef("A", 1, "CY4", "SG"),
                ResidueRef("A", 2, "CY4", "SG"),
                ResidueRef("A", 3, "HD2", "NE2"),
                ResidueRef("A", 4, "HD2", "NE2"),
            ]
        ),
    )


def test_pass_and_distances(tmp_path):
    [s] = validate_sites(read_pdb(pdb(tmp_path)), [site()], CoordinationCheck())
    assert s.zn_position == 5 and len(s.ligands) == 4
    assert s.ligands[0].distance == pytest.approx(2.1)
    assert s.bond_violations == []


def test_long_bond_is_reported_not_replaced(tmp_path):
    t = read_pdb(pdb(tmp_path, zn="3.400", sg="0.000"))
    [s] = validate_sites(t, [site()], CoordinationCheck())
    assert any("3.4" in v for v in s.bond_violations)
    assert s.ligands[0].ref.atom == "SG"


def test_extra_near_atom_reported(tmp_path):
    t = read_pdb(pdb(tmp_path, extra=True))
    [s] = validate_sites(t, [site()], CoordinationCheck(report_extra_near_atoms=True))
    near = {(e.chain, e.resid, e.atom) for e in s.extra_near}
    assert near == {("A", 5, "SG")}


def test_his_rejected(tmp_path):
    text = pdb(tmp_path).read_text().replace("CY4 A   1", "HIS A   1")
    t = read_pdb(write(tmp_path, text, "his.pdb"))
    with pytest.raises(PreflightError, match="HIS"):
        preflight_structure(t)


def test_resname_overflow_rejected(tmp_path):
    text = "ATOM      1  CA  HISAA   1      0.000   0.000   0.000  1.00  0.00           C\nTER\nEND\n"
    with pytest.raises(PreflightError, match="rename"):
        preflight_structure(read_pdb(write(tmp_path, text, "ovf.pdb")))


def test_missing_ter_rejected(tmp_path):
    t = read_pdb(pdb(tmp_path, ter=False))
    with pytest.raises(PreflightError, match="TER"):
        validate_sites(t, [site()], CoordinationCheck())


def test_resname_mismatch(tmp_path):
    bad = ZincSite(
        center_id=4,
        coordination_number=4,
        zn=ResidueRef("B", 365, "ZN4", "ZN"),
        ligands=tuple(
            [ResidueRef("A", 1, "CYS", "SG")]
            + [ResidueRef("A", i, "HD2", "NE2") for i in (2, 3, 4)]
        ),
    )
    with pytest.raises(PreflightError, match="CY4"):
        validate_sites(read_pdb(pdb(tmp_path)), [bad], CoordinationCheck())
