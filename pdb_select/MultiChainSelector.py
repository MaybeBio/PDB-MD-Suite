from .SingleChainSelector import SingleChainSelector

class MultiChainSelector:
    """Only accepts residues with right chainid, between start and end.

    Remove hydrogens, waters and ligands. Only use model 0 by default.

    collector for multiple SingleChainSelector objects, to be used with PDBIO
    """

    def __init__(self, selectors: list[SingleChainSelector], model_id: int = 0):
        """Initialize the class."""
        # chain id must be uniquely provided in one specific selector
        ids = [selector.chain_id for selector in selectors]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate chain_id in selectors: {ids}") 
        self.selectors = selectors
        self.model_id = model_id
    def accept_model(self, model):
        """Verify if model match the model identifier."""
        # model - only keep model 0
        if model.get_id() == self.model_id:
            return 1
        return 0
    def accept_chain(self, chain):
        """Verify if chain match the chain identifier."""
        # every chain in the structure is accepted only if it is accepted by any of the selectors (by its chain selector function)
        for selector in self.selectors:
            # or
            # if chain.get_id() == selector.chain_id:
            if selector.accept_chain(chain):
                return 1
        return 0

    def accept_residue(self, residue):
        """Verify if a residue sequence is between the start and end sequence of a specific selector."""
        # residue - between start and end
        for selector in self.selectors:
            # eg. selector is [SingleChainSelector(chain_id='A', regions=[(1, 10), (20, 30)], model_id=0),
            # SingleChainSelector(chain_id='B', regions=[(5, 15)], model_id=0)]
            # then, for residue 5-10 whether in A or B, it will be accepted but lose the information of which selector accepted it
            # so, only the selector with the matching chain id of the residue has the right to accept the residue or not
            if selector.chain_id == residue.get_parent().get_id():
                return selector.accept_residue(residue)
        return 0

    def accept_atom(self, atom):
        """Verify if atoms are not Hydrogen."""
        # we can also define it specifically for each selector
        # only the selector with the matching chain id of the atom's parent residue has the right to accept the atom or not
        # atoms - get rid of hydrogens
        for selector in self.selectors:
            if selector.chain_id == atom.get_parent().get_parent().get_id():
                return selector.accept_atom(atom)
        return 0