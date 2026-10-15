# How to define position restrains on the two monomers of a dimer?

> GROMACS version:  GROMACS modification: No  Here post your question Dear all,  I want to simulate  a system containing a dimer. I want to restrain each of the monomers. I generated the restrain file and incorporated it in the topology file.  Each of my monomer has 12 atoms. But I am getting the following error.  ERROR 1 [file posre_sqm2.itp, line 5]:  Atom index (13) in position_restraints out of bounds (1-12).  This probably means that you have inserted topology section  “position_restraints”  ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mdp-parameters](https://gromacs.bioexcel.eu/tag/mdp-parameters), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[Bijaya](https://gromacs.bioexcel.eu/u/Bijaya) August 1, 2024, 12:03pm 1

GROMACS version:

 GROMACS modification: No

 Here post your question Dear all,

 I want to simulate a system containing a dimer. I want to restrain each of the monomers. I generated the restrain file and incorporated it in the topology file.

 Each of my monomer has 12 atoms. But I am getting the following error.

ERROR 1 [file posre_sqm2.itp, line 5]:

 Atom index (13) in position_restraints out of bounds (1-12).

 This probably means that you have inserted topology section

 “position_restraints”

 in a part belonging to a different molecule than you intended to.

 In that case move the “position_restraints” section to the right molecule.

I tried making two different position restrain files as well but come across the same issue.

 My topology file looks like the following:

; Include sqm topologies

#include “sqm1.itp”

#ifdef POSRES

#include “posre_sqm1.itp”

#endif

#include “sqm2.itp”

#ifdef POSRES

#include “posre_sqm2.itp”

#endif

; Include water topology

#include “oplsaa.ff/spc.itp”

#ifdef POSRES_WATER

 ; Position restraint for each water oxygen

 [ position_restraints ]

 ; i funct fcx fcy fcz

 1 1 1000 1000 1000

#endif

 Can anyone help me with the issue ? Am I missing something here ?

[obZehn](https://gromacs.bioexcel.eu/u/obZehn) August 1, 2024, 12:54pm 2

Dear [@Bijaya](https://gromacs.bioexcel.eu/u/bijaya)

This happens because the restraints are defined as a function of the molecule type. As such, if your monomer molecule has 12 atoms, then the .itp of the monomer will have 12 atoms and the restraints have to refer to those same atoms, that is, the atom number in the restraint definition can go from a min of 1 to a max of 12.

What you did here was define the second restraint (in “posre_sqm2.itp”) basing the number of the atoms on the .gro file (I guess your first two entries in the .gro file are monomer 1 and monomer 2?). As such, GROMACS will try to apply restraints to atoms 13to24, but the topology you refer to (“sqm2.itp”) has 12 atoms, and so GROMACS doesn’t see any 13to24 atom, gets confused, throws and error and dies.

You can solve this by fixing the numbering in “posre_sqm2.itp”, which should go from 1 to 12, that is, the numbering in the restraint should refer to the atom number INSIDE the topology of the molecule (“sqm2.itp”), NOT the atom number in the structure file (.gro/.pdb etc).

How did you generate the restraint files “posre_sqm1.itp” and “posre_sqm2.itp”? With `gmx genrestr` and giving as input the .gro file of the whole system?

[Bijaya](https://gromacs.bioexcel.eu/u/Bijaya) August 1, 2024, 1:26pm 3

yes, I generated the posre files using gmx genrestr but I guess I somehow made some modifications.

 It worked. Thank you so much. If I understood correctly, for a molecule type, I don’t have to repeat the index from the .gro file. It will be same for all the molecules, irrespective of the number of the molecule. Right ? Also, is it possible to provide position restrain for the two monomers in the same position restrain file ? Cause I tried doing it and it didn’t work . I might have made some mistake.

[obZehn](https://gromacs.bioexcel.eu/u/obZehn) August 5, 2024, 12:09pm 4> yes, I generated the posre files using gmx genrestr but I guess I somehow made some modifications.

Then what happened is probably that, if you provide the .gro file of the whole system, then the atom numbering is going to follow the numbering of .gro file. As such, monomer A is the first molecule of your system, and the .itp generated from `genrestr` will correctly point to atoms 1-12. The second monomer, however, will have indexes from 13 to 24, and if you `genrestr` this molecule you will have indexes 13-24 in your restraint file, which will give rise to your error. My suggestion is to extract the subsystem for which you want to generate the restraints with `trjconv`. This will give you a .gro file with the correct atom numbering, i.e. starting from 1, to use in `genrestr`.

> It will be same for all the molecules, irrespective of the number of the molecule. Right ?

Exactly. If you have a POPC lipid, and you define correctly the restraints on it, then whether you have 1 or 1000 POPC molecules the restraint file will always be the same, as the definition of the molecule is the same.

> Also, is it possible to provide position restrain for the two monomers in the same position restrain file ?

No, I do not think you can do that. Again, the position restraints are part of the molecule definition. You can’t define the restraint on two different molecules within the same molecule!

[Bijaya](https://gromacs.bioexcel.eu/u/Bijaya) August 6, 2024, 4:40am 5

Thank you so much. It was very informative.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Atom index in position_restraints out of boundsUser discussions | 5 | 964 | October 25, 2024 |  |
| Problem using Position restraints for multiple groupsUser discussionssimulation-setup | 2 | 79 | March 30, 2026 |  |
| Using positional restraints for atoms of the perimeterUser discussionsrestraints | 4 | 1479 | August 24, 2021 |  |
| Position Restraints on specific residues of a multimerUser discussionsrestraints | 2 | 158 | August 22, 2024 |  |
| Positional restraint, grompp -r error, restraint coordinates does not match topologyUser discussionsrestraints | 1 | 1048 | August 19, 2021 |  |
