# Trouble to apply distance restraints

> GROMACS version:  2019.2  GROMACS modification: No  Here post your question  Hello,  I am trying to apply distance restraint on protein in SIrah force field to prevent deformation of protein during pulling (as reducing force constant or  with lower rate did not help).  In my topology I have 4 chains: ChainA, ChainB, ChainC, ChainD  Dimer1 consists of chains A,B and they are fixed during pulling by including following command in topology files:  #ifdef POSRES_A  #include “posre_Other_chain_A.itp” ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mdp-parameters](https://gromacs.bioexcel.eu/tag/mdp-parameters), [restraints](https://gromacs.bioexcel.eu/tag/restraints), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[srdjan](https://gromacs.bioexcel.eu/u/srdjan) February 8, 2022, 5:52pm 1

GROMACS version: 2019.2

 GROMACS modification: No

 Here post your question

Hello,

I am trying to apply distance restraint on protein in SIrah force field to prevent deformation of protein during pulling (as reducing force constant or with lower rate did not help).

 In my topology I have 4 chains: ChainA, ChainB, ChainC, ChainD

Dimer1 consists of chains A,B and they are fixed during pulling by including following command in topology files:

#ifdef POSRES_A

#include “posre_Other_chain_A.itp”

#endif

#ifdef POSRES_B

#include “posre_Other_chain_B.itp”

#endif

I have created distance restraint files by following command:

 gmx genrestr -f C.pdb -n C.ndx -o C.itp -disre yes -fc 1000 1000 1000 (for chain C and chain D)

and then included following command in topology of chain C:

#ifdef CONF_C

#include “C.itp”

#endif

end in mdp file: DEFINE = -DCONF_C

and then simulation works.

However, if I try to distance restrain chain D too, it does not work, I am getting some error in gromacs:

 DEFINE = -DCONF_C -DCONF_D

I was also getting same error if I use only :

 DEFINE = -DCONF_C

and write in corresponding topology files:

#ifdef CONF_C

#include “C.itp”

#endif

#ifdef CONF_C

#include “D.itp”

#endif

I have tried to start simulation again by making gromacs merge chain A,B into one chain1, and merge chains C,D into another chain2, and then I have create distance restraints to chain2, and simulation started without showing any error, but I see no progress in .log file, it is on timestep 0 for hours.

I would appreciate if someone could help me with this issue. Thank you in advance.

PS. The error I get when I try to apply distance restraints to two chains simultaneously is:

getting the following error:

 Program: gmx mdrun, version 2019.2

 Source file: src/gromacs/listed-forces/disre.cpp (line 174)

 Function: init_disres(FILE*, const gmx_mtop_t*, t_inputrec*, const t_commrec*, const gmx_multisim_t*, t_fcdata*, t_state*, gmx_bool)::&lt;lambda()&gt;

Assertion failed:

 Condition: type_max - type_min + 1 == dd-&gt;nres

 All distance restraint parameter entries in the topology should be consecutive

[srdjan](https://gromacs.bioexcel.eu/u/srdjan) February 9, 2022, 9:54am 2

Hello,

I would also appreciate if someone can give advice how to prevent protein being deformed during pulling, I have tried to reduce force and apply slower pulling, the slowest I tried is 0.001 and force 500 (with force 250 it was difficult to move them).

 But maybe there are some another useful tips or advices?

 If I would manage to get proteins not deformed during pulling, then I would not need distance restraints.

Thanx a lot.

[srdjan](https://gromacs.bioexcel.eu/u/srdjan) April 4, 2022, 10:18am 3

I managed to resolve problem on another way, by inserting special bonds of type 10.

![](https://avatars.discourse-cdn.com/v4/letter/s/e495f1/48.png)[Distance restraints applied to multiple proteins](https://gromacs.bioexcel.eu/t/distance-restraints-applied-to-multiple-proteins/3389/11)[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)

>  Thanx :). For me even worked when I have put “force constant 10” although I was not checking thoroughly by RMSD how stable is conformation, but visually in VMD it looked pretty fine. 

1 Like

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Distance restraints applied to multiple proteinsUser discussions | 10 | 2002 | February 10, 2022 |  |
| How to put distance restraints into topology fileUser discussionsmdrun,restraints | 25 | 2280 | January 16, 2025 |  |
| Distance restraints applied to multiple proteins + separate thermostat couplingUser discussions | 0 | 328 | January 3, 2022 |  |
| Distance restraints between more than one protein and ligandUser discussions | 1 | 435 | December 7, 2022 |  |
| Difficulties with distance restraints of multiple moleculesUser discussionsmdp-parameters,mdrun | 5 | 962 | August 17, 2021 |  |
