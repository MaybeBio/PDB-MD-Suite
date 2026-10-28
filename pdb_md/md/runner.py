"""Subprocess execution helper for the ``pdb-md md`` pipeline.

Every external tool (gmx, tleap, parmed, ...) is invoked through :class:`Runner`
so that command lines and output are persisted to a log file and failures are
surfaced as :class:`~pdb_md.md.errors.StageError`.
"""

import os
import shlex
import shutil
import signal
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from .errors import StageError

TAIL_LINES = 50


def shell_join(argv: Sequence[str]) -> str:
    """Quote ``argv`` for display and logging using shell rules."""

    return shlex.join([str(a) for a in argv])


@dataclass(frozen=True)
class CommandResult:
    """Outcome of a logged command run."""

    argv: list
    cwd: Path
    returncode: int
    log_path: Optional[Path]


class Runner:
    """Run external commands, teeing output to per-command log files."""

    def __init__(
        self,
        log_dir: Path,
        echo: bool = False,
        timeout_s: Optional[float] = None,
    ):
        self.log_dir = Path(log_dir)
        self.echo = echo
        self.timeout_s = timeout_s

    def run(
        self,
        argv: Sequence[str],
        log_name: str,
        cwd: Optional[Path] = None,
        stdin_text: Optional[str] = None,
        check: bool = True,
    ) -> CommandResult:
        """Run ``argv``, appending its command line and output to a log file.

        Raises :class:`StageError` on a non-zero exit when ``check`` is true, or
        when the command exceeds the configured timeout.
        """
        argv = [str(a) for a in argv]
        cwd = Path(cwd) if cwd is not None else Path.cwd()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_path = self.log_dir / ("{}.log".format(log_name))

        header = "$ cd {} && {}".format(cwd, shell_join(argv))
        timed_out = threading.Event()
        timer: Optional[threading.Timer] = None
        tail: "deque[str]" = deque(maxlen=TAIL_LINES)

        with open(log_path, "a", encoding="utf-8") as log:
            log.write(header + "\n")
            log.flush()
            if self.echo:
                print(header, flush=True)

            proc = subprocess.Popen(
                argv,
                cwd=str(cwd),
                stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                start_new_session=True,
            )

            if self.timeout_s is not None:

                def _on_timeout() -> None:
                    if proc.poll() is not None:
                        # Already finished; do not report a spurious timeout.
                        return
                    timed_out.set()
                    proc.kill()
                    # The child may have spawned its own children (e.g. a
                    # shell wrapper); kill the whole process group so the
                    # stdout pipe is actually closed.
                    if os.name == "posix":
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except OSError:
                            pass

                timer = threading.Timer(self.timeout_s, _on_timeout)
                timer.daemon = True
                timer.start()

            try:
                if stdin_text is not None and proc.stdin is not None:
                    try:
                        proc.stdin.write(stdin_text)
                        proc.stdin.flush()
                    except BrokenPipeError:
                        pass
                    finally:
                        try:
                            proc.stdin.close()
                        except BrokenPipeError:
                            pass

                assert proc.stdout is not None
                for line in proc.stdout:
                    line = line.rstrip("\n")
                    tail.append(line)
                    log.write(line + "\n")
                    log.flush()
                    if self.echo:
                        print(line, flush=True)

                returncode = proc.wait()
            finally:
                if timer is not None:
                    timer.cancel()

        hint = "Full log: {}".format(log_path)

        if timed_out.is_set():
            raise StageError(
                "command timed out after {}s".format(self.timeout_s),
                argv=argv,
                cwd=cwd,
                returncode=returncode,
                tail=list(tail),
                hint=hint,
            )

        if returncode != 0 and check:
            raise StageError(
                "command failed with exit code {}".format(returncode),
                argv=argv,
                cwd=cwd,
                returncode=returncode,
                tail=list(tail),
                hint=hint,
            )

        return CommandResult(
            argv=argv,
            cwd=cwd,
            returncode=returncode,
            log_path=log_path,
        )

    def run_capture(
        self,
        argv: Sequence[str],
        cwd: Optional[Path] = None,
        timeout_s: Optional[float] = None,
        check: bool = True,
    ) -> str:
        """Run ``argv`` and return combined stdout+stderr, raising on failure.

        The two streams are concatenated with stdout first.  Some tools (e.g.
        real ``gmx check``) write their diagnostics to stderr, so callers that
        parse the output must see both.

        Unlike :meth:`run`, output is not written to a log file.
        """
        argv = [str(a) for a in argv]
        cwd_obj = Path(cwd) if cwd is not None else Path.cwd()
        timeout = timeout_s if timeout_s is not None else self.timeout_s

        try:
            proc = subprocess.run(
                argv,
                cwd=str(cwd_obj),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            output = exc.output or ""
            stderr = exc.stderr or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            combined = output + stderr
            raise StageError(
                "command timed out after {}s".format(timeout),
                argv=argv,
                cwd=cwd_obj,
                returncode=-1,
                tail=combined.splitlines()[-TAIL_LINES:],
            ) from exc

        if proc.returncode != 0 and check:
            combined = (proc.stdout or "") + (proc.stderr or "")
            raise StageError(
                "command failed with exit code {}".format(proc.returncode),
                argv=argv,
                cwd=cwd_obj,
                returncode=proc.returncode,
                tail=combined.splitlines()[-TAIL_LINES:],
            )

        return (proc.stdout or "") + (proc.stderr or "")

    def which(self, exe: str) -> Optional[str]:
        """Return the path to ``exe``, or ``None`` if it is not on PATH."""

        return shutil.which(exe)
