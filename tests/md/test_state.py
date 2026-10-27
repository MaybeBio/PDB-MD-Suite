import json, pytest
from pdb_md.md.errors import PreflightError
from pdb_md.md.state import (RunState, RunLock, sha256_text, file_fingerprint,
                             hash_or_missing)

def test_roundtrip_and_done_requires_artifacts(tmp_path):
    art = tmp_path / "a.txt"; art.write_text("x")
    st = RunState(tmp_path / "state.json", "r")
    st.record_start("zaff", sha256_text("cfg"), "logs/zaff.log")
    st.record_done("zaff", [art], tmp_path)
    st.save()
    st2 = RunState.load(tmp_path / "state.json", "r")
    assert st2.is_done("zaff", sha256_text("cfg"), [art])
    art.unlink()
    assert not st2.is_done("zaff", sha256_text("cfg"), [art])
    assert not st2.is_done("zaff", sha256_text("other"), [tmp_path / "a.txt"])

def test_state_file_is_valid_json_after_failure(tmp_path):
    st = RunState(tmp_path / "state.json", "r")
    st.record_failed("em", "boom")
    st.save()
    data = json.loads((tmp_path / "state.json").read_text())
    assert data["stages"]["em"]["status"] == "failed"
    assert data["schema_version"] == 1

def test_lock_conflict(tmp_path):
    with RunLock(tmp_path / ".lock"):
        with pytest.raises(PreflightError, match="locked"):
            with RunLock(tmp_path / ".lock"):
                pass

def test_file_fingerprint_tracks_size(tmp_path):
    p = tmp_path / "big.bin"; p.write_bytes(b"a" * 1000)
    fp = file_fingerprint(p)
    assert fp == file_fingerprint(p)
    p.write_bytes(b"a" * 1001)
    assert file_fingerprint(p) != fp

def test_hash_or_missing(tmp_path):
    assert hash_or_missing(tmp_path / "nope", tmp_path) == "missing:nope"
    p = tmp_path / "a.txt"; p.write_text("x")
    assert hash_or_missing(p, tmp_path) == sha256_text("x")
