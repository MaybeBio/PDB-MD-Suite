# tests/md/test_config.py
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
