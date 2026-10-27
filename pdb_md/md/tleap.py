"""LEaP script rendering, SPLIT ion-count arithmetic and prmtop/leap.log parsing.

Two ``tleap`` passes build the AMBER topology.  Pass 1 loads the ZAFF-prepared
structure, makes the explicit Zn-ligand bonds, and solvates the box.  Pass 2
reloads that solvated topology and adds the neutralizing/salting ions computed
by :func:`compute_split_counts`.  Splitting the run lets the water count (and
therefore the ion count) be read from the pass-1 ``leap.log`` instead of
guessed from the structure.

All script paths are written absolute where a real filesystem path is expected
(``loadpdb``), because ``tleap`` is executed from the ``01_zaff/`` stage
directory.  AMBER system names (``source``/``loadAmberParams``/atom types) are
written verbatim from the configuration.
"""

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .config import RunConfig
from .coords import StructureTable
from .errors import ConfigError
from .zinc import SiteCheck


@dataclass(frozen=True)
class SplitCounts:
    """Ion counts for one ``addionsrand`` call (SPLIT-style)."""

    no: float
    counter: int
    coion: int
    counter_name: str
    coion_name: str


@dataclass(frozen=True)
class LeapLogInfo:
    """Values scraped from ``leap.log``; each field is ``None`` if absent."""

    water_count: Optional[int]
    net_charge: Optional[int]
    volume_A3: Optional[float]
    density: Optional[float]


def _round_half_up(value: float) -> int:
    """Round half away from zero-at-the-.5 boundary (``floor(x + 0.5)``)."""
    return int(math.floor(value + 0.5))


def compute_split_counts(
    water_count: int,
    net_charge: int,
    concentration_M: float,
    cation: str,
    anion: str,
) -> SplitCounts:
    """Compute how many counter-ions and co-ions to add in pass 2.

    ``no`` is the ideal number of salt formula units for the requested molarity
    (56 waters per mole under this convention).  Half the absolute net charge
    is added to the counter-ion count and subtracted from the co-ion count;
    negative co-ion counts mean the target concentration cannot be reached and
    raise :class:`ConfigError`.
    """
    no = water_count * concentration_M / 56.0
    half_charge = abs(net_charge) / 2.0
    counter = _round_half_up(no + half_charge)
    coion = _round_half_up(no - half_charge)

    if coion < 0:
        raise ConfigError(
            "cannot reach {:.4g} M salt: the system charge {} would require "
            "a negative coion count ({})".format(
                concentration_M, net_charge, coion
            ),
            hint="lower system.salt.concentration_M or check the net charge",
        )

    if net_charge > 0:
        # A positive system needs anions to neutralize it, so the anion is the
        # counter-ion and the cation is the co-ion.
        counter_name, coion_name = anion, cation
    else:
        counter_name, coion_name = cation, anion

    return SplitCounts(
        no=no,
        counter=counter,
        coion=coion,
        counter_name=counter_name,
        coion_name=coion_name,
    )


def _header_lines(cfg: RunConfig) -> List[str]:
    ff = cfg.forcefield
    return [
        "source {}".format(ff.protein),
        "source {}".format(ff.nucleic),
        "source {}".format(ff.water),
        "loadAmberPrep {}".format(ff.zaff_prep),
        "loadAmberParams {}".format(ff.zaff_frcmod),
        "loadAmberParams {}".format(ff.ions_frcmod),
        ff.atom_types,
    ]


def render_pass1_script(
    cfg: RunConfig,
    table: StructureTable,
    sites: Sequence[SiteCheck],
    prefix: str,
) -> str:
    """Render the first ``tleap`` script (dry complex -> solvated box).

    ``table`` is accepted for future atom-name lookups but is not needed to
    render bonds: bond positions come from the resolved :class:`SiteCheck`.
    """
    lines = _header_lines(cfg)
    lines.append("mol = loadpdb {}".format(cfg.path(cfg.input.structure)))

    for site in sites:
        for ligand in site.ligands:
            lines.append(
                "bond mol.{}.ZN mol.{}.{}".format(
                    site.zn_position, ligand.position, ligand.ref.atom
                )
            )

    lines.extend(
        [
            "charge mol",
            "check mol",
            "saveamberparm mol {p}_dry.prmtop {p}_dry.inpcrd".format(p=prefix),
            "savepdb mol {p}_dry.pdb".format(p=prefix),
            "solvateBox mol {} {}".format(
                cfg.system.solvate.box, cfg.system.solvate.buffer_angstrom
            ),
            "charge mol",
            "check mol",
            "saveamberparm mol {p}_solv.prmtop {p}_solv.inpcrd".format(p=prefix),
            "savepdb mol {p}_solv.pdb".format(p=prefix),
            "quit",
        ]
    )
    return "\n".join(lines) + "\n"


