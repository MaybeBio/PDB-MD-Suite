# generate position-restraint .itp files for a GROMACS topology, and include them
#
# Why this exists
# ---------------
# pdb2gmx writes posre.itp AND the "#ifdef POSRES ... #endif" block automatically.
# ParmEd does NOT. A GROMACS topology converted from AMBER with ParmEd therefore
# has no restraint file and no #ifdef POSRES block, so "define = -DPOSRES" in the
# NVT/NPT .mdp files is a silent no-op and equilibration runs unrestrained.
#
# [ position_restraints ] indices are local to each [ moleculetype ] (starting at
# 1), so one .itp is written per selected moleculetype, numbered from that
# moleculetype's own [ atoms ] section.

from dataclasses import dataclass, field
from pathlib import Path

import re

# a section header, e.g. "[ moleculetype ]", "[ atoms ]", "[ position_restraints ]"
_SECTION_RE = re.compile(r"^\s*\[\s*([A-Za-z_]+)\s*\]")
# an [ atoms ] data row starts with the atom number
_ATOM_ROW_RE = re.compile(r"^\s*\d")
# section headers that terminate a moleculetype's parameter block
_BLOCK_END_SECTIONS = frozenset({"moleculetype", "system", "molecules"})


@dataclass
class Moleculetype:
    name: str
    header_line: int
    atoms: list = field(default_factory=list)  # [(local nr, atom name)]


@dataclass
class RestraintReport:
    itp_files: list = field(default_factory=list)  # [Path]
    restrained: list = field(default_factory=list)  # [(name, n_heavy, n_total)]


def parse_moleculetypes(lines):
    """Return one Moleculetype per [ moleculetype ] block, with its [ atoms ] rows.

    The moleculetype name is the first non-blank, non-comment line after the
    header, so a topology with or without the "; Name nrexcl" comment parses.
    """
    mts = []
    cur = None
    in_atoms = False
    for i, ln in enumerate(lines):
        m = _SECTION_RE.match(ln)
        if m:
            section = m.group(1).lower()
            if section == "moleculetype":
                name = None
                for j in range(i + 1, len(lines)):
                    token = lines[j].strip()
                    if token == "" or token.startswith(";"):
                        continue
                    name = token.split()[0]
                    break
                cur = Moleculetype(name=name, header_line=i)
                mts.append(cur)
                in_atoms = False
            elif section == "atoms" and cur is not None:
                in_atoms = True
            else:
                in_atoms = False
        elif in_atoms and _ATOM_ROW_RE.match(ln):
            parts = ln.split()
            cur.atoms.append((int(parts[0]), parts[4]))
    return mts


def select_heavy_atoms(atoms):
    """Keep atoms whose name does not start with H (case-insensitive)."""
    return [(nr, name) for nr, name in atoms if not name.upper().startswith("H")]


def render_posre(heavy_atoms, fc):
    """Render the [ position_restraints ] block for a set of heavy atoms."""
    lines = ["[ position_restraints ]", "; ai   funct   fcx       fcy       fcz"]
    for nr, _ in heavy_atoms:
        lines.append(f"{nr:6d}     1 {fc:8.1f} {fc:8.1f} {fc:8.1f}")
    return "\n".join(lines) + "\n"


def _block_end(lines, mt):
    """Index of the line that ends this moleculetype's block (next mt or [ system ])."""
    for j in range(mt.header_line + 1, len(lines)):
        m = _SECTION_RE.match(lines[j])
        if m and m.group(1).lower() in _BLOCK_END_SECTIONS:
            return j
    return len(lines)


def inject_posres_blocks(lines, moleculetypes, selected):
    """Return a copy of `lines` with a #ifdef POSRES block at the end of each selected block."""
    by_name = {mt.name: mt for mt in moleculetypes}
    inserts = []
    for name in selected:
        end = _block_end(lines, by_name[name])
        block = ["#ifdef POSRES", f'#include "posre_{name}.itp"', "#endif", ""]
        inserts.append((end, block))

    out = list(lines)
    # insert bottom-up so earlier indices stay valid
    for pos, block in sorted(inserts, key=lambda item: -item[0]):
        out[pos:pos] = block
    return out


def restrain_topology(input_path, names, fc, output_path, force=False):
    """Write posre_<name>.itp per selected moleculetype and a patched topology copy.

    The input topology is never modified. Returns a RestraintReport.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    lines = input_path.read_text().splitlines()

    if not force and any("#ifdef POSRES" in ln for ln in lines):
        raise ValueError(
            "input topology already contains a #ifdef POSRES block; "
            "pass force=True to add another set"
        )

    mts = parse_moleculetypes(lines)
    if not mts:
        raise ValueError("no [ moleculetype ] section found in the input topology")

    known = [mt.name for mt in mts]
    for name in names:
        if name not in known:
            raise ValueError(
                f"moleculetype {name!r} not found; available: {', '.join(known)}"
            )

    patched = inject_posres_blocks(lines, mts, names)

    by_name = {mt.name: mt for mt in mts}
    outdir = output_path.parent
    itp_files = []
    restrained = []
    for name in names:
        atoms = by_name[name].atoms
        heavy = select_heavy_atoms(atoms)
        itp = outdir / f"posre_{name}.itp"
        itp.write_text(render_posre(heavy, fc))
        itp_files.append(itp)
        restrained.append((name, len(heavy), len(atoms)))

    output_path.write_text("\n".join(patched) + "\n")
    return RestraintReport(itp_files=itp_files, restrained=restrained)
