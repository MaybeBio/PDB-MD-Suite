"""Exception hierarchy for the ``pdb-md md`` pipeline.

Exit codes are load-bearing and consumed by the CLI:

* 0 - success
* 1 - stage failure (an external tool failed)
* 2 - configuration error (bad user input/config file)
* 3 - preflight failure (environment prerequisite missing)
"""

from pathlib import Path
from typing import Optional, Sequence


class MdError(Exception):
    """Base class for all pipeline errors.

    ``render`` is the user-facing representation; subclasses may override it.
    """

    exit_code: int = 1

    def __init__(self, message: str, hint: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.hint = hint

    def render(self) -> str:
        text = self.message
        if self.hint:
            text += "\nHint: " + self.hint
        return text


class ConfigError(MdError):
    """Invalid user configuration (exit code 2)."""

    exit_code = 2


class PreflightError(MdError):
    """A required environment prerequisite is missing (exit code 3)."""

    exit_code = 3


class StageError(MdError):
    """An external command failed (exit code 1).

    Carries everything needed to debug a failed subprocess: the command line,
    working directory, exit code, and the tail of the merged output.
    """

    exit_code = 1

    def __init__(
        self,
        message: str,
        argv: Sequence[str],
        cwd: Optional[Path],
        returncode: int,
        tail: Sequence[str],
        hint: Optional[str] = None,
    ):
        super().__init__(message, hint)
        self.argv = [str(a) for a in argv]
        self.cwd = Path(cwd) if cwd is not None else Path.cwd()
        self.returncode = int(returncode)
        self.tail = [str(line) for line in tail]

    def __str__(self) -> str:
        # Local import keeps errors.py free of a module-level dependency on the
        # subprocess machinery while reusing its canonical quoting helper.
        from .runner import shell_join

        lines = [
            self.message,
            "Command: " + shell_join(self.argv),
            "  cwd: {}".format(self.cwd),
            "  exit code: {}".format(self.returncode),
        ]
        if self.hint:
            lines.append("Hint: " + self.hint)
        if self.tail:
            lines.append("Last {} line(s) of output:".format(len(self.tail)))
            lines.extend("  " + line for line in self.tail)
        return "\n".join(lines)
