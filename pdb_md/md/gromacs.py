"""GROMACS ``.gro`` / ``.top`` parsers and the atom-count helper.

The ``topology`` stage consumes the ParmEd conversion of the AMBER topology:
``conf.gro`` supplies the atom names/residues in system order (used to verify
the LEaP ``position`` -> system atom-number mapping) and ``topol.top`` supplies
the moleculetypes, their atom counts and the ``[ molecules ]`` multiplicities.

Both formats are fixed-column/whitespace hybrids, so ``.gro`` atom lines are
sliced by column while ``.top`` sections are driven by an explicit state
machine: rows are only interpreted once their own section header has been seen,
so ``[ atomtypes ]`` rows before the first ``[ moleculetype ]`` are never
mistaken for a moleculetype name line.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

#: ``[ section_name ]`` header, tolerating interior whitespace and case.
_SECTION_RE = re.compile(r"^\s*\[\s*([A-Za-z_]+)\s*\]")


@dataclass(frozen=True)
class GroAtom:
    """One ``.gro`` atom line (coordinates are deliberately not retained)."""

    index: int      # 1-based atom number from columns 16-20
    resid: int      # residue number from columns 1-5
    resname: str    # residue name from columns 6-10
    name: str       # atom name from columns 11-15


@dataclass(frozen=True)
class GroFile:
    atoms: List[GroAtom]
    box: Tuple[float, ...]


@dataclass(frozen=True)
class MTAtom:
    """One ``[ atoms ]`` row of a moleculetype."""

    nr: int
    atype: str
    resnr: int
    resname: str
    name: str


@dataclass(frozen=True)
class Moleculetype:
    name: str
    atoms: List[MTAtom]


@dataclass(frozen=True)
class Topology:
    moleculetypes: List[Moleculetype]
    molecules: List[Tuple[str, int]]


def read_gro(path: Path) -> GroFile:
    """Parse a GROMACS ``.gro`` file.

    Atom lines are sliced by fixed columns because ``resid`` and ``resname``
    (and ``resname``/``name``) are run together without a delimiter.  Only the
    header count, the atom lines and the trailing box vector are needed.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if len(lines) < 2:
        raise ValueError("gro file is too short: {}".format(path))
    try:
        n_atoms = int(lines[1].strip())
    except ValueError:
        raise ValueError(
            "gro file has no atom count on line 2: {}".format(path)
        )

    atoms: List[GroAtom] = []
    for line in lines[2 : 2 + n_atoms]:
        if len(line) < 20:
            raise ValueError(
                "gro atom line is too short (need 20 columns): {!r}".format(line)
            )
        atoms.append(
            GroAtom(
                index=int(line[15:20].strip()),
                resid=int(line[0:5].strip()),
                resname=line[5:10].strip(),
                name=line[10:15].strip(),
            )
        )

    box: Tuple[float, ...] = ()
    box_index = 2 + n_atoms
    if box_index < len(lines):
        box = tuple(float(value) for value in lines[box_index].split())
    return GroFile(atoms=atoms, box=box)


def read_top(path: Path) -> Topology:
    """Parse the moleculetype and molecule sections of a GROMACS topology.

    ``[ atomtypes ]`` and every parameter section are ignored, so the only rows
    interpreted are those inside the section currently open.  A moleculetype
    name is the first data row after ``[ moleculetype ]``; an ``[ atoms ]`` row
    contributes its first five fields.
    """
    moleculetypes: List[Moleculetype] = []
    molecules: List[Tuple[str, int]] = []
    mode = ""
    current_name = None
    current_atoms: List[MTAtom] = []

    def flush_moleculetype() -> None:
        nonlocal current_name, current_atoms
        if current_name is not None:
            moleculetypes.append(Moleculetype(current_name, current_atoms))
        current_name = None
        current_atoms = []

    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line or line.startswith("#"):
            continue

        header = _SECTION_RE.match(line)
        if header:
            section = header.group(1).lower()
            # Only the start of the *next* moleculetype closes the current one;
            # intermediate sections ([ atoms ], [ bonds ], ...) belong to it.
            if section == "moleculetype":
                flush_moleculetype()
            mode = section
            continue

        if mode == "moleculetype":
            if current_name is None:
                current_name = line.split()[0]
        elif mode == "atoms" and current_name is not None:
            parts = line.split()
            if len(parts) < 5:
                raise ValueError(
                    "malformed [ atoms ] row: {!r}".format(raw)
                )
            current_atoms.append(
                MTAtom(
                    nr=int(parts[0]),
                    atype=parts[1],
                    resnr=int(parts[2]),
                    resname=parts[3],
                    name=parts[4],
                )
            )
        elif mode == "molecules":
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(
                    "malformed [ molecules ] row: {!r}".format(raw)
                )
            molecules.append((parts[0], int(parts[1])))

    flush_moleculetype()
    return Topology(moleculetypes=moleculetypes, molecules=molecules)


def total_atoms(topology: Topology) -> int:
    """Return the number of atoms in the composed system.

    Each ``[ molecules ]`` entry expands its moleculetype ``count`` times.
    """
    by_name: Dict[str, Moleculetype] = {
        mt.name: mt for mt in topology.moleculetypes
    }
    total = 0
    for name, count in topology.molecules:
        try:
            mt = by_name[name]
        except KeyError:
            raise ValueError(
                "molecules entry {!r} has no matching moleculetype".format(name)
            )
        total += count * len(mt.atoms)
    return total
