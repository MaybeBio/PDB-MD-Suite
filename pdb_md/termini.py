# designed to remove terminal phosphate groups from nucleic acids, e.g. 5' phosphate group from DNA/RNA

from Bio.PDB.Polypeptide import is_nucleic 

# Names of phosphate atoms to delete: P + non-bridging oxygen + hydrogen attached to it (both naming conventions included)
# O5'(in phosphodiester bond formation) is not in this list, so it will never be deleted
PHOSPHATE_ATOM_NAMES = frozenset({                                                                        
      "P",                                                                                                  
      "OP1", "O1P", "HOP1", "HO1P",                                                                         
      "OP2", "O2P", "HOP2", "HO2P",                                                                         
      "OP3", "O3P", "HOP3", "HO3P",                                                                         
  }) 

def find_terminal_phosphate_residue(chain):
    """
    Find terminal phosphate groups in the given chain and return this residue.

    Parameters
    ----------
    chain : Bio.PDB.Chain.Chain
        The chain object to search for terminal phosphate groups

    Returns
    -------
    Bio.PDB.Residue.Residue or None
        The terminal phosphate residue found in the chain, or None if not found.
    """

    # we first check the first residue of the chain
    residues = list(chain.get_residues())
    # assume the chain is not empty
    if not residues:
        return None
    first_residue = residues[0]

    # check if the first residue is a nucleic acid and has a terminal phosphate group
    if not is_nucleic(first_residue):
        return None
    elif not first_residue.has_id("P"):
        # so it is a typical 5'-OH
        return None
    return first_residue

def strip_5_phosphate(structure, chains):
    """
    Remove terminal phosphate groups from nucleic acids in the given structure and chains.
    
    Args
    ----
    structure: Bio.PDB.Structure.Structure
        The structure object to process.

    chains: list[str] or None
        List of chain IDs to process. If None, all chains will be processed.
    
    Returns
    -------
    dict[str, list[str]]
        {chain_id: [atom names removed]} for each chain that was modified.
        An empty dict means no chain carried a 5'-terminal phosphate.
        `structure` itself is modified in place.
    """

    # determine the model id 
    model = structure[0]  # assuming we are working with the first model

    # iterate over the specified chains or all chains if none are specified
    if chains is None:
        # process all chains in the model if no specific chains are provided
        chains_to_process = model.get_chains()
    else:
        # filter the chains to only those that exist in the model
        # note we need to change the `chain` from str to the actual chain object in the model
        chains_to_process = [model[chain] for chain in chains if chain in model]

    # collect what was removed per chain, so the caller can report it
    removed: dict[str, list[str]] = {}

    # iterate over the chains and remove terminal phosphate groups
    for chain in chains_to_process:
        # find the terminal phosphate groups in the chain
        residue = find_terminal_phosphate_residue(chain)
        if residue is None:
            continue
        # collect the terminal phosphate group atoms to remove
        remove_atoms = [a.get_name() for a in residue if a.get_name() in PHOSPHATE_ATOM_NAMES]
        # remove them
        for atom_name in remove_atoms:
            residue.detach_child(atom_name)
        # find_terminal_phosphate_residue only returns a residue that has "P",
        # and "P" is in PHOSPHATE_ATOM_NAMES, so remove_atoms is never empty here
        removed[chain.get_id()] = remove_atoms

    return removed
