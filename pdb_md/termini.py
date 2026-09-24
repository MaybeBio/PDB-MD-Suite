# designed to remove terminal phosphate groups from nucleic acids, e.g. 5' phosphate group from DNA/RNA

from .utils import load_pdb, save_pdb

def is_nucleic_residue()


def find_terminal_phosphate(chain):
    """
    Find terminal phosphate groups in the given chain.

    Parameters
    ----------
    chain : Bio.PDB.Chain.Chain
        The chain object to search for terminal phosphate groups

    Returns
    -------
    list[Bio.PDB.Residue.Residue]
        A list of terminal phosphate residues found in the chain.
    """

    # we first check the first residue of the chain
    residues = list(chain.get_residues())
    first_residue = residues[0]

    
    terminal_phosphates = []
    for residue in chain:
        if is_nucleic_residue(residue) and is_terminal_phosphate(residue):
            terminal_phosphates.append(residue)
    return terminal_phosphates


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
    structure: Bio.PDB.Structure.Structure
        The modified structure with terminal phosphate groups removed.
    """

    # determine the model id 
    model = structure[0]  # assuming we are working with the first model

    # iterate over the specified chains or all chains if none are specified
    if chains is None:
        chains_to_process = model.get_chains()
    else:
        # filter the chains to only those that exist in the model
        chains_to_process = [chain for chain in chains if chain in model]

    # iterate over the chains and remove terminal phosphate groups
    for chain in chains_to_process:
        # find the terminal phosphate groups in the chain
        terminal_phosphates = find_terminal_phosphate(chain)

        # remove the terminal phosphate groups from the chain
        for phosphate in terminal_phosphates:
            chain.detach_child(phosphate.get_id())
    