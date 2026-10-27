import pytest

from pdb_md.md.coords import StructureTable
from pdb_md.md.errors import ConfigError
from pdb_md.md.tleap import (
    compute_split_counts,
    count_prmtop_atoms,
    parse_leap_log,
    prmtop_residue_atoms,
    render_pass1_script,
    render_pass2_script,
)
from pdb_md.md.zinc import LigandCheck, SiteCheck


def test_split_negative_charge():
    c = compute_split_counts(6336, -34, 0.15, "NA", "CL")
    assert c.counter == 34 and c.coion == 0
    assert c.counter_name == "NA" and c.coion_name == "CL"


def test_split_positive_charge_swaps():
    c = compute_split_counts(10000, 10, 0.15, "NA", "CL")   # no = 26.7857
    assert c.counter_name == "CL" and c.coion_name == "NA"
    assert (c.counter, c.coion) == (32, 22)


def test_split_negative_coion_rejected():
    with pytest.raises(ConfigError, match="coion|charge"):
        compute_split_counts(100, 500, 0.15, "NA", "CL")


def test_round_half_up():
    # no = 280 * 0.1 / 56 = 0.5: half-up gives 1, Python round() gives 0
    assert compute_split_counts(280, 0, 0.1, "NA", "CL").counter == 1


def test_render_bonds_and_pass_difference(make_config):
    cfg = make_config()
    table = StructureTable(residues=[], atoms=[], has_ter=True, resname_overflow=False)
    sites = [SiteCheck(
        index=1, center_id=4, zn_position=5, zn_atom_index=5,
        ligands=[LigandCheck(ref=cfg.zinc_sites[0].ligands[i],
                             position=i + 1, atom_index=i + 1, distance=2.1)
                 for i in range(4)],
        extra_near=[], bond_violations=[])]
    # 5000 waters / -8 charge is the solvated-box scale used by the zaff stage
    # (Task 10 expects counter=17, coion=9); 500 waters cannot hold the salt.
    counts = compute_split_counts(5000, -8, 0.15, "NA", "CL")
    p1 = render_pass1_script(cfg, table, sites, "run")
    p2 = render_pass2_script(cfg, counts, "run")
    assert p1.count("bond mol.") == 4
    assert "solvateBox" in p1 and "addionsrand" not in p1
    assert "addionsrand" in p2 and "solvateBox" not in p2
    assert "loadamberparm" in p2
    assert cfg.forcefield.atom_types.strip() in p1


def test_parse_log():
    text = "Added 6336 residues.\nTotal unperturbed charge: -34.000000\nVolume: 287027.740 (A^3)\nDensity: 0.998\n"
    info = parse_leap_log(text)
    assert (info.water_count, info.net_charge) == (6336, -34)
    assert info.volume_A3 == pytest.approx(287027.740) and info.density == pytest.approx(0.998)


def test_parse_log_failure_returns_none():
    info = parse_leap_log("nothing useful")
    assert info.water_count is None and info.net_charge is None


def test_prmtop_residue_atoms(tmp_path):
    p = tmp_path / "a.prmtop"
    p.write_text("%FLAG POINTERS\n%FORMAT(10I8)\n       4       3       1       0\n"
                 "%FLAG ATOM_NAME\n%FORMAT(20a4)\nN   CA  SG  ZN  \n"
                 "%FLAG RESIDUE_POINTER\n%FORMAT(10I8)\n       1       3       4\n")
    assert count_prmtop_atoms(p) == 4
    assert prmtop_residue_atoms(p) == [["N", "CA"], ["SG"], ["ZN"]]
