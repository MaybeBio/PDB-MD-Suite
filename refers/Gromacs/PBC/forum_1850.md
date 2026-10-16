# Starting simulation from another trajectory using -t grompp option - How are PBC treated?

> GROMACS version: 2018.8  GROMACS modification: No  Hello,  I have a question regarding the treatment of periodic boundary conditions in a special case.  I am performing multiple simulations of a protein-ligand system which are always started from the last position of another trajectory (there is a reason for it). I am using the -t option in grompp to do so.  Now my question: If the ligand is jumping across boundaries in the first simulation then it can be on the “wrong” side of the protein in th...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[grompp](https://gromacs.bioexcel.eu/tag/grompp), [pbc](https://gromacs.bioexcel.eu/tag/pbc)[NickK](https://gromacs.bioexcel.eu/u/NickK) March 29, 2021, 10:24am 1

GROMACS version: 2018.8

 GROMACS modification: No

 Hello,

I have a question regarding the treatment of periodic boundary conditions in a special case.

 I am performing multiple simulations of a protein-ligand system which are always started from the last position of another trajectory (there is a reason for it). I am using the -t option in grompp to do so.

 Now my question: If the ligand is jumping across boundaries in the first simulation then it can be on the “wrong” side of the protein in the last frame which I am using as a starting position for the next run. Does grompp consider this when using the -t option? So is the information about periodic boundaries stored in the .trr file or only in the .tpr file?

 In the end I combine all trajectories in a Markov state model and need to treat periodic boundary conditions beforehand. If the ligand is now on different sides of the protein and in the new trajectory the information about the “jump” across boundaries in a previous trajectory is not known I generate states in phase-space which actually not have been sampled which would be a great problem.

 I searched the forum but could not find the information I am seeking so I hope you can help me with this.

Best regards,

 Nicolas

[hess](https://gromacs.bioexcel.eu/u/hess) March 30, 2021, 12:44pm 2

In MD there is no “side of the protein”. The system is periodic. You can not be sampling incorrect states because of PBC jumps. It sounds that the problem you are having is a post-processing problem. That problem can likely be fixed using gmx trjconv -pbc nojump

[NickK](https://gromacs.bioexcel.eu/u/NickK) March 30, 2021, 12:55pm 3

Thank you very much for your reply. But I think I wrongly explained my issue then. I do know how to treat PBC for analysis but my issue is a bit more specific.

I am doing unbinding simulations and I guess here it is a problem when the molecule jumps along box edges since I have not one long simulation but multiple short ones which depend on each other. It would be easy to treat PBCs with the tools provided in GROMACS if I would have one long simulation.

 But I am performing special simulations (parallel cascade selection MD) where I perform short simulations, take the snapshots where the inter-COM distance between protein and ligand is highest and then use these as starting positions for the next simulation where the atoms get new velocities.

The problem I am facing now is: If the ligand “jumps” and I take a snapshot of the trajectory (without directly treating PBCs), then I have a different structure than without the jump. What I am wondering now is if the PBC information is stored in the .trr file or not and if grompp utilizes this information when providing the starting positions using the -t option and a .trr file. If yes I have no issues. If not I have starting positions which actually never have been sampled in that sense. E.g. the protein and the ligand are 3 nm away, then the ligand jumps to the next periodic image and lands “on the opposite side” of the protein. If I calculate the distance now it is maybe only 2nm for example.

So I know how to treat periodic boundary conditions but if I take a starting structure which has not been treated I likely get issues.

 If the trr file does not store PBC information I have to perform PBC treatment after every short simulation. And one never knows if this works correctly. In order to check this one has to visualize every trajectory which is not possible if you have multiple hundreds.

I hope I could explain the issue in more detail now.

[NickK](https://gromacs.bioexcel.eu/u/NickK) March 30, 2021, 12:57pm 4

One short further explanation:

 If the PBC information is not stores than the new simulation does not know about the movement over the periodic boundaries anymore and thus my distance calculations are wrong.

But I guess the issue is then rather a too small box size.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Periodic Boundary Conditions Error, Molecule Trajectory Collapses to 2DUser discussions | 2 | 493 | February 20, 2024 |  |
| Fixing periodic boundary conditions distance artefactsUser discussions | 1 | 1598 | November 17, 2020 |  |
| Importance of .tpr file for generating trajectoriesUser discussionsanalysis-tools | 11 | 1651 | May 10, 2022 |  |
| Removing jumps from the simulation trajectoryUser discussions | 18 | 1560 | June 28, 2024 |  |
| Jumping residue after PBC removalUser discussionspbc,gmx-trjconv | 13 | 787 | August 26, 2024 |  |
