# Position restraints

> GROMACS version: 2018.1  GROMACS modification: No  I’m new to GROMACS so I’ve been following Dr. Lemkul’s tutorials at mdtutorials.com, in particular his lysozme tutorial. Towards the end he mentions that we need to remove the position restraints for the production md but doesn’t give any instruction on how to do that. He goes right into using grompp with the topology file still containing the posre.itp include statement. Do we need to manually delete these for the production md or is it ignored...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Krabfinder](https://gromacs.bioexcel.eu/u/Krabfinder) August 13, 2020, 4:35pm 1

GROMACS version: 2018.1

 GROMACS modification: No

 I’m new to GROMACS so I’ve been following Dr. Lemkul’s tutorials at [mdtutorials.com](http://mdtutorials.com), in particular his lysozme tutorial. Towards the end he mentions that we need to remove the position restraints for the production md but doesn’t give any instruction on how to do that. He goes right into using grompp with the topology file still containing the posre.itp include statement. Do we need to manually delete these for the production md or is it ignored in some way in that final grompp statement that I just dont understand yet? Also, assuming that GROMACS does ignore the posre.itp file in the topology for the final grompp command (it may not, I don’t know), if I created an index of atoms that I wanted to keep restrained during the production md, how would I set it up to not ignore those position restraints? Any help would be appreciated, thanks!

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) August 13, 2020, 6:36pm 2

Position restraints are activated when using `define = -DPOSRES` to match the corresponding `#ifdef...#endif` block in the topology. The `.mdp` files for equilibration include the `define` keyword, the one for the production simulation does not. So the production simulation is unrestrained.

If you want to restrain only a subset of atoms, you need to create a new position restraint topology with `gmx genrestr` and modify the system topology file to `#include` this file, ideally under the control of a different `#ifdef` condition.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Fix coordinates of specific residues for simulationUser discussions | 1 | 471 | August 18, 2023 |  |
| Position Restraining CNT during MD ProductionUser discussionsmdrun | 1 | 373 | June 11, 2023 |  |
| Position restraints missing when .itp is printed to .topUser discussionspdb2gmx,simulation-setup | 2 | 132 | January 21, 2025 |  |
| Using positional restraints for atoms of the perimeterUser discussionsrestraints | 4 | 1479 | August 24, 2021 |  |
| Ligand position restraints inclusion statement placeUser discussions | 11 | 1764 | December 5, 2021 |  |
