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
from typing import Optional

import re

# a section header, e.g. "[ moleculetype ]", "[ atoms ]", "[ position_restraints ]"
_SECTION_RE = re.compile(r"^\s*\[\s*([A-Za-z_]+)\s*\]")
# an [ atoms ] data row starts with the atom number
_ATOM_ROW_RE = re.compile(r"^\s*\d")
# section headers that terminate a moleculetype's parameter block
_BLOCK_END_SECTIONS = frozenset({"moleculetype", "system", "molecules"})
# the #ifdef that guards a restraint include (word boundary: not POSRES_FC etc.)
_POSRES_IFDEF_RE = re.compile(r"^\s*#ifdef\s+POSRES\b")
_ENDIF_RE = re.compile(r"^\s*#endif\b")


@dataclass
class Moleculetype:
    name: str
    header_line: int
    atoms: list = field(default_factory=list)  # [(local nr, atom name)]


@dataclass
class RestraintResult:
    name: str
    status: str  # "added" | "skipped" | "replaced"
    itp_file: Optional[Path] = None
    n_heavy: int = 0
    n_total: int = 0
    original_block: list = field(default_factory=list)  # pre-existing #ifdef lines


@dataclass
class RestraintReport:
    results: list = field(default_factory=list)  # [RestraintResult]


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


def existing_posres_block(lines, mt):
    """(start, stop) inclusive line range of this moleculetype's #ifdef POSRES block.

    Returns None when the moleculetype's own block carries no POSRES include.
    """
    end = _block_end(lines, mt)
    for j in range(mt.header_line + 1, end):
        if _POSRES_IFDEF_RE.match(lines[j]):
            for k in range(j + 1, end):
                if _ENDIF_RE.match(lines[k]):
                    return (j, k)
            return (j, end - 1)  # unterminated #ifdef: take to the block end
    return None


def _posres_block_lines(name):
    return ["#ifdef POSRES", f'#include "posre_{name}.itp"', "#endif", ""]


def inject_posres_blocks(lines, moleculetypes, selected, force=False):
    """Return (new_lines, plan) for the selected moleculetypes.

    plan is a list of (name, status, original_block_lines) in `selected` order,
    where status is "added", "skipped" (already restrained, no --force) or
    "replaced" (already restrained, --force). Unselected moleculetypes are never
    touched, whether or not they carry a POSRES block.
    """
    by_name = {mt.name: mt for mt in moleculetypes}
    plan = []
    operations = []  # (position, remove_count, name)
    for name in selected:
        mt = by_name[name]
        rng = existing_posres_block(lines, mt)
        if rng is None:
            operations.append((_block_end(lines, mt), 0, name))
            plan.append((name, "added", []))
            continue
        start, stop = rng
        original = lines[start:stop + 1]
        if not force:
            plan.append((name, "skipped", original))
            continue
        # replace: also eat one trailing blank line so repeated --force is stable
        remove_stop = stop
        if remove_stop + 1 < len(lines) and lines[remove_stop + 1].strip() == "":
            remove_stop += 1
        operations.append((start, remove_stop - start + 1, name))
        plan.append((name, "replaced", original))

    out = list(lines)
    # apply bottom-up so earlier line indices stay valid
    for pos, remove, name in sorted(operations, key=lambda op: -op[0]):
        out[pos:pos + remove] = _posres_block_lines(name)
    return out, plan


def restrain_topology(input_path, names, fc, output_path, force=False):
    """Write posre_<name>.itp per selected moleculetype and a patched topology copy.

    Selected moleculetypes that already carry a #ifdef POSRES block are skipped
    unless force=True, in which case the existing block is replaced. The input
    topology is never modified. Returns a RestraintReport.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    lines = input_path.read_text().splitlines()

    mts = parse_moleculetypes(lines)
    if not mts:
        raise ValueError("no [ moleculetype ] section found in the input topology")

    known = [mt.name for mt in mts]
    for name in names:
        if name not in known:
            raise ValueError(
                f"moleculetype {name!r} not found; available: {', '.join(known)}"
            )

    patched, plan = inject_posres_blocks(lines, mts, names, force=force)

    by_name = {mt.name: mt for mt in mts}
    outdir = output_path.parent
    results = []
    for name, status, original in plan:
        if status == "skipped":
            results.append(RestraintResult(name=name, status=status, original_block=original))
            continue
        atoms = by_name[name].atoms
        heavy = select_heavy_atoms(atoms)
        itp = outdir / f"posre_{name}.itp"
        itp.write_text(render_posre(heavy, fc))
        results.append(
            RestraintResult(
                name=name,
                status=status,
                itp_file=itp,
                n_heavy=len(heavy),
                n_total=len(atoms),
                original_block=original,
            )
        )

    output_path.write_text("\n".join(patched) + "\n")
    return RestraintReport(results=results)
