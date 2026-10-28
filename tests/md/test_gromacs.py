from pdb_md.md.gromacs import read_gro, read_top, total_atoms
from pdb_md.md.parmed_convert import postprocess_top_text


def test_pairs_section_renamed_and_atomtypes_deduped():
    text = ("[ atomtypes ]\nZN 65.0 0.0 A 0.0 0.0\nZN 65.0 0.0 A 0.0 0.0\n"
            "[ pairs ]\n1 2 1\n")
    out = postprocess_top_text(text)
    assert "[ pairs_nb ]" in out and "[ pairs ]" not in out
    assert out.count("ZN 65.0 0.0 A 0.0 0.0") == 1


def test_read_top_and_gro(tmp_path):
    top = tmp_path / "t.top"
    top.write_text("[ moleculetype ]\nprot 3\n[ atoms ]\n1 ZN 1 ZN4 ZN 1 0 65\n"
                   "2 CA 2 ALA CA 2 0 12\n3 N 2 ALA N 3 0 14\n"
                   "[ moleculetype ]\nSOL 2\n[ atoms ]\n1 OW 1 SOL OW 1 0 16\n"
                   "[ molecules ]\nprot 1\nSOL 2\n")
    gro = tmp_path / "c.gro"
    gro.write_text("x\n3\n    1ZN4    ZN    1   0.000   0.000   0.000\n"
                   "    1SOL    OW    2   1.000   0.000   0.000\n    1SOL    OW    3   2.000   0.000   0.000\n1 1 1\n")
    t = read_top(top); g = read_gro(gro)
    # prot: 1 个分子 × 3 原子；SOL: 2 个分子 × 1 原子
    assert total_atoms(t) == 5 and len(g.atoms) == 3 and g.atoms[0].resname == "ZN4"
