# PBC correction doesn't remove all PBCs

> GROMACS version: 2021.4  GROMACS modification: No  Hi,  I can’t correct the PBC of my system after the MD simulation. My system includes a monomer protein, POPC membrane bilayer, and ligand.  It was relatively stable and didn’t show any other problems in VMD.  Based on Terminology — GROMACS 2022.3 documentation.  My commands:  gmx trjconv -f step7.gro -s step7.tpr -o step7whole.xtc -n indexPL.ndx -pbc whole -b 110000 -e 210000  System(0)  I didn’t use the cluster command.  gmx trjconv -f step7wh...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[pbc](https://gromacs.bioexcel.eu/tag/pbc), [gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[Parisa_Dashtestani](https://gromacs.bioexcel.eu/u/Parisa_Dashtestani) November 2, 2022, 8:26pm 1

GROMACS version: 2021.4

 GROMACS modification: No

Hi,

I can’t correct the PBC of my system after the MD simulation. My system includes a monomer protein, POPC membrane bilayer, and ligand.

 It was relatively stable and didn’t show any other problems in VMD.

Based on [Terminology — GROMACS 2022.3 documentation](https://manual.gromacs.org/current/user-guide/terminology.html#suggested-workflow).

My commands:

gmx trjconv -f step7.gro -s step7.tpr -o step7whole.xtc -n indexPL.ndx -pbc whole -b 110000 -e 210000

 System(0)

I didn’t use the cluster command.

gmx trjconv -f step7whole.xtc -s step72.tpr -o step7noPBC.xtc -n indexPL.ndx -pbc nojump

 System(0)

gmx trjconv -f step7noPBC.xtc -s step72.tpr -o final2.xtc -n indexPL.ndx -pbc mol -center

 Protein and ligand as the center, write output into System (0)

I also read this topic [Correcting Periodicity in GMX](https://gromacs.bioexcel.eu/t/correcting-periodicity-in-gmx/165). But it didn’t help.

The commands reduced my PBC, but I still see them in the final file frames.

I appreciate any kinda help. Thanks!

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Unable to correct PBC effect of MD trajectory of a tetrameric protein + ligandUser discussions | 3 | 771 | January 3, 2024 |  |
| Issue: Unable to Remove PBC in GROMACS Using trjconv OptionsUser discussionsgmx-trjconv | 1 | 188 | March 24, 2025 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 201 | January 15, 2025 |  |
| Correcting Periodicity in GMXUser discussions | 9 | 6575 | May 28, 2020 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3636 | October 25, 2022 |  |
