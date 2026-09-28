# some utility functions defined

import typer
from Bio.PDB import PDBIO, PDBParser, MMCIFParser
from pathlib import Path

def consolidate_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Description
    -----------
    Consolidate a list of tuple ranges into a list of non-overlapping ranges, and sort in ascending order

    Args
    ----
    ranges: list[tuple[int, int]]
        A list of tuple ranges, e.g. [(1, 5), (3, 7), (10, 12)]

    Returns
    -------
    list[tuple[int, int]]: A list of non-overlapping ranges, sorted in ascending order
    
    """
    if not ranges:
        return []
    # first sort the ranges by the start value in ascending order
    ranges.sort(key=lambda x: x[0])
    # start with the first range
    consolidated = [ranges[0]]
    # start comparison
    for current in ranges[1:]:
        previous = consolidated[-1]
        if current[0] <= previous[1] + 1:
            previous[1] = max(previous[1], current[1])
        else:
            consolidated.append(current)
    return consolidated

    
def warn_if_4char_resnames(input_pdb: Path):
    """
    Warn when a PDB input uses 4-character residue names.

    PDB reserves columns 18-20 for the residue name and column 21 for the blank
    separator before the chain id. Some force fields (GROMOS HISA/HISB, CHARMM
    CYSH) write a 4th character into column 21. PDBParser reads the name from the
    strict 3-column slice line[17:20], so such a name loses its 4th character
    without any error. Report it rather than let it pass unnoticed.

    Parameters
    ----------
    input_pdb : Path
        Path to the input PDB file.
    """
    first = None
    count = 0
    with open(input_pdb) as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.startswith(("ATOM", "HETATM")) or len(line) < 21:
                continue
            # column 21 (0-indexed 20) is the blank separator; anything there
            # means the residue name spilled out of its 3-column field
            if line[20] == " ":
                continue
            count += 1
            if first is None:
                # line[17:21] is the name as written. The columns after it are
                # shifted by one in the 81-column variant, so report the line
                # number rather than a chain id / residue number that may be off.
                first = (line[17:21].strip(), lineno)

    if first is None:
        return
    resname, lineno = first
    typer.echo(
        f"WARNING: {input_pdb} uses 4-character residue names; e.g. {resname} on line "
        f"{lineno}. This toolkit reads residue names from columns 18-20 only, so all "
        f"{count} of them will be truncated to 3 characters.",
        err=True,
    )


def load_pdb(input_pdb:Path):
    """
    Load a PDB or MMCIF file and return the structure object.

    Parameters
    ----------
    input_pdb : Path
        Path to the input PDB or MMCIF file.

    Returns
    -------
    structure : Bio.PDB.Structure.Structure
        The loaded structure object.
    """

    # check if the input file exists
    if not input_pdb.exists():
        raise ValueError(f"Input file {input_pdb} does not exist.")

    # check the file extension to determine the parser
    suffix = input_pdb.suffix.lower()
    if suffix == ".pdb":
        # warn before parsing, so the message is seen even if a shifted 81-column
        # record makes PDBParser raise
        warn_if_4char_resnames(input_pdb)
        parser = PDBParser(QUIET=True)
    elif suffix == ".cif":
        parser = MMCIFParser(QUIET=True)
    else:
        raise ValueError("Unsupported file format. Please provide a .pdb or .cif file.")

    # parse the structure
    return parser.get_structure("x", input_pdb)

def save_pdb(structure, output_pdb:Path):
    """
    Save a structure object to a PDB file.

    Parameters
    ----------
    structure : Bio.PDB.Structure.Structure
        The structure object to save.
    output_pdb : Path
        Path to the output PDB file.
    """

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_pdb))
