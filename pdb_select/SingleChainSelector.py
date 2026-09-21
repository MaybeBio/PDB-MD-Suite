# this script is adapted and modified from https://github.com/biopython/biopython/blob/master/Bio/PDB/Dice.py

# Copyright (C) 2002, Thomas Hamelryck (thamelry@binf.ku.dk)
#
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.
#
# Modifications for pdb-select: Copyright (C) 2026, Joe Hoye Dow
# Licensed under the BSD 3-Clause License (see LICENSE).

"""Code for chopping up (dicing) a structure.

This module is used internally by the Bio.PDB.extract() function.
"""

import re
import warnings

from Bio import BiopythonWarning
from Bio.PDB.PDBIO import PDBIO
from .utils import consolidate_ranges

_hydrogen = re.compile("[123 ]*H.*")


class SingleChainSelector:
    """Only accepts residues with right chainid, between start and end.

    Remove hydrogens, waters and ligands. Only use model 0 by default.

    Modified to support multiple regions selected.

    Pass regions=None to keep the whole chain instead of specific ranges.
    """

    def __init__(
        self,
        chain_id,
        regions: list[tuple[int, int]] | None = None,
        model_id=0,
    ):
        """Initialize the class.

        A regions of None means "whole chain" and an empty list means "keep
        nothing"; the two stay distinguishable because consolidate_ranges would
        collapse both to an empty list otherwise.
        """
        self.chain_id = chain_id
        self.regions = None if regions is None else consolidate_ranges(regions)
        self.model_id = model_id

    def accept_model(self, model):
        """Verify if model match the model identifier."""
        # model - only keep model 0
        if model.get_id() == self.model_id:
            return 1
        return 0

    def accept_chain(self, chain):
        """Verify if chain match chain identifier."""
        if chain.get_id() == self.chain_id:
            return 1
        return 0

    def accept_residue(self, residue):
        """Verify if a residue sequence is between the start and end sequence."""
        # residue - between start and end
        hetatm_flag, resseq, icode = residue.get_id()
        if hetatm_flag != " ":
            # skip HETATMS
            return 0
        if icode != " ":
            warnings.warn(
                f"WARNING: Icode {icode} at position {resseq}", BiopythonWarning
            )
        # whole chain: every standard residue is accepted
        if self.regions is None:
            return 1
        # or if any(start <= resseq <= end for start, end in self.regions)
        for start, end in self.regions:
            if start <= resseq <= end:
                return 1
        return 0

    def accept_atom(self, atom):
        """Verify if atoms are not Hydrogen."""
        # atoms - get rid of hydrogens
        name = atom.get_id()
        if _hydrogen.match(name):
            return 0
        else:
            return 1

# extract function only works for a single chain, useless now that we have MultiChainSelector
def extract(structure, chain_id, regions, filename):
    """Write out selected portion to filename."""
    sel = SingleChainSelector(chain_id, regions)
    io = PDBIO()
    io.set_structure(structure)
    io.save(filename, sel)