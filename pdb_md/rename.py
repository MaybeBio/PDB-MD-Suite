# designed for renaming residues in a PDB file, e.g. renaming a selected residue to a different name, or renaming all residues of a certain type to a new name

from io import StringIO

from Bio.PDB import PDBIO

# A PDB residue name occupies columns 18-20. A 4-character name (GROMOS HISA/HISB,
# CHARMM CYSH) borrows the blank column 21 that separates name from chain id;
# there is no room for anything longer.
MAX_RESNAME_LEN = 4

def find_residue(chain, resseq):
    """
    Return the residue numbered `resseq` in `chain`, or None if there is none.

    Parameters
    ----------
    chain : Bio.PDB.Chain.Chain
        The chain to search.
    resseq : int
        Residue sequence number.

    Returns
    -------
    Bio.PDB.Residue.Residue or None
    """
    # A biopython residue id is (hetfield, resseq, icode), so `chain[resseq]` only
    # resolves polymer residues; a HETATM residue is keyed e.g. ('H_ZN', 1, ' ').
    # Iterating sidesteps that asymmetry and covers both record types.
    for residue in chain.get_residues():
        # or for residue in chain 
        if residue.id[1] == resseq:
            # or residue.get_id()[1] == resseq
            return residue
    return None


def rename_residues(structure, renames):
    """
    Rename residues in `structure`. The structure is modified in place.

    Parameters
    ----------
    structure : Bio.PDB.Structure.Structure
        The structure to modify.

    renames : list[tuple[str, int, str]]
        (chain_id, resseq, new_resname) triples.

    Returns
    -------
    dict[tuple[str, int], tuple[str, str]]
        {(chain_id, resseq): (old_resname, new_resname)} for each rename that was
        applied. A chain or residue that is absent is skipped, not raised on, so the
        caller can report every miss in one pass.
    """

    # test the first model
    model = structure[0]

    #  {(chain_id, resseq): (old_resname, new_resname)}
    applied: dict[tuple[str, int], tuple[str, str]] = {}
    for chain_id, resseq, new_resname in renames:
        if chain_id not in model:
            continue
        residue = find_residue(model[chain_id], resseq)
        if residue is None:
            continue
        # Keep the name the residue had on first sight, so listing one residue twice
        # reports its true before/after instead of the intermediate name.
        old_resname = applied[(chain_id, resseq)][0] if (chain_id, resseq) in applied else residue.resname
        residue.resname = new_resname
        applied[(chain_id, resseq)] = (old_resname, new_resname)

    return applied


def save_pdb_keeping_columns(structure, output_pdb):
    """
    Save `structure` to `output_pdb`, repairing PDBIO's mishandling of 4-character
    residue names.

    PDBIO formats the residue name with a *minimum* width of 3 ("%3s"), which does not
    truncate. A 4-character name therefore pushes every following column one to the
    right, emitting an 81-column atom record with the chain id and residue number out of
    place -- a record that fixed-column parsers read wrong. We render to memory, drop
    the stray column, then write to disk.

    Parameters
    ----------
    structure : Bio.PDB.Structure.Structure
        The structure to save.
    output_pdb : pathlib.Path
        Path to the output PDB file.
    """
    io = PDBIO()
    io.set_structure(structure)
    buffer = StringIO()
    # we save to a buffer first, so we can fix the 4-character residue names before writing to disk
    io.save(buffer)

    lines = []
    for line in buffer.getvalue().splitlines(keepends=True):
        # if it has a 4-character residue name, then:
        # len(line.strip()) 79 column
        # len(line) 82 column
        # len(line.rstrip("\n")) 81 column
        # In normal 3-character residue names, len(line.rstrip("\n")) is 80 column
        # Only a 4-character residue name can push an atom record past 80 columns,
        # so 3-character names (and every other record) pass through untouched.
        if line.startswith(("ATOM", "HETATM")) and len(line.rstrip("\n")) > 80:
            # in normal-case(3-character), column 21(1-index, 20(0-index)) is a blank space, but in 4-character names it is the 4th character of the name
            # so line[:21] is end of the 4-character name,, line[21:22] is the blank space right-moved move now, line[22:] is the rest of the record starting with the chain id
            # and we combine 4-character name with chain id to make it 80 columns
            line = line[:21] + line[22:]
        lines.append(line)

    with open(output_pdb, "w") as handle:
        handle.writelines(lines)
