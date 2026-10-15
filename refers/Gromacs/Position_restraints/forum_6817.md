# Position restraints on two ligands

> GROMACS version: 2020.3  I have a system comprising an enzyme, a coenzyme, and a substrate. Due to certain circumstances (such as clashes within the system), I need to apply restrictions on both the coenzyme and the substrate. My objective is to ensure these two ligands remain stable and unaltered. However, despite implementing restraints, one of the ligands still experiences distortion.  I am seeking guidance on how to properly enforce these restraints.  Thank you

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Rochik](https://gromacs.bioexcel.eu/u/Rochik) July 12, 2023, 12:32pm 1

GROMACS version: 2020.3

 I have a system comprising an enzyme, a coenzyme, and a substrate. Due to certain circumstances (such as clashes within the system), I need to apply restrictions on both the coenzyme and the substrate. My objective is to ensure these two ligands remain stable and unaltered. However, despite implementing restraints, one of the ligands still experiences distortion.

I am seeking guidance on how to properly enforce these restraints.

 Thank you

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) July 26, 2023, 8:07am 2

Hi,

 First, you could check that the position restraints files are properly included in the topology file. You should have a file for the coenzyme and of for the substrate. Each position restrain file has to be included under the corresponding `[ moleculetype ]` directives. In your case in the `[ moleculetype ]` directives of substrate and coenzyme. Then you could check that mdp file call both of them properly.

I also understood that the enzyme does not have position restraints. Do you observe that in your simulations?

In principle you can modify the position restraints file and apply higher force, but that should not be the case for a standard biomolecular system

I hope it helps

 Alessandra

[Rochik](https://gromacs.bioexcel.eu/u/Rochik) July 26, 2023, 8:42am 3

Thank you Alessandra,

 The enzyme does not have position restraints because I want to do just an energy minimization to remove the clashes between the enzyme and the substrate. I don’t want to change the orientation of the substrate and the coenzyme with respect to each other. What if I keep those molecules frozen and let just the enzyme change?

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) July 26, 2023, 9:28am 4

Hi.

 I think that position restraint is what you want to achieve your aim.

 I understood that you see distortion in one of the two ligands.

 For this reason I asked to check that position restraints were properly implemented. Maybe you are restraining other part of the systems (protein and one ligand) and not the two ligands.

Which type of distortion in the ligand do you observe? Which atoms do you position restraints in the ligand?

Kind regards

 Alessandra

[Rochik](https://gromacs.bioexcel.eu/u/Rochik) July 26, 2023, 1:00pm 5

the substrate is a pigment with a tetrapyrrole ring which should be planar, but after the energy minimization, it gets distorted.

 This is the way that I prepared the posre files:

 gmx genrestr -f lg1.gro -o posre_lg1.itp -fc 1000 1000 1000

 gmx genrestr -f lg2.gro -o posre_lg2.itp -fc 1000 1000 1000

 I checked the posre files. The files don’t have any problem. I also checked the topology file. This is the section before [moleculetype]:

; Include forcefield parameters

#include “amber99sb.ff/forcefield.itp”

; Include ligands topology

#include “lg1.itp”

; ligand position restraints

#ifdef POSRES

#include “posre_lg1.itp”

#endif

; Include ligands topology

#include “lg2.itp”

; ligand position restraints

#ifdef POSRES

#include “posre_lg2.itp”

#endif

[moleculetype]

Thank you

[Karis](https://gromacs.bioexcel.eu/u/Karis) July 27, 2023, 10:10am 6

Were the position restraints included in minim.mdp?

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Steepest descent (SD) with protein restraint?User discussions | 6 | 586 | February 23, 2024 |  |
| How to define position restrains on the two monomers of a dimer?User discussionsmdp-parameters,simulation-setup | 4 | 312 | August 6, 2024 |  |
| Position restraint problemUser discussions | 1 | 82 | July 30, 2025 |  |
| Ligand position restraints inclusion statement placeUser discussions | 11 | 1764 | December 5, 2021 |  |
| Restraining two ZN position during minimization, equilibration and MD runUser discussionsmdp-parameters,mdrun,restraints,simulation-setup | 3 | 913 | February 20, 2023 |  |
