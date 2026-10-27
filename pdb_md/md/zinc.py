"""Zinc-site validation, coordination-distance checks and reporting.

The MD pipeline must refuse structures whose Zn sites cannot be represented by
ZAFF (four-coordinate centres): a missing TER can make ``tleap`` bond the metal
to its neighbours, HID/HIE/HIP protonation names and residue-name column
overflow both corrupt the LEaP residue mapping.  This module checks those
preconditions plus the Zn-ligand distances and produces a :class:`SiteCheck`
report per configured site.

Structural problems (the configuration is syntactically valid but does not
match *this* PDB) raise :class:`PreflightError` (exit code 3), never
:class:`ConfigError`.
"""

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from .config import CoordinationCheck, ResidueRef, ZincSite
from .coords import AtomRecord, ResidueRecord, StructureTable
from .errors import PreflightError


#: Atom names that may coordinate a Zn if they sit inside the bond window.
NEAR_ATOM_NAMES = frozenset(
    ("SG", "NE2", "ND1", "SD", "O", "OG", "OG1", "OH", "NE", "ND2")
)


@dataclass(frozen=True)
class LigandCheck:
    """One configured ligand atom resolved against the structure."""

    ref: ResidueRef
    position: int
    atom_index: int
    distance: float


@dataclass(frozen=True)
class ExtraNear:
    """A coordinating atom found close to a Zn but not configured as a ligand."""

    chain: str
    resid: int
    resname: str
    atom: str
    distance: float
    atom_index: int


@dataclass(frozen=True)
class SiteCheck:
    """Resolved, measured report for one configured zinc site."""

    index: int                          # 1-based, order in ``zinc_sites``
    center_id: Optional[int]
    zn_position: int
    zn_atom_index: int
    ligands: List[LigandCheck]
    extra_near: List[ExtraNear]
    bond_violations: List[str]          # human-readable; empty means all in range


def preflight_structure(table: StructureTable) -> None:
    """Reject structures AMBER would mis-handle, independent of zinc sites.

    Checks for ``HIS`` residue names (AMBER needs HID/HIE/HIP) and for residue
    names that overflow the three-column fixed field (they would be silently
    truncated by ``tleap``).  No zinc-site checks are performed, so structures
    without zinc can be preflighted too.
    """
    # Column overflow is checked first: a 4-character name is already being
    # truncated by the fixed-column parser, so any HIS detection on the
    # truncated residue name would be unreliable.
    if table.resname_overflow:
        raise PreflightError(
            "a residue name overflows the 3-column PDB field and would be "
            "truncated by tleap; rename it with `pdb-md res-rename` (keeping "
            "the fixed columns) or rename the residue manually first"
        )
    for residue in table.residues:
        if residue.resname.upper() == "HIS":
            raise PreflightError(
                "residue {}:{} has resname HIS; AMBER needs a protonation-state "
                "name (HID, HIE or HIP)".format(residue.chain, residue.resid),
                hint="pdb-md res-rename -I <input.pdb> -R {}:{}:HIE".format(
                    residue.chain, residue.resid
                ),
            )


def validate_sites(
    table: StructureTable,
    sites: List[ZincSite],
    check: CoordinationCheck,
) -> List[SiteCheck]:
    """Resolve every configured zinc site and measure its coordination shell.

    Each site is validated and immediately either raises :class:`PreflightError`
    or contributes a :class:`SiteCheck`, so the first structural problem is not
    hidden behind a partial report.  Long or short bonds are *reported* in
    :attr:`SiteCheck.bond_violations`, never silently replaced.
    """
    if sites and not table.has_ter:
        raise PreflightError(
            "no TER records; tleap may bond Zn to its neighbours"
        )
    return [
        _check_site(table, site, check, index)
        for index, site in enumerate(sites, 1)
    ]


