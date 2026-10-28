# tests/md/test_config.py
from pathlib import Path

import pytest

from pdb_md.md.config import load_config
from pdb_md.md.errors import ConfigError


def test_relative_paths_resolve_against_yaml_dir(tmp_path, minimal_yaml):
    p = minimal_yaml(tmp_path)
    cfg = load_config(p)
    assert cfg.root == tmp_path.resolve()
    assert cfg.path("mdp/em1.mdp") == tmp_path / "mdp/em1.mdp"


def test_seed_count_mismatch(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, seeds=[1])
    with pytest.raises(ConfigError, match="seeds"):
        load_config(p)


def test_duplicate_seeds(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, seeds=[7, 7])
    with pytest.raises(ConfigError, match="distinct"):
        load_config(p)


def test_center_11_rejected(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, center_id=11)
    with pytest.raises(ConfigError, match="11"):
        load_config(p)


def test_coordination_must_be_four(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, coordination_number=5)
    with pytest.raises(ConfigError, match="four|4"):
        load_config(p)


def test_duplicate_ligand_rejected(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, duplicate_ligand=True)
    with pytest.raises(ConfigError, match="duplicate"):
        load_config(p)


def test_unknown_top_level_key_rejected(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, extra_top_level={"typo": 1})
    with pytest.raises(ConfigError, match="typo"):
        load_config(p)


def test_missing_mdp_is_reported(tmp_path, minimal_yaml):
    p = minimal_yaml(tmp_path, delete_mdp="nvt.mdp")
    with pytest.raises(ConfigError, match="nvt.mdp"):
        load_config(p)


def test_maxwarn_mapping(minimal_yaml, tmp_path):
    cfg = load_config(minimal_yaml(tmp_path, maxwarn={"em": 1}))
    assert cfg.stage_maxwarn("em") == 1 and cfg.stage_maxwarn("prod") == 0


def test_missing_pbc_ndx_reported(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, pbc_ndx="nope.ndx")
    with pytest.raises(ConfigError, match="ndx"):
        load_config(p)


def test_malformed_replicates_count_is_config_error(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, replicates_count="two")
    # A raw ValueError/TypeError here would escape the aggregated ConfigError.
    with pytest.raises(ConfigError, match="replicates.count"):
        load_config(p)


def test_malformed_grompp_stage_is_config_error(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path, maxwarn={"em": {"nested": 1}})
    with pytest.raises(ConfigError, match="grompp.em"):
        load_config(p)


def test_unreadable_mdp_is_config_error(minimal_yaml, tmp_path, monkeypatch):
    p = minimal_yaml(tmp_path)
    original = Path.read_text

    def failing_read(self, *args, **kwargs):
        if str(self).endswith(".mdp"):
            raise OSError("permission denied")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", failing_read)
    with pytest.raises(ConfigError, match="cannot read mdp"):
        load_config(p)


def _structure_atoms(path):
    atoms = set()
    for line in Path(path).read_text().splitlines():
        if line.startswith(("ATOM", "HETATM")):
            atoms.add(
                (
                    line[21],
                    int(line[22:26]),
                    line[17:20].strip(),
                    line[12:16].strip(),
                )
            )
    return atoms


def test_make_config_structure_contains_zinc_site_atoms(make_config):
    cfg = make_config()
    path = cfg.path(cfg.input.structure)
    assert path.is_file()
    atoms = _structure_atoms(path)
    site = cfg.zinc_sites[0]
    for ref in (site.zn,) + tuple(site.ligands):
        assert (ref.chain, ref.resid, ref.resname, ref.atom) in atoms


def test_minimal_yaml_structure_contains_zinc_site_atoms(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path)
    cfg = load_config(p)
    path = cfg.path(cfg.input.structure)
    assert path.is_file()
    atoms = _structure_atoms(path)
    site = cfg.zinc_sites[0]
    for ref in (site.zn,) + tuple(site.ligands):
        assert (ref.chain, ref.resid, ref.resname, ref.atom) in atoms


def test_run_name_charset_is_config_error(minimal_yaml, tmp_path):
    # ``run_name`` is interpolated into LEaP input; reject shell/LEaP syntax.
    p = minimal_yaml(tmp_path, extra_top_level={"run_name": "bad/name"})
    with pytest.raises(ConfigError, match="run_name may only contain"):
        load_config(p)


def test_run_dir_whitespace_is_config_error(minimal_yaml, tmp_path):
    p = minimal_yaml(tmp_path / "with space")
    with pytest.raises(ConfigError, match="whitespace"):
        load_config(p)
