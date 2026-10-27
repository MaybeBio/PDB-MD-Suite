# tests/md/test_mdp.py
import pytest
from pdb_md.md.errors import ConfigError
from pdb_md.md.mdp import parse_mdp, check_mdp, replace_key

def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p

def test_parse_strips_comments_and_last_wins(tmp_path):
    p = write(tmp_path, "a.mdp", "dt = 0.001 ; ps\ndt = 0.002\nintegrator = md\n")
    assert parse_mdp(p.read_text()) == {"dt": "0.002", "integrator": "md"}

def test_missing_keys_are_reported(tmp_path):
    p = write(tmp_path, "nvt.mdp", "integrator = md\ngen_vel = yes\n")
    with pytest.raises(ConfigError) as ei:
        check_mdp(p, "nvt")
    msg = str(ei.value)
    assert "nsteps" in msg and "gen_seed" in msg and "nvt.mdp" in msg

def test_nvt_requires_posres_and_gen_vel(tmp_path):
    p = write(tmp_path, "nvt.mdp",
              "integrator=md\nnsteps=1\ndt=0.002\ngen_vel=no\ngen_seed=1\ndefine=-DPOSRES\n")
    with pytest.raises(ConfigError, match="gen_vel"):
        check_mdp(p, "nvt")

def test_replace_key(tmp_path):
    text = "integrator = md\ngen_seed = 1\n"
    out = replace_key(text, "gen_seed", "20002")
    assert "gen_seed = 20002" in out and "integrator = md" in out

def test_replace_missing_key_raises():
    with pytest.raises(ConfigError, match="gen_seed"):
        replace_key("integrator = md\n", "gen_seed", "1")
