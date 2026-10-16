# To get position of my molecule without pbc

> GROMACS version:  GROMACS modification: Yes/No  Here post your question  I had run a simulation of 100 ns including 1 molecule of A and 2000 molecule of B in a box size of 3.931 nm in gromacs 2020.2 with NPT equilibration run and NVT production run with pbc on and generated nvt.xtc file.  Now I want to generate a file containing position of center of mass of molecule A from initial to 3 ns without pbc (i.e. to find real coordinates of A). And I had tried the following gmx codes in order to gener...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[RamKrishna](https://gromacs.bioexcel.eu/u/RamKrishna) January 30, 2021, 4:34pm 1

GROMACS version:

 GROMACS modification: Yes/No

 Here post your question

I had run a simulation of 100 ns including 1 molecule of A and 2000 molecule of B in a box size of 3.931 nm in gromacs 2020.2 with NPT equilibration run and NVT production run with pbc on and generated nvt.xtc file.

 Now I want to generate a file containing position of center of mass of molecule A from initial to 3 ns without pbc (i.e. to find real coordinates of A). And I had tried the following gmx codes in order to generate the same:

1. gmx trajconv -f nvt.xtc -s nvt.tpr -b 0 -e 3 -tu ns -seltype mol_com -ox position_A.xvg
2. gmx trajconv -f nvt.xtc -s nvt.tpr -b 0 -e 3 -tu ns -seltype mol_com -nopbc -ox position_A_nopbc.xvg
3. gmx trajconv -f nvt.xtc -s nvt.tpr -b 0 -e 3 -tu ns -seltype mol_com -pbc no -ox position_A_pbcno.xvg
4. gmx trajconv -f nvt.xtc -s nvt.tpr -b 0 -e 3 -tu ns -seltype mol_com -pbc yes -ox position_A_pbcyes.xvg

But when I viewed these all 4 xvg files I found no any differences in the coordinates. The pbc effect was unable to nullified by (-nopbc) and (-pbc no) extensions and everytime either x or y or z coordinate reaches near to 3.931nm (box size), the coordinate suddenly jumps around 0 nm in next frame where each coordinate shift after every successive frame is less than about 0.1 nm. I am stuck in this problem.

 Help me to figure out my problem.

 Thanks in advance.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) February 1, 2021, 9:04pm 2

Hi,

 gmx trajconv is not a standard gromacs tools

 Do you mean

[gmx trjconv](https://manual.gromacs.org/current/onlinehelp/gmx-trjconv.html) or [gmx traj](https://manual.gromacs.org/current/onlinehelp/gmx-traj.html).?

Maybe [gmx trajectory](https://manual.gromacs.org/current/onlinehelp/gmx-trajectory.html) can also be useful.

Best regards

 Alessandra

[RamKrishna](https://gromacs.bioexcel.eu/u/RamKrishna) February 2, 2021, 2:21am 3

Oh I am sorry for my mistake. You are right. It is actually ‘trajectory’ not ‘trajconv’. But the other parts and my conditions are same.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| To get position of a molecule without jumpUser discussions | 2 | 1130 | February 6, 2021 |  |
| How to remove the PBC effect in the .trr file?User discussions | 1 | 425 | October 4, 2020 |  |
| Trjconv for removing pbc: -s gro does not yield expected resultUser discussions | 2 | 899 | September 14, 2020 |  |
| Removing pbc effectUser discussions | 13 | 11165 | April 3, 2023 |  |
| Fail to remove the center of mass when simulate evaporation of filmUser discussions | 4 | 372 | October 13, 2020 |  |
