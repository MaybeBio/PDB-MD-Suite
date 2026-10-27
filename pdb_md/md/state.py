"""Run state persistence, hashing helpers, and the run lock.

``state.json`` is the pipeline's audit trail and skip-logic input.  It lives at
the run root and records, per stage, the input hash that produced it, the
artifacts it emitted, timestamps, and the last failure.  A stage is skipped
only when its status is ``done``, its input hash still matches, and every
artifact still exists.

Hashing policy:

* ``sha256_text`` / ``sha256_file`` - full hashes for small inputs.
* ``sha256_parts`` - recursive, order-preserving hash of a sequence of parts.
* ``file_fingerprint`` - cheap fingerprint for huge trajectory files (size,
  mtime, first/last 64 KiB).
* ``hash_or_missing`` - never raises for a missing file; returns
  ``"missing:<relpath>"`` so a first ``--dry-run`` can still plan stages whose
  upstream artifacts do not exist yet.  This is a global constraint of the
  pipeline: every stage's ``input_hash`` must read upstream artifacts through
  this helper.
"""

import fcntl
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Sequence

from .errors import PreflightError

# Chunk size used by ``file_fingerprint`` for the head/tail samples.
_FINGERPRINT_CHUNK = 64 * 1024
# Files at or below this size are hashed whole rather than by head/tail.
_FINGERPRINT_WHOLE = 4 * 1024


def _utc_now() -> str:
    """Return the current UTC time in ISO 8601 form."""

    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    """Return the hex sha256 digest of ``text`` encoded as UTF-8."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the hex sha256 digest of ``path`` without loading it whole."""

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_parts(parts: Sequence[object]) -> str:
    """Hash a sequence of config fragments / hashes as one stable value.

    The parts are serialised with ``json.dumps(..., sort_keys=True,
    default=str)`` so nested dicts are key-sorted recursively while unknown
    leaf objects (``Path``, dataclasses exposed via ``asdict``, ...) become
    their ``str()``.  List order is preserved and matters: callers pass the
    parts in a fixed, documented order.
    """

    payload = json.dumps(list(parts), sort_keys=True, default=str)
    return sha256_text(payload)


def file_fingerprint(path: Path) -> str:
    """Return a cheap fingerprint for a potentially huge file.

    Full sha256 is unacceptable for trajectories that can reach tens of GB.
    Instead hash the size, ``st_mtime_ns``, and the first and last 64 KiB of
    content.  Files of at most 4 KiB are read whole.  Any change in size,
    mtime, or sampled content changes the fingerprint.

    Note this is a change detector, not a cryptographic integrity check.
    """

    path = Path(path)
    stat = path.stat()
    digest = hashlib.sha256()
    digest.update("{}:{}".format(stat.st_size, stat.st_mtime_ns).encode("ascii"))

    with open(path, "rb") as handle:
        if stat.st_size <= _FINGERPRINT_WHOLE:
            digest.update(handle.read())
        else:
            digest.update(handle.read(_FINGERPRINT_CHUNK))
            if stat.st_size > _FINGERPRINT_CHUNK:
                handle.seek(-_FINGERPRINT_CHUNK, os.SEEK_END)
                digest.update(handle.read(_FINGERPRINT_CHUNK))
    return digest.hexdigest()


def _relative_posix(path: Path, root: Path) -> str:
    """Express ``path`` relative to ``root`` using posix separators."""

    path = Path(path)
    root = Path(root)
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        pass
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def hash_or_missing(
    path: Path,
    root: Path,
    hash_fn: Callable[[Path], str] = sha256_file,
) -> str:
    """Hash ``path``, or return ``"missing:<relpath>"`` when it does not exist.

    Missing files must not raise: the first ``--dry-run`` runs before any
    upstream stage has produced its artifacts, yet every stage's
    ``input_hash`` still has to be computable.  ``root`` is the run root used
    for the relative (posix) path in the sentinel value.
    """

    path = Path(path)
    if not path.exists():
        return "missing:" + _relative_posix(path, root)
    return hash_fn(path)


@dataclass
class StageRecord:
    """Persisted status of one pipeline stage."""

    status: str  # pending | running | done | failed
    input_hash: str = ""
    artifacts: list[str] = field(default_factory=list)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    log: Optional[str] = None
    error: Optional[str] = None


