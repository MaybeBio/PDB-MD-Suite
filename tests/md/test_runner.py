import pytest
from pdb_md.md.errors import StageError
from pdb_md.md.runner import Runner

def test_run_writes_log_and_returns_result(tmp_path, write_script):
    exe = write_script(tmp_path / "hello", "#!/usr/bin/env bash\necho hello\n")
    r = Runner(tmp_path / "logs")
    result = r.run([str(exe)], "x", cwd=tmp_path)
    assert result.returncode == 0
    log = (tmp_path / "logs" / "x.log").read_text()
    assert "$ cd " in log and "hello" in log

def test_nonzero_raises_with_tail(tmp_path, write_script):
    exe = write_script(tmp_path / "bad",
        "#!/usr/bin/env bash\nfor i in $(seq 1 60); do echo line$i; done\nexit 3\n")
    r = Runner(tmp_path / "logs")
    with pytest.raises(StageError) as ei:
        r.run([str(exe)], "bad", cwd=tmp_path)
    assert ei.value.returncode == 3
    assert len(ei.value.tail) == 50 and ei.value.tail[-1] == "line60"
    assert str(exe) in str(ei.value)

def test_stdin_text(tmp_path, write_script):
    exe = write_script(tmp_path / "first", "#!/usr/bin/env bash\nhead -n 1\n")
    Runner(tmp_path / "logs").run([str(exe)], "s", cwd=tmp_path,
                                  stdin_text="Complex\nSystem\n")
    assert "Complex" in (tmp_path / "logs" / "s.log").read_text()

def test_timeout(tmp_path, write_script):
    exe = write_script(tmp_path / "slow", "#!/usr/bin/env bash\nsleep 5\n")
    r = Runner(tmp_path / "logs", timeout_s=0.2)
    with pytest.raises(StageError, match="timed out"):
        r.run([str(exe)], "slow", cwd=tmp_path)

def test_run_capture(tmp_path, write_script):
    exe = write_script(tmp_path / "out", "#!/usr/bin/env bash\necho 2025.1\n")
    assert Runner(tmp_path / "logs").run_capture([str(exe)]) == "2025.1\n"

def test_run_capture_includes_stderr(tmp_path, write_script):
    exe = write_script(
        tmp_path / "both", "#!/usr/bin/env bash\necho out\necho err >&2\n"
    )
    assert Runner(tmp_path / "logs").run_capture([str(exe)]) == "out\nerr\n"
