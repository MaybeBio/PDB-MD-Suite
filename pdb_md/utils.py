# some utility functions defined

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
