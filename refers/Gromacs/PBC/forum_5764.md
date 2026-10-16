# Gmx editconf -pbc not removing periodicity

> GROMACS version: 2023  GROMACS modification: No  Hi,  I used gmx editconf -pbc to remove the periodicity of a slab of liquid water. However, it seems to only remove the periodicity of single molecules.       As you can see, there’s a layer of water outside the pbc box that doesn’t get mapped inside the pbc box.  Is the command supposed to work like that? Is there a way to remove the periodicity for the whole system and not just single molecules?

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools)[MichelePellegrino](https://gromacs.bioexcel.eu/u/MichelePellegrino) February 9, 2023, 12:37pm 1

GROMACS version: 2023

 GROMACS modification: No

Hi,

I used `gmx editconf -pbc` to remove the periodicity of a slab of liquid water. However, it seems to only remove the periodicity of single molecules.

[![before-pbc](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/2/25d82ec0d5b32e3241cff4ac44c9330c44242e3a_2_470x500.jpeg)before-pbc1920×2040 257 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/2/25d82ec0d5b32e3241cff4ac44c9330c44242e3a.jpeg)

[![after-pbc](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/4/4c1fb544143dccb8d249c1d5134355de2c287111_2_470x500.jpeg)after-pbc1920×2040 289 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/4/4c1fb544143dccb8d249c1d5134355de2c287111.jpeg)

As you can see, there’s a layer of water outside the pbc box that doesn’t get mapped inside the pbc box.

Is the command supposed to work like that? Is there a way to remove the periodicity for the whole system and not just single molecules?

[hess](https://gromacs.bioexcel.eu/u/hess) February 17, 2023, 9:41pm 2

The -pbc option of editconf only makes molecules whole. trjconv has a lot more pbc options and some of them do what you want.

[Maria_Milanesi](https://gromacs.bioexcel.eu/u/Maria_Milanesi) November 17, 2023, 6:06pm 3

Hello,

I was wondering if you eventually resolved the issue you’re facing. I’ve noticed that the behavior of water in my system is similar to what you described in your system.

I’m concerned because, starting the minimisation step, it abruptly stops with the following error:

“There are inconsistent shifts over periodic boundaries in a molecule type consisting of 4 atoms. The longest distance involved in such interactions is 1.601 nm, which is above half the box length. This molecule type consists of multiple parts, such as monomers, connected by interactions that are not chemical bonds, for example, restraints. Such systems cannot be treated. The only solution is increasing the box size.”

I’ve read through all the discussions on this error, but I don’t understand why it’s happening. I suspect that the “molecule consisting of 4 atoms” is the tip4 water model that I’m using. Perhaps solving the issue of the water layer may address this larger problem.

If there are any other suggestions, please help me in resolving this issue. If needed, I’ll send all the files used to generate the system.

Thank you very much.

[MichelePellegrino](https://gromacs.bioexcel.eu/u/MichelePellegrino) November 17, 2023, 11:08pm 4

Hi,

It was some time ago, but if I remeber correctly I used ´trjconv´ with ´-pbc nojump´ to remove periodicity.

 However, I never got the type of message you are reporting, at least not for this system. Usually I “just” get a bunch of LINCS warnings when trying to minimize systems with “untreated periodiciy” or with free interfaces.

[hess](https://gromacs.bioexcel.eu/u/hess) November 18, 2023, 9:27am 5

Does this happen at minimization step 0? In that case it could be that you have (near) overlapping atoms and one jumps away very far. If that’s the case, lowering the step size should help.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Issue: Unable to Remove PBC in GROMACS Using trjconv OptionsUser discussionsgmx-trjconv | 1 | 189 | March 24, 2025 |  |
| Algorithm Gromacs used for removing periodic boundary conditionUser discussionsanalysis-tools | 6 | 2063 | November 3, 2022 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Find error while using trjconvUser discussions | 7 | 210 | September 24, 2024 |  |
| My production file - periodic boundaryUser discussions | 0 | 64 | February 5, 2025 |  |
