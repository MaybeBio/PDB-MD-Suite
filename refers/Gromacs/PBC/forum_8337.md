# PBC correction while inserting a molecule

> Dear gromacs users,  I am currently working with polymer and studying the effect on a protein. I am generating the polymer configuration and protein configuration separately. So I am equilibrating the protein and the polymer in water for long time and then extract the polymer configuration and inserting in the protein using gmx insert-molecules by replacing water molecules.  For this purpose I am removing PBC from the final gro file obtained for the protein-in-water equilibration simulation (pbc...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mjm91](https://gromacs.bioexcel.eu/u/mjm91) February 15, 2024, 4:55am 1

Dear gromacs users,

I am currently working with polymer and studying the effect on a protein. I am generating the polymer configuration and protein configuration separately. So I am equilibrating the protein and the polymer in water for long time and then extract the polymer configuration and inserting in the protein using gmx insert-molecules by replacing water molecules.

For this purpose I am removing PBC from the final gro file obtained for the protein-in-water equilibration simulation (pbc_protein_water.gro) and removing PBC from the final gro file obtained for the polymer-in-water equilibration simulation and extracting polymer coordinates only (pbc_polymer.gro), making sure there is no broken molecule or outside boundary as that might have an effect while using gmx insert-molecules. Then I am inserting the pbc_polymer.gro into the pbc_protein_water.gro by using the gmx insert-molecules tool by replacing water molecules. Is this fine or we don’t need to remove PBC for preparing the initial configuration for the protein-polymer-water system?

Any suggestion(s) is much appreciated.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Removing PBC before gromppUser discussions | 5 | 511 | July 24, 2020 |  |
| How can I add molecules to an equilibrated system without messing PBCs?User discussionssimulation-setup | 1 | 91 | January 16, 2025 |  |
| Remove PBC effects on membrane+protein+ligandUser discussionspbc | 4 | 699 | October 20, 2022 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 202 | January 15, 2025 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
