"""Fixed-column PDB parsing and LEaP residue-position mapping.

The MD pipeline refers to residues by ``chain``/``resid`` in YAML, but the
AMBER toolchain (``tleap``) indexes residues by the order in which ``loadpdb``
sees them in the PDB file.  :class:`ResidueRecord.position` bridges the two:
it is the 1-based residue order in the file (which is also the order LEaP
assigns), independent of the PDB residue numbers.

Only the first ``MODEL`` of a multi-model file is read.  Records other than
``ATOM``/``HETATM`` are ignored, with the exception of ``TER`` (recorded so the
Zn-site check can verify the metal is isolated from its neighbours).
"""

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .errors import ConfigError, PreflightError

# ``^\d+[A-Za-z]?$`` for the whitespace-token fallback path, where the residue
# number and insertion code arrive glued together (e.g. "365A").
_RESID_TOKEN = re.compile(r"^(-?\d+)([A-Za-z]?)$")


@dataclass(frozen=True)
class AtomRecord:
    atom_index: int          # 1-based, 文件顺序
    serial: int
    name: str
    resname: str
    chain: str
    resid: int
    icode: str
    element: str
    xyz: tuple[float, float, float]


@dataclass
class ResidueRecord:
    chain: str
    resid: int
    icode: str
    resname: str
    position: int            # 1-based, loadpdb 后的残基顺序（含所有残基）
    atoms: dict[str, AtomRecord] = field(default_factory=dict)
    ter_after: bool = False


@dataclass
class StructureTable:
    residues: list[ResidueRecord]
    atoms: list[AtomRecord]
    has_ter: bool
    resname_overflow: bool   # 是否存在 [17:21].strip() 长度 > 3 的残基名（固定列溢出）

    def find(self, chain: str, resid: int) -> list[ResidueRecord]:
        """All residues matching ``chain`` and ``resid`` (insertion codes kept)."""
        return [r for r in self.residues if r.chain == chain and r.resid == resid]

    def locate(self, chain: str, resid: int) -> ResidueRecord:
        """Return the unique residue for ``chain``/``resid``.

        A missing residue or several residues sharing the number but differing
        in insertion code both mean the configuration does not match this
        structure, so they raise :class:`PreflightError` (exit code 3) rather
        than a configuration error.
        """
        hits = self.find(chain, resid)
        if len(hits) == 1:
            return hits[0]
        if not hits:
            in_chain = [r for r in self.residues if r.chain == chain]
            if in_chain:
                candidates = ", ".join(
                    "{} {}{} (position {})".format(
                        r.resname, r.resid, r.icode, r.position
                    )
                    for r in in_chain
                )
                message = (
                    "residue {}:{} not found in structure; candidates in chain {}: {}"
                ).format(chain, resid, chain, candidates)
            else:
                chains = sorted({r.chain for r in self.residues})
                message = (
                    "residue {}:{} not found in structure; chain {} has no "
                    "residues (chains present: {})"
                ).format(chain, resid, chain, ", ".join(chains) or "none")
            raise PreflightError(message)
        candidates = ", ".join(
            "{} {}:{}{} (position {})".format(
                r.resname, r.chain, r.resid, r.icode, r.position
            )
            for r in hits
        )
        message = (
            "residue {}:{} matches {} residues in structure; insertion code must "
            "be specified: {}"
        ).format(chain, resid, len(hits), candidates)
        raise PreflightError(
            message,
            hint="PDB insertion codes (column 27) are not part of a ResidueRef; "
            "rename or renumber one of the residues.",
        )

    def atom(self, ref: Any) -> AtomRecord:
        """Look up an atom from a ``ResidueRef``-like object.

        ``ref`` must expose ``chain``, ``resid`` and ``atom``; ``resname`` is
        checked case-insensitively when present.
        """
        residue = self.locate(ref.chain, ref.resid)
        expected = getattr(ref, "resname", None)
        if expected is not None and residue.resname.upper() != str(expected).upper():
            raise PreflightError(
                "resname mismatch for {}:{}: structure has {!r} but reference "
                "says {!r}".format(
                    ref.chain, ref.resid, residue.resname, expected
                )
            )
        key = str(ref.atom).upper()
        atom = residue.atoms.get(key)
        if atom is None:
            available = ", ".join(sorted(residue.atoms)) or "none"
            raise PreflightError(
                "atom {!r} not found in residue {}:{}{} (resname {}, position "
                "{}); available atoms: {}".format(
                    ref.atom,
                    ref.chain,
                    ref.resid,
                    residue.icode,
                    residue.resname,
                    residue.position,
                    available,
                )
            )
        return atom

    def distance(self, a: AtomRecord, b: AtomRecord) -> float:
        """Euclidean distance in angstrom between two atom coordinates."""
        return math.dist(a.xyz, b.xyz)


