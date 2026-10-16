# PBC correction during Umbrella sampling configuration generation

> Dear gromacs users, I am working on a protein ligand umbrella sampling simulation. I have run a steered MD simulation to steer the ligand more and more away from the ligand binding site and dumped the snapshots or configurations for a range of the reaction coordinate. However, while dumping the snapshots from the steered MD trajectory I have done trjconv PBC correction. But I see in Dr. Lemkul’s tutorial, PBC correction has not been done just to generate configurations for umbrella sampling. My ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[grompp](https://gromacs.bioexcel.eu/tag/grompp), [gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[mjm91](https://gromacs.bioexcel.eu/u/mjm91) May 17, 2023, 4:09am 1

Dear gromacs users, I am working on a protein ligand umbrella sampling simulation. I have run a steered MD simulation to steer the ligand more and more away from the ligand binding site and dumped the snapshots or configurations for a range of the reaction coordinate. However, while dumping the snapshots from the steered MD trajectory I have done trjconv PBC correction. But I see in Dr. Lemkul’s tutorial, PBC correction has not been done just to generate configurations for umbrella sampling. My question is: Is it okay to have done the PBC correction for obtaining configurations for umbrella sampling or gromacs does not actually care about whether or not the given structure is PBC corrected or not and removes the PBC automatically while running a simulation? I have done PBC corrections on the snapshots and then generated the corresponding tpr files that I have used for subsequent umbrella sampling simulations. I am just trying to clear my doubt regarding this procedure, any help will be much appreciated, thank you.

[hess](https://gromacs.bioexcel.eu/u/hess) May 19, 2023, 8:47am 2

I don’t know exactly what you mean with PBC correction. But mdrun does not care at all about in which periodic image atoms reside in the input structure.

[mjm91](https://gromacs.bioexcel.eu/u/mjm91) May 19, 2023, 10:31am 3

Thank you for your reply Prof. Hess. What I did is actually use simple trjconv -pbc mol -center on the my protein-ligand steered MD trajectory and then dumped individual configurations for umbrella sampling.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Unable to correct PBC effect of MD trajectory of a tetrameric protein + ligandUser discussions | 3 | 772 | January 3, 2024 |  |
| Is PBC correction needed before Peak force, total work, RMSD analysis and trajectory visualization?User discussions | 1 | 75 | May 2, 2026 |  |
| Removing PBC before gromppUser discussions | 5 | 511 | July 24, 2020 |  |
| Is PBC correction necessary for some particular type of analysis?User discussionspbc,analysis-tools,gmx-trjconv | 2 | 1227 | May 30, 2023 |  |
