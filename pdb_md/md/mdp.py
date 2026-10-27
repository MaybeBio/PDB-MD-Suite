"""GROMACS ``.mdp`` file parsing and per-stage validation.

An ``.mdp`` file is a key/value text format with a few quirks we handle here:

* ``#include`` lines are directives, not settings, and are ignored.
* Everything after a ``;`` is a comment.
* When a key appears more than once, the last occurrence wins.
* Key names are case-insensitive and normalised to lowercase.
"""

import re
from pathlib import Path

from pdb_md.md.errors import ConfigError

# Required keys per pipeline stage. The order is the order they are reported in
# when several are missing at once.
_REQUIRED_KEYS = {
    "em": ("integrator", "nsteps", "emtol", "emstep"),
    "nvt": ("integrator", "nsteps", "dt", "gen_vel", "gen_seed", "define"),
    "npt": ("integrator", "nsteps", "dt", "continuation", "define"),
    "prod": ("integrator", "nsteps", "dt"),
}


def parse_mdp(text: str) -> dict[str, str]:
    """Parse ``.mdp`` text into a ``{key: value}`` mapping.

    ``#include`` lines are dropped, ``;`` starts a comment, keys are lowercased,
    and the last occurrence of a key wins.
    """
    result: dict[str, str] = {}
    for line in text.splitlines():
        # Strip the trailing comment first, then surrounding whitespace.
        body = line.split(";", 1)[0].strip()
        if not body:
            continue
        if body.startswith("#include"):
            continue
        if "=" not in body:
            continue
        key, _, value = body.partition("=")
        result[key.strip().lower()] = value.strip()
    return result


def read_mdp(path: Path) -> dict[str, str]:
    """Read and parse the ``.mdp`` file at ``path``."""
    return parse_mdp(Path(path).read_text())


def check_mdp(path: Path, stage: str) -> dict[str, str]:
    """Validate the ``.mdp`` file at ``path`` for ``stage``.

    Raises :class:`ConfigError` when a required key is missing (all missing keys
    are listed at once) or when a stage-specific semantic check fails. Returns
    the parsed mapping on success.
    """
    path = Path(path)
    parsed = read_mdp(path)

    try:
        required = _REQUIRED_KEYS[stage]
    except KeyError:
        raise ConfigError(
            "{}: unknown stage {!r} (expected one of {})".format(
                path.name, stage, ", ".join(sorted(_REQUIRED_KEYS))
            )
        )

    missing = [key for key in required if key not in parsed]
    if missing:
        raise ConfigError(
            "{}: missing required key(s) for stage {!r}: {}".format(
                path.name, stage, ", ".join(missing)
            )
        )

    # integrator must never be empty, for any stage.
    if not parsed["integrator"]:
        raise ConfigError(
            "{}: 'integrator' must not be empty".format(path.name)
        )

    if stage == "nvt":
        if parsed["gen_vel"].lower() != "yes":
            raise ConfigError(
                "{}: 'gen_vel' must be 'yes' for stage 'nvt'".format(path.name)
            )
        if "-DPOSRES" not in parsed["define"]:
            raise ConfigError(
                "{}: 'define' must contain '-DPOSRES' for stage 'nvt'".format(path.name)
            )
    elif stage == "npt":
        if parsed["continuation"].lower() != "yes":
            raise ConfigError(
                "{}: 'continuation' must be 'yes' for stage 'npt'".format(path.name)
            )
        if "-DPOSRES" not in parsed["define"]:
            raise ConfigError(
                "{}: 'define' must contain '-DPOSRES' for stage 'npt'".format(path.name)
            )

    return parsed


def replace_key(text: str, key: str, value: str) -> str:
    """Replace the value of ``key`` in ``text``, returning the new text.

    The key must occur exactly once; otherwise a :class:`ConfigError` is raised
    naming the key.
    """
    pattern = r"(?m)^(\s*" + re.escape(key) + r"\s*=\s*).*$"
    new_text, count = re.subn(pattern, lambda m: m.group(1) + value, text)
    if count != 1:
        raise ConfigError(
            "expected exactly one occurrence of {!r} in mdp, found {}".format(key, count)
        )
    return new_text
