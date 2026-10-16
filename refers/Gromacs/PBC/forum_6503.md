# Is PBC correction necessary for some particular type of analysis?

> Dear gromacs users,  This is more of a general question I have regarding removal of PBC effects from simulation trajectory. I have seen that some of the online tutorials mention the removal of PBC for analysis and some of the tutorials use raw production MD trajectory for further analysis without correcting the trajectory for PBC. Some of the tools such as: gmx rms, rmsf, distance etc., already contain some PBC related options. My question: Is removal of PBC necessary only for visualization purp...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[pbc](https://gromacs.bioexcel.eu/tag/pbc), [analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools), [gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[mjm91](https://gromacs.bioexcel.eu/u/mjm91) May 28, 2023, 11:54am 1

Dear gromacs users,

This is more of a general question I have regarding removal of PBC effects from simulation trajectory. I have seen that some of the online tutorials mention the removal of PBC for analysis and some of the tutorials use raw production MD trajectory for further analysis without correcting the trajectory for PBC. Some of the tools such as: gmx rms, rmsf, distance etc., already contain some PBC related options. My question: Is removal of PBC necessary only for visualization purpose and analyses can surely be performed without removal of PBC or For some analysis PBC removal is necessary?

In this regard I have one more question. I am currently trying to simulate a peptide in presence of a micelle. I want to calculate the com-to-com (center of mass) distance between the peptide and micelle. Now for doing this I can use gmx distance. Shall I use gmx distance on the raw trajectory or the PBC corrected trajectory? Here when I refer to micelle center of mass that means center of mass of all surfactant molecules that together constitute the micelle.

 Any help would be much appreciated.

[Karis](https://gromacs.bioexcel.eu/u/Karis) May 30, 2023, 6:09pm 2

PBC correction is necessary for analysis, calculations of rms, rmsf, distance, etc don’t account for the displacement due to PBC so not correcting for it will give you inaccurate results.

In the case of gmx distance, while you should definitely use PBC corrected trajectories when analyzing the data, I’ve actually found that sometimes the PBC-corrected trajectories would still not account for all PBC effects entirely ([Atom to atom distance measured by gmx distance command is larger than measured in VMD](https://gromacs.bioexcel.eu/t/atom-to-atom-distance-measured-by-gmx-distance-command-is-larger-than-measured-in-vmd/4354)), possibly due to some incorrect option I’d chosen for -pbc, so I usually include ‘-pbc no’ in the gmx distance command as well

[mjm91](https://gromacs.bioexcel.eu/u/mjm91) May 30, 2023, 11:50pm 3

Thank you for your suggestion. However, I think that while using gmx distance to calculate the distance between two different molecules, we can keep the -pbc yes option; If we don’t do that it may happen that some interactions we can miss as trjconv PBC correction simply makes the molecules whole and puts them in the box, but if distance between two molecules are greater than the half box length, then the distance between image particles need to be considered to account for the boundarylessness or to mimic infinite boundaryless system. Having said that, if we need to calculate the end-to-end distance of a same protein or the distance between two residues, then probably -pbc no would be better option as we are calculating the distance between two residues of a single molecule, so applying PBC or minimum image convention does not make much sense in that case.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Is PBC correction needed before Peak force, total work, RMSD analysis and trajectory visualization?User discussions | 1 | 75 | May 2, 2026 |  |
| -pbc flag in hbond calculation not workingUser discussions | 12 | 420 | July 2, 2024 |  |
| On computing distances between COMsUser discussions | 2 | 162 | December 13, 2024 |  |
| Large differences in gmx mindist values with and without PBC correctionUser discussions | 5 | 153 | November 25, 2025 |  |
| Pbc effect removalUser discussions | 2 | 1565 | December 4, 2020 |  |
