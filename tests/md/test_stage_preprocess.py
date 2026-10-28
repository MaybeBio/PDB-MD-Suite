from pathlib import Path
import pytest
from pdb_md.md.config import PreprocessConfig
from pdb_md.md.errors import StageError
from pdb_md.md.plan import RunContext
from pdb_md.md.runner import Runner
from pdb_md.md.stages.preprocess import PreprocessStage
from pdb_md.md.state import RunState

def ctx_for(cfg, root):
    return RunContext(cfg, root, RunState(root / "state.json", cfg.run_name),
                      Runner(root / "logs"), False)

def test_disabled_copies_structure(tmp_path, make_config):
    cfg = make_config(root=tmp_path)
    PreprocessStage(cfg).run(ctx_for(cfg, tmp_path))
    assert (tmp_path / "00_input/structure.pdb").read_text() == \
        cfg.path(cfg.input.structure).read_text()

def test_enabled_runs_steps_in_order(tmp_path, make_config, write_script):
    log = tmp_path / "calls.log"
    script = write_script(tmp_path / "step",
        f'#!/usr/bin/env bash\necho "$1|$2" >> "{log}"\ncp "$1" "$2"\n')
    cfg = make_config(root=tmp_path, preprocess=PreprocessConfig(
        enabled=True, steps=((str(script), "{in}", "{out}"), (str(script), "{in}", "{out}"))))
    PreprocessStage(cfg).run(ctx_for(cfg, tmp_path))
    first, second = log.read_text().splitlines()
    assert Path(second.split("|")[0]) == Path(first.split("|")[1])
    assert Path(second.split("|")[1]) == tmp_path / "00_input/structure.pdb"
    assert (tmp_path / "00_input/structure.pdb").exists()

def test_failing_step_stops(tmp_path, make_config, write_script):
    bad = write_script(tmp_path / "bad", "#!/usr/bin/env bash\nexit 2\n")
    cfg = make_config(root=tmp_path, preprocess=PreprocessConfig(
        enabled=True, steps=((str(bad), "{in}", "{out}"),)))
    with pytest.raises(StageError):
        PreprocessStage(cfg).run(ctx_for(cfg, tmp_path))
    assert not (tmp_path / "00_input/structure.pdb").exists()
