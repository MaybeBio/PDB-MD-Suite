# Removing PBC before grompp

> GROMACS version: 5.0.5  GROMACS modification: Yes/No  Here post your question  Hi all, I am fairly new to gromacs. I have been doing a binary mixture simulation of TFE-Water system. After energy minimization of my system, when I load the em.gro file in VMD, I can see one/two F atoms moved far apart from some TFE molecules. I suppose this happens due to PBC. My question is: if I want to continue to equilibration from em.gro, if I first remove PBC using trjconv: gmx trjconv -f em.gro -s em.tpr -pb...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mjm91](https://gromacs.bioexcel.eu/u/mjm91) July 23, 2020, 8:31pm 1

GROMACS version: 5.0.5

 GROMACS modification: Yes/No

 Here post your question

Hi all, I am fairly new to gromacs. I have been doing a binary mixture simulation of TFE-Water system. After energy minimization of my system, when I load the em.gro file in VMD, I can see one/two F atoms moved far apart from some TFE molecules. I suppose this happens due to PBC. My question is: if I want to continue to equilibration from em.gro, if I first remove PBC using trjconv: gmx trjconv -f em.gro -s em.tpr -pbc mol -o pbc_em.gro; and perform grompp on pbc_em.gro - is this procedure okay or I can directly use em.gro without removing PBC for grompp as well. Thanks in advance

[Masrul](https://gromacs.bioexcel.eu/u/Masrul) July 23, 2020, 8:40pm 2

You don’t need to remove pbc. Tweaking PBC with trjconv serves mostly for visualization and post processing purpose, relative distances don’t get changed

[mjm91](https://gromacs.bioexcel.eu/u/mjm91) July 23, 2020, 8:51pm 3

Dear Masrul, thank you for your reply. In order to understand and test your comment, I generated two tpr files: one from em.gro and from pbc_em.gro and run two short test simulations starting from each tpr and checked if the zeroth frame gro files are similar in both cases and found that indeed the zeroth frame structures are almost similar to the em.gro file. Now I understand your point. So do I have to rerun simulations where I mistakenly removed PBC before grompp or I can still work with PBC removed structure as an input for grompp.

[Masrul](https://gromacs.bioexcel.eu/u/Masrul) July 23, 2020, 9:45pm 4

No, don’t need to rerun.

[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) July 23, 2020, 11:40pm 5

“Removing PBC” or adjusting the appearance of the system with respect to the PBC doesn’t actually change the system. All it changes is the visualision. What the simulation sees is exactly the same.

[mjm91](https://gromacs.bioexcel.eu/u/mjm91) July 24, 2020, 5:34am 6

Dear Masrul and DR_DBW thank you for your valuable comments

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Removing PBCs as simulation printsUser discussions | 1 | 340 | May 20, 2022 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Pbc effect removalUser discussions | 2 | 1566 | December 4, 2020 |  |
| Membrane box distorted after removing pbcUser discussionsforcefield,grompp,mdrun,gpu,simulation-setup | 2 | 527 | November 6, 2023 |  |
| Algorithm Gromacs used for removing periodic boundary conditionUser discussionsanalysis-tools | 6 | 2063 | November 3, 2022 |  |
