# Lipid-Protein-Ligand

> Dear all,  GROMACS version:2020-4  GROMACS modification: No  I am actually interested to study the interactions of ligands with a membrane protein with the binding pocket residing in the transmembrane region.  Did the lysosyme tutorial, protein-ligand interactions tutorial and the Protein-Lipid (KALP in DPCC) tutorials.  I would like to intoduce the ligand too into the protein-lipid system. Is there any tutorial available for the same (Lipid-Protein-Ligand), so that I can be comfortable before w...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[tarzan](https://gromacs.bioexcel.eu/u/tarzan) January 8, 2021, 5:39am 1

Dear all,

 GROMACS version:2020-4

 GROMACS modification: No

 I am actually interested to study the interactions of ligands with a membrane protein with the binding pocket residing in the transmembrane region.

 Did the lysosyme tutorial, protein-ligand interactions tutorial and the Protein-Lipid (KALP in DPCC) tutorials.

 I would like to intoduce the ligand too into the protein-lipid system. Is there any tutorial available for the same (Lipid-Protein-Ligand), so that I can be comfortable before working on my problem of interest.

 with best wishes

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) January 8, 2021, 2:06pm 2

If you apply what you learned from the existing tutorials, you should be able to piece this together. You generate the protein and ligand topologies, generate the complex coordinates, then embed those in the membrane.

[tarzan](https://gromacs.bioexcel.eu/u/tarzan) January 21, 2021, 11:04am 3

Dear Prof. Justin

 ligand+protein_lipid.

 I have put the coplex in the lipid …

 now during position restain step I want to restain both protein and the ligand,

 I run this step

 gmx genrestr -f complex_newbox.gro -o strong_posre.itp -fc 100000 100000 100000

 and restrain protein …(chose group 1)

 should i run this once again and choose the ligand (group 13) to restain it

 or should i do it someother way…

 regards

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) January 22, 2021, 1:26pm 4

You need to create a restraint topology for the ligand from a coordinate file containing only the ligand and that has all atoms numbered starting from 1.

[tarzan](https://gromacs.bioexcel.eu/u/tarzan) January 27, 2021, 5:07am 5

thank you for the reply…

 With all the little experince I have, I have been trying since a few days … i keep getting this error in one form or the other …

 during this command

 gmx grompp -f minim_inflategro.mdp -c system_inflated.gro -p topol.top -r system_inflated.gro -o system_inflated_em.tp

ERROR 1 [file strong_posre.itp, line 754]:

 Atom index (750) in position_restraints out of bounds (1-749).

 This probably means that you have inserted topology section

 “position_restraints”

 in a part belonging to a different molecule than you intended to.

 In that case move the “position_restraints” section to the right molecule.

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) January 27, 2021, 4:37pm 6

You can only generate restraint topologies from coordinate files of that single molecule, numbered from 1. The error suggests you used a complex or whole system as input to `genrestr`.

[tarzan](https://gromacs.bioexcel.eu/u/tarzan) February 1, 2021, 8:50am 7

Dear Prof. Justin

 I couldn’t just manage to get it right … any leads pls …

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) February 1, 2021, 5:01pm 8

`gmx genrestr -f my_ligand_only_with_atoms_numbered_from_1.gro`

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| ERROR 1 [file strong_posre_Protein_chain_A.itp, line 4414]: INQUIRYUser discussions | 2 | 430 | July 9, 2022 |  |
| Add restraint on Phosphorous atoms of lipid headgroups that were farther than 0.5 nm from proteinUser discussions | 4 | 413 | April 2, 2024 |  |
| ERROR 1 [file strong_posre.itp, line 4414] INQUIRYUser discussions | 16 | 1729 | July 12, 2022 |  |
| Protein-Ligand complex MD simulationUser discussions | 7 | 948 | June 18, 2024 |  |
| Problem for merging two proteins and membrane in the same boxUser discussions | 8 | 1095 | March 10, 2023 |  |
