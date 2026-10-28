"""GROMACS ``.ndx`` index generation and parsing.

The ``pbc`` stage drives ``trjconv`` non-interactively and therefore has to
name its groups by index rather than by picking them at a prompt.  The groups
are built from the system ``.gro`` (whose atoms are already in system order)
and a :class:`~pdb_md.md.config.SpeciesConfig` that decides which residue
names are DNA, metal or solvent.

Classification is intentionally conservative: anything not recognised as DNA,
metal or solvent is treated as protein, so a complex of protein plus DNA plus
zinc still lands in one ``Complex`` group while bulk solvent stays out of it.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pdb_md.md.config import SpeciesConfig
from pdb_md.md.errors import PreflightError
from pdb_md.md.gromacs import GroFile

#: Fixed group emission order; later stages resolve names against file order.
GROUP_ORDER: Tuple[str, ...] = ("System", "Protein", "DNA", "Metal", "Complex")

#: GROMACS convention: index lines wrap after this many atom numbers.
ATOMS_PER_LINE = 15

#: ``[ group_name ]`` header, tolerating interior whitespace.
_HEADER_RE = re.compile(r"^\[\s*(\S+)\s*\]")


def build_groups(gro: GroFile, species: SpeciesConfig) -> Dict[str, List[int]]:
    """Classify every atom of ``gro`` into the five pipeline groups.

    Residue names are compared case-insensitively.  Each atom is assigned in
    priority order DNA, metal, solvent; everything else is protein.  Solvent
    atoms appear only in ``System``.  ``Complex`` is the sorted union of the
    protein, DNA and metal atom numbers so that it always follows the system
    order (GROMACS groups need not be sorted, but keeping them so makes files
    and tests easy to compare).
    """
    dna_resnames = {name.upper() for name in species.dna_resnames}
    metal_resnames = {name.upper() for name in species.metal_resnames}
    solvent_resnames = {name.upper() for name in species.solvent_resnames}

    protein: List[int] = []
    dna: List[int] = []
    metal: List[int] = []
    for atom in gro.atoms:
        resname = atom.resname.upper()
        if resname in dna_resnames:
            dna.append(atom.index)
        elif resname in metal_resnames:
            metal.append(atom.index)
        elif resname in solvent_resnames:
            continue
        else:
            protein.append(atom.index)

    return {
        "System": list(range(1, len(gro.atoms) + 1)),
        "Protein": protein,
        "DNA": dna,
        "Metal": metal,
        "Complex": sorted(protein + dna + metal),
    }


def write_ndx(groups: Dict[str, List[int]], path: Path) -> None:
    """Write ``groups`` as a GROMACS ``.ndx`` file in :data:`GROUP_ORDER`.

    Empty groups still emit their header (harmless, and
    :func:`read_ndx` reads them back as empty lists).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    for name in GROUP_ORDER:
        lines.append("[ {} ]".format(name))
        atoms = groups[name]
        for start in range(0, len(atoms), ATOMS_PER_LINE):
            chunk = atoms[start : start + ATOMS_PER_LINE]
            lines.append(" ".join(str(number) for number in chunk))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_ndx(path: Path) -> Dict[str, List[int]]:
    """Parse a GROMACS ``.ndx`` file, preserving the on-disk group order.

    Blank lines are ignored.  A repeated header extends the existing group
    rather than replacing it, which matches how GROMACS concatenates chunks.
    """
    groups: Dict[str, List[int]] = {}
    current: Optional[List[int]] = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        header = _HEADER_RE.match(line)
        if header:
            current = groups.setdefault(header.group(1), [])
            continue
        if current is None:
            raise PreflightError(
                "{}: atom list appears before the first group header".format(path)
            )
        current.extend(int(token) for token in line.split())
    return groups


def resolve_group(path: Path, name: str) -> Tuple[int, List[int]]:
    """Return ``(0-based index in file order, atom numbers)`` for ``name``.

    ``trjconv`` selects groups by their position in the index file, so the
    index must reflect the parsed order rather than :data:`GROUP_ORDER`.
    A missing group is a valid configuration meeting an unexpected input, so
    it raises :class:`PreflightError` (exit code 3) listing what is available.
    """
    groups = read_ndx(path)
    names = list(groups)
    try:
        index = names.index(name)
    except ValueError:
        raise PreflightError(
            "group {!r} not found in {}; available: {}".format(
                name, path, ", ".join(names) if names else "(none)"
            )
        )
    return index, groups[name]
