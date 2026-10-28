import pytest
from pdb_md.md.errors import StageError
from pdb_md.md.gromacs import GroAtom
from pdb_md.md.zinc import SiteAtoms, map_site_atoms


def test_positions_map_to_system_atoms():
    report = [{"index": 1, "zn": {"position": 1},
               "ligands": [{"position": 2, "atom": "CA"}, {"position": 2, "atom": "N"},
                           {"position": 3, "atom": "OW"}]}]
    atoms = [GroAtom(1, 1, "ZN4", "ZN"), GroAtom(2, 2, "ALA", "CA"),
             GroAtom(3, 2, "ALA", "N"), GroAtom(4, 3, "SOL", "OW")]
    assert map_site_atoms(report, [["ZN"], ["CA", "N"], ["OW"]], atoms) == \
        [SiteAtoms(1, [2, 3, 4])]


def test_gro_name_mismatch_fails():
    report = [{"index": 1, "zn": {"position": 1},
               "ligands": [{"position": 2, "atom": "CA"}]}]
    atoms = [GroAtom(1, 1, "ZN4", "ZN"), GroAtom(2, 2, "ALA", "CB")]
    with pytest.raises(StageError, match="site 1"):
        map_site_atoms(report, [["ZN"], ["CA"]], atoms)