class RunState:
    """The contents of ``state.json``: stage records plus run-level metadata."""

    schema_version = 1

    def __init__(
        self,
        path: Path,
        run_name: str,
        config_hash: str = "",
        tool_versions: Optional[dict] = None,
    ):
        self.path = Path(path)
        self.run_name = run_name
        self.created_at = _utc_now()
        self.config_hash = config_hash
        self.tool_versions = dict(tool_versions or {})
        self.stages: "dict[str, StageRecord]" = {}

    @classmethod
    def load(cls, path: Path, run_name: str) -> "RunState":
        """Load ``state.json``, returning an empty state when it is absent."""

        path = Path(path)
        state = cls(path, run_name)
        if not path.exists():
            return state

        data = json.loads(path.read_text(encoding="utf-8"))
        state.run_name = data.get("run_name") or run_name
        state.created_at = data.get("created_at") or state.created_at
        state.config_hash = data.get("config_hash") or ""
        state.tool_versions = dict(data.get("tool_versions") or {})

        for key, raw in (data.get("stages") or {}).items():
            state.stages[key] = StageRecord(
                status=raw.get("status", "pending"),
                input_hash=raw.get("input_hash") or "",
                artifacts=list(raw.get("artifacts") or []),
                started_at=raw.get("started_at"),
                finished_at=raw.get("finished_at"),
                log=raw.get("log"),
                error=raw.get("error"),
            )
        return state

    def set_config_hash(self, config_hash: str) -> None:
        """Record the hash of the run configuration (audit only)."""

        self.config_hash = config_hash

    def set_tool_versions(self, versions: "dict[str, str]") -> None:
        """Record tool versions captured for this run."""

        self.tool_versions = dict(versions)

    def save(self) -> None:
        """Atomically write ``state.json`` (tmp file + ``os.replace``)."""

        payload = {
            "schema_version": self.schema_version,
            "run_name": self.run_name,
            "created_at": self.created_at,
            "config_hash": self.config_hash,
            "tool_versions": self.tool_versions,
            "stages": {key: asdict(record) for key, record in self.stages.items()},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(tmp), str(self.path))

    def get(self, key: str) -> Optional[StageRecord]:
        """Return the record for ``key``, or ``None`` if it was never seen."""

        return self.stages.get(key)

    def record_start(
        self, key: str, input_hash: str, log: Optional[str]
    ) -> None:
        """Mark ``key`` as running, replacing any previous record."""

        self.stages[key] = StageRecord(
            status="running",
            input_hash=input_hash,
            log=log,
            started_at=_utc_now(),
        )

    def record_done(
        self, key: str, artifacts: Sequence[Path], root: Path
    ) -> None:
        """Mark ``key`` done and store its artifacts relative to ``root``."""

        record = self.stages.get(key)
        now = _utc_now()
        if record is None:
            record = StageRecord(status="running", started_at=now)
            self.stages[key] = record
        record.status = "done"
        record.artifacts = [_relative_posix(item, root) for item in artifacts]
        record.finished_at = now
        record.error = None
        if record.started_at is None:
            record.started_at = now

    def record_failed(self, key: str, error: str) -> None:
        """Mark ``key`` failed, keeping the error message for the audit trail."""

        record = self.stages.get(key)
        now = _utc_now()
        if record is None:
            record = StageRecord(status="running", started_at=now)
            self.stages[key] = record
        record.status = "failed"
        record.error = error
        record.finished_at = now

    def _artifact_exists(self, artifact: object) -> bool:
        path = Path(artifact)
        if not path.is_absolute():
            path = self.path.parent / path
        return path.exists()

    def is_done(
        self, key: str, input_hash: str, artifacts: Sequence[Path]
    ) -> bool:
        """Return True when ``key`` may be skipped.

        Requires status ``done``, an unchanged ``input_hash``, and every
        artifact - both the recorded (relative) ones and the expected ones
        passed by the caller - to exist on disk.  Relative artifacts resolve
        against the directory holding ``state.json`` (the run root).
        """

        record = self.stages.get(key)
        if record is None or record.status != "done":
            return False
        if record.input_hash != input_hash:
            return False
        if not all(self._artifact_exists(item) for item in record.artifacts):
            return False
        return all(self._artifact_exists(item) for item in artifacts)


class RunLock:
    """Exclusive advisory lock preventing concurrent runs on one workdir.

    Backed by ``fcntl.flock`` on a lock file; the holder writes its pid so a
    conflicting process can report who is running.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self._fd: Optional[int] = None

    def __enter__(self) -> "RunLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(self.path), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            pid = _read_pid(fd)
            os.close(fd)
            raise PreflightError("run is locked by pid {}".format(pid))
        # We own the lock: replace any stale pid from a previous run.
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, str(os.getpid()).encode("ascii"))
        self._fd = fd
        return self

    def __exit__(self, *exc) -> None:
        if self._fd is None:
            return
        try:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            os.close(self._fd)
            self._fd = None


def _read_pid(fd: int) -> str:
    """Read the pid the lock holder wrote, or ``"unknown"`` if unreadable."""

    try:
        os.lseek(fd, 0, os.SEEK_SET)
        raw = os.read(fd, 64)
    except OSError:
        return "unknown"
    pid = raw.decode("ascii", errors="replace").strip()
    return pid or "unknown"
