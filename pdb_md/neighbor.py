# Find atoms within a distance of a given atom, using Bio.PDB.NeighborSearch

from Bio.PDB import NeighborSearch, Selection


def find_neighbors(structure, serial, radius):
    """
    Return atoms within `radius` of the atom whose serial number is `serial`.

    Only model 0 of the structure is searched, matching the single-model
    convention used by the rest of this toolkit.

    Args
    ----
    structure : Bio.PDB.Structure.Structure
        The parsed structure object.
    serial : int
        Atom serial number (PDB columns 7-11) of the query atom.
    radius : float
        Distance threshold in Angstrom.

    Returns
    -------
    (target, neighbors)
        target : Bio.PDB.Atom.Atom
            The query atom.
        neighbors : list[tuple[float, Bio.PDB.Atom.Atom]]
            (distance, atom) pairs, sorted ascending by distance. The query
            atom itself is excluded.
    """
    model = structure[0]
    # list all atoms in the model, so we can find the target atom by serial number
    atoms = list(Selection.unfold_entities(model, "A"))

    target = None
    for atom in atoms:
        # each atom is a Bio.PDB.Atom.Atom object
        if atom.get_serial_number() == serial:
            target = atom
            break
    if target is None:
        raise ValueError(f"No atom with serial {serial} in model 0 of the structure.")

    ns = NeighborSearch(atoms)
    # ns.search matches ≤ radius
    hits = ns.search(target.coord, radius, level="A")

    neighbors = []
    for atom in hits:
        # each atom is a Bio.PDB.Atom.Atom object, excluding the target atom itself
        if atom.get_serial_number() == serial:
            continue
        # Bio.PDB Atom.__sub__ returns the distance between two atoms
        # refer to https://biopython.org/wiki/The_Biopython_Structural_Bioinformatics_FAQ
        # the minus operator for atoms has been overloaded to return the distance between two atoms
        neighbors.append((atom - target, atom))
    neighbors.sort(key=lambda pair: pair[0])
    return target, neighbors


def atom_identity(atom):
    """
    Return identifying fields for an atom.

    Args
    ----
    atom : Bio.PDB.Atom.Atom

    Returns
    -------
    tuple[str, str, str, str, str, str]
        (serial, chain, resid, resname, atomname, element). `resid` is the
        residue number with any insertion code appended; `element` is empty
        when the source file carried no element column.
    """
    full_id = atom.get_full_id()
    chain = full_id[2]
    _hetflag, resseq, icode = full_id[3]
    # Note here icode!
    resid = str(resseq) + icode.strip()
    element = atom.element or ""
    return (
        str(atom.get_serial_number()),
        chain,
        resid,
        atom.get_parent().get_resname(),
        atom.get_name(),
        element,
    )