def render_pass2_script(
    cfg: RunConfig, counts: SplitCounts, prefix: str
) -> str:
    """Render the second ``tleap`` script (add SPLIT ions, re-save).

    Deliberately contains no ``solvateBox``: the topology is already solvated.
    """
    lines = _header_lines(cfg)
    lines.extend(
        [
            "mol = loadamberparm {p}_solv.prmtop {p}_solv.inpcrd".format(p=prefix),
            "charge mol",
            "check mol",
            "addionsrand mol {} {} {} {}".format(
                counts.counter_name,
                counts.counter,
                counts.coion_name,
                counts.coion,
            ),
            "charge mol",
            "check mol",
            "saveamberparm mol {p}_solv.prmtop {p}_solv.inpcrd".format(p=prefix),
            "savepdb mol {p}_solv.pdb".format(p=prefix),
            "quit",
        ]
    )
    return "\n".join(lines) + "\n"


_ADDED_RESIDUES = re.compile(r"Added\s+(\d+)\s+residues")
_WATER_RESIDUES = re.compile(r"(\d+)\s+(?:WAT|HOH|SOL)\s+residues")
_CHARGE_TOTAL = re.compile(
    r"Total unperturbed charge:\s*(-?\d+(?:\.\d+)?)"
)
_CHARGE_UNIT = re.compile(
    r"unperturbed charge of the unit:\s*(-?\d+(?:\.\d+)?)"
)
_VOLUME_PAREN = re.compile(r"Volume:\s*([\d.]+)\s*\(A\^3\)")
_VOLUME_PLAIN = re.compile(r"Volume:\s*([\d.]+)\s*A\^3")
_DENSITY = re.compile(r"Density:\s*([\d.]+)")


def _last_float(pattern: "re.Pattern[str]", text: str) -> Optional[float]:
    matches = pattern.findall(text)
    if not matches:
        return None
    return float(matches[-1])


def _last_int(pattern: "re.Pattern[str]", text: str) -> Optional[int]:
    matches = pattern.findall(text)
    if not matches:
        return None
    return int(matches[-1])


def parse_leap_log(text: str) -> LeapLogInfo:
    """Scrape water count, charge, volume and density from a ``leap.log``.

    Several historical ``tleap`` message formats are accepted; any value that
    cannot be found is returned as ``None`` rather than raising.
    """
    water_count = _last_int(_ADDED_RESIDUES, text)
    if water_count is None:
        water_count = _last_int(_WATER_RESIDUES, text)

    net_charge: Optional[int] = None
    for pattern in (_CHARGE_TOTAL, _CHARGE_UNIT):
        matches = pattern.findall(text)
        if matches:
            # Charge appears as e.g. "-34.000000"; truncate to match the
            # integer charge the topology actually carries.
            net_charge = int(float(matches[-1]))
            break

    volume: Optional[float] = None
    for pattern in (_VOLUME_PAREN, _VOLUME_PLAIN):
        volume = _last_float(pattern, text)
        if volume is not None:
            break

    density = _last_float(_DENSITY, text)

    return LeapLogInfo(
        water_count=water_count,
        net_charge=net_charge,
        volume_A3=volume,
        density=density,
    )


_FLAG_LINE = re.compile(r"^%FLAG\s+(\S+)\s*$")
_FORMAT_LINE = re.compile(r"^%FORMAT")


def _read_sections(path: Path) -> Dict[str, List[str]]:
    """Split a prmtop into ``{flag: [data lines]}``.

    Each section's data starts after its ``%FORMAT`` line and runs until the
    next ``%FLAG`` line.  Lines are returned raw (trailing newline removed) so
    fixed-width fields such as ``ATOM_NAME`` survive intact.
    """
    sections: Dict[str, List[str]] = {}
    current: Optional[List[str]] = None
    for raw in Path(path).read_text().splitlines():
        flag = _FLAG_LINE.match(raw)
        if flag:
            current = []
            sections[flag.group(1)] = current
            continue
        if current is None or _FORMAT_LINE.match(raw):
            continue
        current.append(raw)
    return sections


def count_prmtop_atoms(path: Path) -> int:
    """Return ``NATOM`` (the first ``%FLAG POINTERS`` integer)."""
    sections = _read_sections(path)
    data = sections.get("POINTERS")
    if not data:
        raise ValueError("prmtop has no %FLAG POINTERS section: {}".format(path))
    for line in data:
        fields = line.split()
        if fields:
            return int(fields[0])
    raise ValueError("prmtop %FLAG POINTERS section is empty: {}".format(path))


def prmtop_residue_atoms(path: Path) -> List[List[str]]:
    """Return each residue's atom names in prmtop (and therefore LEaP) order."""
    sections = _read_sections(path)
    atom_lines = sections.get("ATOM_NAME")
    pointer_lines = sections.get("RESIDUE_POINTER")
    if atom_lines is None:
        raise ValueError("prmtop has no %FLAG ATOM_NAME section: {}".format(path))
    if pointer_lines is None:
        raise ValueError(
            "prmtop has no %FLAG RESIDUE_POINTER section: {}".format(path)
        )

    atom_names: List[str] = []
    for line in atom_lines:
        if not line:
            continue
        for start in range(0, len(line), 4):
            name = line[start : start + 4].strip()
            if name:
                atom_names.append(name)
    natom = len(atom_names)

    pointers = [int(value) for line in pointer_lines for value in line.split()]
    residues: List[List[str]] = []
    for index, start in enumerate(pointers):
        start0 = start - 1
        if index + 1 < len(pointers):
            end0 = pointers[index + 1] - 1
        else:
            end0 = natom
        residues.append(atom_names[start0:end0])
    return residues
