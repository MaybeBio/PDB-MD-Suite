from pdb_md.md.groups import build_groups, write_ndx, read_ndx, resolve_group
from pdb_md.md.gromacs import GroFile, GroAtom
from pdb_md.md.config import SpeciesConfig
from pdb_md.md.errors import PreflightError
import pytest

def gro():
    rs = [("ALA", "CA"), ("ALA", "N"), ("DA", "P"), ("ZN4", "ZN"), ("SOL", "OW"), ("NA", "NA")]
    return GroFile([GroAtom(i+1, i+1, r, a) for i, (r, a) in enumerate(rs)], (1, 1, 1))

def test_groups_and_complex_excludes_solvent():
    g = build_groups(gro(), SpeciesConfig())
    assert g["Protein"] == [1, 2] and g["DNA"] == [3] and g["Metal"] == [4]
    assert g["Complex"] == [1, 2, 3, 4] and g["System"] == [1, 2, 3, 4, 5, 6]

def test_ndx_roundtrip_and_resolve(tmp_path):
    g = build_groups(gro(), SpeciesConfig())
    p = tmp_path / "pbc.ndx"; write_ndx(g, p)
    assert read_ndx(p)["Complex"] == [1, 2, 3, 4]
    idx, atoms = resolve_group(p, "Complex")
    assert idx == 4 and atoms == [1, 2, 3, 4]

def test_missing_group_lists_available(tmp_path):
    p = tmp_path / "pbc.ndx"; write_ndx(build_groups(gro(), SpeciesConfig()), p)
    with pytest.raises(PreflightError, match="Protein"):
        resolve_group(p, "Protein_Zn")