def _parse_atom_line(line: str) -> tuple[dict, bool]:
    """Parse one ATOM/HETATM record.

    Returns ``(fields, used_fallback)``.  Fixed columns are authoritative; a
    handful of tools emit slightly misaligned ATOM/HETATM lines (an extra space
    before the residue name), so when the fixed-column fields are not usable
    the record is re-parsed by whitespace tokens instead of being rejected.
    """
    try:
        serial = int(line[6:11])
        resid = int(line[22:26])
        x = float(line[30:38])
        y = float(line[38:46])
        z = float(line[46:54])
    except ValueError:
        return _parse_atom_line_by_tokens(line), True

    return (
        {
            "serial": serial,
            "name": line[12:16].strip(),
            "resname": line[17:20].strip(),
            "chain": line[21:22].strip(),
            "resid": resid,
            "icode": line[26:27].strip(),
            "element": line[76:78].strip() if len(line) >= 78 else "",
            "xyz": (x, y, z),
        },
        False,
    )


def _parse_atom_line_by_tokens(line: str) -> dict:
    tokens = line.split()
    # record serial name resname chain resid x y z [occ bfactor element]
    if len(tokens) < 9:
        raise PreflightError(
            "cannot parse ATOM/HETATM record (too few fields): {!r}".format(line)
        )
    try:
        serial = int(tokens[1])
        x = float(tokens[6])
        y = float(tokens[7])
        z = float(tokens[8])
    except ValueError:
        raise PreflightError(
            "cannot parse ATOM/HETATM record (bad serial or coordinates): {!r}".format(
                line
            )
        )
    match = _RESID_TOKEN.match(tokens[5])
    if match is None:
        raise PreflightError(
            "cannot parse residue number/insertion code {!r}: {!r}".format(
                tokens[5], line
            )
        )
    element = ""
    if len(tokens) >= 12 and tokens[-1].isalpha() and len(tokens[-1]) <= 2:
        element = tokens[-1]
    return {
        "serial": serial,
        "name": tokens[2],
        "resname": tokens[3],
        "chain": tokens[4],
        "resid": int(match.group(1)),
        "icode": match.group(2),
        "element": element,
        "xyz": (x, y, z),
    }


def _detect_resname_overflow(line: str, fields: dict, used_fallback: bool) -> bool:
    """Whether the residue name spills out of its 3-column field.

    Well-aligned records are checked exactly as specified: the 4-column slice
    ``[17:21]`` must reduce to the same text as the 3-column ``[17:20]``.  A
    4-character name packed one column early (``[16:20]``, as some tools write
    it) also counts.  For records that needed the whitespace fallback the
    token-derived name is checked instead, since the fixed columns are known to
    be unreliable on that line.
    """
    if used_fallback:
        return len(fields["resname"]) > 3
    if line[17:21].strip() != line[17:20].strip():
        return True
    return len(line[16:21].strip()) > 3


def read_pdb(path: Path) -> StructureTable:
    """Read the first model of a PDB file into a :class:`StructureTable`."""
    path = Path(path)
    if path.suffix.lower() != ".pdb":
        raise ConfigError(
            "convert to PDB first: {!r} is not a .pdb file (suffix {!r}); the "
            "MD pipeline reads PDB only".format(str(path), path.suffix)
        )

    residues: list[ResidueRecord] = []
    atoms: list[AtomRecord] = []
    has_ter = False
    resname_overflow = False

    model_seen = False
    current_key: Optional[tuple[str, int, str, str]] = None
    pending_break = True

    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        record = line[:6].strip()

        if record == "MODEL":
            if model_seen:
                break
            model_seen = True
            current_key = None
            pending_break = True
            continue
        if record == "ENDMDL":
            current_key = None
            pending_break = True
            continue
        if record == "TER":
            has_ter = True
            if residues and not pending_break:
                residues[-1].ter_after = True
            current_key = None
            pending_break = True
            continue
        if record not in ("ATOM", "HETATM"):
            continue

        fields, used_fallback = _parse_atom_line(line)
        if _detect_resname_overflow(line, fields, used_fallback):
            resname_overflow = True

        atom = AtomRecord(
            atom_index=len(atoms) + 1,
            serial=fields["serial"],
            name=fields["name"],
            resname=fields["resname"],
            chain=fields["chain"],
            resid=fields["resid"],
            icode=fields["icode"],
            element=fields["element"],
            xyz=fields["xyz"],
        )
        atoms.append(atom)

        key = (atom.chain, atom.resid, atom.icode, atom.resname)
        if pending_break or key != current_key:
            residues.append(
                ResidueRecord(
                    chain=atom.chain,
                    resid=atom.resid,
                    icode=atom.icode,
                    resname=atom.resname,
                    position=len(residues) + 1,
                )
            )
            current_key = key
            pending_break = False
        residues[-1].atoms[atom.name.upper()] = atom

    return StructureTable(
        residues=residues,
        atoms=atoms,
        has_ter=has_ter,
        resname_overflow=resname_overflow,
    )
