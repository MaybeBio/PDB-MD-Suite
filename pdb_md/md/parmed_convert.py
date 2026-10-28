"""Convert an AMBER ``prmtop``/``inpcrd`` pair to GROMACS ``.top``/``.gro``.

ParmEd is imported inside :func:`main` only.  This module is executed by the
interpreter named in ``tools.parmed_python`` (the one that has ParmEd), but it
is also imported by the ``topology`` stage (which runs under the pipeline
interpreter) to locate the script, so a module-level ParmEd import would break
that interpreter.

After conversion, the topology is post-processed for GROMACS 2020+:

* ParmEd writes a ``[ pairs ]`` section, but recent ``grompp`` rejects the
  1-4 pair list that carries no parameters; it must be named ``[ pairs_nb ]``.
* ParmEd can emit duplicate ``[ atomtypes ]`` rows (one per source molecule);
  ``grompp`` refuses duplicate atom type definitions, so only the first row
  for each atom type name is kept.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional

_SECTION_RE = re.compile(r"^\s*\[\s*([A-Za-z_]+)\s*\]")


def postprocess_top_text(text: str) -> str:
    """Make a ParmEd GROMACS topology acceptable to ``grompp``.

    Renames ``[ pairs ]`` to ``[ pairs_nb ]`` (header matched
    case/whitespace-insensitively) and drops duplicate ``[ atomtypes ]`` rows,
    keyed by their first column, keeping the first occurrence.
    """
    out: List[str] = []
    seen_atomtypes = set()
    in_atomtypes = False

    for line in text.splitlines():
        header = _SECTION_RE.match(line)
        if header:
            section = header.group(1).lower()
            if section == "pairs":
                out.append("[ pairs_nb ]")
                in_atomtypes = False
                continue
            in_atomtypes = section == "atomtypes"
            out.append(line)
            continue

        if line.lstrip().startswith("#"):
            # Preprocessor directives do not open or close a section.
            out.append(line)
            continue

        content = line.split(";", 1)[0].strip()
        if in_atomtypes and content:
            name = content.split()[0]
            if name in seen_atomtypes:
                continue
            seen_atomtypes.add(name)
        out.append(line)

    result = "\n".join(out)
    if text.endswith("\n"):
        result += "\n"
    return result


def _save(parm, path: Path, fmt: str) -> None:
    """Save ``parm`` as ``path``, probing the ParmEd API for the format kwarg."""
    try:
        parm.save(str(path))
    except Exception:
        # Older/newer ParmEd releases may not infer the format from the
        # extension, so retry with an explicit one.
        parm.save(str(path), format=fmt)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert an AMBER prmtop/inpcrd pair to GROMACS .top/.gro."
    )
    parser.add_argument("--prmtop", required=True)
    parser.add_argument("--inpcrd", required=True)
    parser.add_argument("--top", required=True)
    parser.add_argument("--gro", required=True)
    args = parser.parse_args(argv)

    try:
        import parmed
    except Exception as exc:  # ImportError, or a broken ParmEd install
        print(
            "parmed_convert: cannot import ParmEd with this interpreter: "
            "{}".format(exc),
            file=sys.stderr,
        )
        return 1

    top_path = Path(args.top)
    gro_path = Path(args.gro)
    try:
        parm = parmed.load_file(args.prmtop, args.inpcrd)
        _save(parm, top_path, "gromacs")
        _save(parm, gro_path, "gro")
    except Exception as exc:
        print(
            "parmed_convert: conversion failed: {}".format(exc), file=sys.stderr
        )
        return 1

    try:
        top_path.write_text(
            postprocess_top_text(top_path.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
    except OSError as exc:
        print(
            "parmed_convert: cannot post-process {}: {}".format(top_path, exc),
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