def _check_site(
    table: StructureTable,
    site: ZincSite,
    check: CoordinationCheck,
    index: int,
) -> SiteCheck:
    label = "zinc site {}".format(index)
    _check_site_shape(site, label)

    zn_atom = table.atom(site.zn)
    zn_residue = table.locate(site.zn.chain, site.zn.resid)
    _check_ter_isolation(table, zn_residue, label)

    ligands: List[LigandCheck] = []
    for ref in site.ligands:
        atom = table.atom(ref)
        residue = table.locate(ref.chain, ref.resid)
        ligands.append(
            LigandCheck(
                ref=ref,
                position=residue.position,
                atom_index=atom.atom_index,
                distance=table.distance(zn_atom, atom),
            )
        )

    bond_violations = [
        "{}:{}:{} {:.2f} A outside [{},{}]".format(
            ligand.ref.chain,
            ligand.ref.resid,
            ligand.ref.atom,
            ligand.distance,
            check.bond_min_angstrom,
            check.bond_max_angstrom,
        )
        for ligand in ligands
        if not (
            check.bond_min_angstrom
            <= ligand.distance
            <= check.bond_max_angstrom
        )
    ]

    extra_near: List[ExtraNear] = []
    if check.report_extra_near_atoms:
        extra_near = _find_extra_near(table, site, zn_atom, check)

    return SiteCheck(
        index=index,
        center_id=site.center_id,
        zn_position=zn_residue.position,
        zn_atom_index=zn_atom.atom_index,
        ligands=ligands,
        extra_near=extra_near,
        bond_violations=bond_violations,
    )


def _check_site_shape(site: ZincSite, label: str) -> None:
    """ZAFF only models four-coordinate centres; references must be unique."""
    if site.coordination_number != 4:
        raise PreflightError(
            "{}: coordination_number must be four for ZAFF (got {})".format(
                label, site.coordination_number
            )
        )
    if len(site.ligands) != site.coordination_number:
        raise PreflightError(
            "{}: expected {} ligand references, got {}".format(
                label, site.coordination_number, len(site.ligands)
            )
        )
    seen: Set[Tuple[str, int, str, str]] = set()
    for ref in site.ligands:
        key = (ref.chain, ref.resid, ref.resname.upper(), ref.atom.upper())
        if key in seen:
            raise PreflightError(
                "{}: duplicate ligand reference {}:{} {}/{}".format(
                    label, ref.chain, ref.resid, ref.resname, ref.atom
                )
            )
        seen.add(key)


def _check_ter_isolation(
    table: StructureTable, zn_residue: ResidueRecord, label: str
) -> None:
    """The Zn residue must be fenced off by TER records on both sides."""
    if not zn_residue.ter_after:
        raise PreflightError(
            "{}: Zn residue {}:{} is not followed by a TER record; tleap may "
            "bond Zn to its neighbours".format(
                label, zn_residue.chain, zn_residue.resid
            )
        )
    if zn_residue.position > 1:
        previous = table.residues[zn_residue.position - 2]
        if not previous.ter_after:
            raise PreflightError(
                "{}: Zn residue {}:{} is not preceded by a TER record; tleap "
                "may bond Zn to its neighbours".format(
                    label, zn_residue.chain, zn_residue.resid
                )
            )


def _find_extra_near(
    table: StructureTable,
    site: ZincSite,
    zn_atom: AtomRecord,
    check: CoordinationCheck,
) -> List[ExtraNear]:
    """Coordinating atoms inside the bond window that are not configured."""
    configured = {
        (ref.chain, ref.resid, ref.atom.upper()) for ref in site.ligands
    }
    extra: List[ExtraNear] = []
    for atom in table.atoms:
        if atom.name.upper() not in NEAR_ATOM_NAMES:
            continue
        if atom.atom_index == zn_atom.atom_index:
            continue
        if (atom.chain, atom.resid, atom.name.upper()) in configured:
            continue
        distance = table.distance(zn_atom, atom)
        if distance <= check.bond_max_angstrom:
            extra.append(
                ExtraNear(
                    chain=atom.chain,
                    resid=atom.resid,
                    resname=atom.resname,
                    atom=atom.name,
                    distance=distance,
                    atom_index=atom.atom_index,
                )
            )
    return extra
