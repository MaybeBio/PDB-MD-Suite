# Restrains positions issue of metal ions in protein active site

> GROMACS version:2021  GROMACS modification: Yes/No  Here post your question  Hi all,  I have prepared my metalloprotein-inhibitor model with CHARMM-GUI and need to restrains positions of Zn atoms. I have tried two different methods and got the same error for both of them:   Adding these lines into ZN2.itp file in toppar folder:  #ifdef POSRES_ZN  [ position_restraints ]  ;  i funct       fcx        fcy        fcz  10952    1    1000     1000    1000  10953    1    1000     1000    1000  #endif A...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mdp-parameters](https://gromacs.bioexcel.eu/tag/mdp-parameters), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[Zahraibt7](https://gromacs.bioexcel.eu/u/Zahraibt7) November 4, 2023, 3:36pm 1

GROMACS version:2021

 GROMACS modification: Yes/No

 Here post your question

 Hi all,

 I have prepared my metalloprotein-inhibitor model with CHARMM-GUI and need to restrains positions of Zn atoms. I have tried two different methods and got the same error for both of them:

1. Adding these lines into ZN2.itp file in toppar folder:
#ifdef POSRES_ZN
 [ position_restraints ]
 ; i funct fcx fcy fcz
 10952 1 1000 1000 1000
 10953 1 1000 1000 1000
#endif
2. Adding these lines into topol.top file:
 ; Include forcefield parameters
#include “toppar/forcefield.itp”
#include “toppar/PROA.itp”
#include “toppar/ZN2.itp”
#ifdef POSRES_ZN
#include “posre_zn.itp”
#endif
#include “toppar/LHK.itp”
#include “toppar/SOD.itp”
#include “toppar/CLA.itp”
#include “toppar/TIP3.itp”

ERROR 1 [file ZN2.itp, line 22]:

 Atom index (10952) in position_restraints out of bounds (1-1).

 This probably means that you have inserted topology section

 “position_restraints”

 in a part belonging to a different molecule than you intended to.

 In that case move the “position_restraints” section to the right molecule.

Any help/suggest will be appreciated

 Bests

 Zahra

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) November 5, 2023, 7:26pm 2

Hi Zahra,

Based on the error, it seems that your `ZN2.itp` has just one atom (or perhaps two atoms) defined in the `[ atoms ]` section following the `[ moleculetype ]` with zinc ions. In that case, you should use numbering from that `[ atoms ]` section, so if there are two atoms, use `1` and `2` instead of `10952` and `10953`.

Note that `[ atoms ]` for each molecule defined in the topology have to have numbering starting with 1, so even if your `ZN2.itp` has different numbers, make sure to renumber it.

(This is all assuming that adding position restraints to zinc atoms only is what you want to do - keep in mind it will restrain them to their spatial location, but other parts of the system will be able to move freely.)

Best,

 MW

[Zahraibt7](https://gromacs.bioexcel.eu/u/Zahraibt7) November 6, 2023, 6:00am 3

Dear Milosz,

 Hi. Thank you so much for your reply. I have used the following command line to make posre_ZN.itp file so 10952 and 10953 are related to Zn atom numbers in .gro file:

 gmx genrestr -f step3_input.gro -o posre_ZN.itp -fc 1000 1000 1000

in ZN2.itp there is only one atom:

 [ moleculetype ]

 ; name nrexcl

 ZN2 1

[ atoms ]

 ; nr type resnr residu atom cgnr charge mass

 1 ZN 751 ZN2 ZN 1 2.000000 65.3700 ; qtot 2.0

 So I have changed it to:

 [ atoms ]

 ; nr type resnr residu atom cgnr charge mass

 1 ZN 751 ZN2 ZN 1 2.000000 65.3700 ; qtot 2.0

 2 ZN 752 ZN2 ZN 1 2.000000 65.3700 ; qtot 2.0

#ifdef POSRES_ZN

 [ position_restraints ]

 ; i funct fcx fcy fcz

 1 1 1000 1000 1000

 2 1 1000 1000 1000

#endif

Using above mentioned ZN2.itp, I got this issue at the minimization step:

 Fatal error:

 number of coordinates in coordinate file (step3_input.gro, 132816)

 does not match topology (topol.top, 132818)

For more information and tips for troubleshooting, please check the GROMACS

 website at [Common Errors — GROMACS webpage https://www.gromacs.org documentation](http://www.gromacs.org/Documentation/Errors)

 Can you please let know how to fix this issue.

 I appreciate your time and consideration

 Bests

 Zahra

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) November 6, 2023, 3:53pm 4

Hi Zahra, if your ZN2.itp only had 1 atom, then it could be fine too - the name was ambiguous as there’s a ZN2 residue but that could also be 2x ZN.

Now that you made a `ZN2` molecule that has two atoms in it, your `[ system ]` directive probably contains this molecule twice, so `grompp` will think there are 2x2 = 4 Zn ions while your `.gro` has only 2. Either decrease the number of `ZN2` molecules in `[ system ]` or make your `ZN2` with one atom only.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Restraining two ZN position during minimization, equilibration and MD runUser discussionsmdp-parameters,mdrun,restraints,simulation-setup | 3 | 913 | February 20, 2023 |  |
| How to define position restrains on the two monomers of a dimer?User discussionsmdp-parameters,simulation-setup | 4 | 312 | August 6, 2024 |  |
| Problem using Position restraints for multiple groupsUser discussionssimulation-setup | 2 | 79 | March 30, 2026 |  |
| How to apply position constraint for a particular molecule?User discussions | 3 | 946 | October 4, 2022 |  |
| Position restraint out of bondsUser discussionsforcefield,mdp-parameters | 3 | 306 | March 20, 2024 |  |
