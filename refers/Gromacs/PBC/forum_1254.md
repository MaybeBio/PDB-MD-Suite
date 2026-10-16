# PBC correction for drug–lipid bilayer system (GROMACS 2024.5)

> Dear GROMACS users,  I am working with a drug–membrane lipid bilayer system simulated for 500 ns using GROMACS 2024.5 (no modifications). I would like to apply PBC corrections to obtain a proper trajectory for analysis.  I first made broken molecules whole:  gmx trjconv -s prod.tpr -f prod.xtc -o pbc_whole.xtc -pbc whole  Then I centered the system around an atom close to the center of mass:  gmx trjconv -s prod.tpr -f pbc_whole.xtc -o pbc_center1.xtc -center -n center.ndx  However, I still obse...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[pbc](https://gromacs.bioexcel.eu/tag/pbc), [analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[Bhara](https://gromacs.bioexcel.eu/u/Bhara) August 19, 2025, 5:15pm 1

Dear GROMACS users,

I am working with a drug–membrane lipid bilayer system simulated for 500 ns using GROMACS 2024.5 (no modifications). I would like to apply PBC corrections to obtain a proper trajectory for analysis.

I first made broken molecules whole:

 gmx trjconv -s prod.tpr -f prod.xtc -o pbc_whole.xtc -pbc whole

Then I centered the system around an atom close to the center of mass:

 gmx trjconv -s prod.tpr -f pbc_whole.xtc -o pbc_center1.xtc -center -n center.ndx

However, I still observe that the drug molecule occasionally jumps between the upper and lower leaflets, even though the water and bilayer remain consistent with the first frame.

I also tried the following options, but the issue persists:

- gmx trjconv with -pbc nojump
- gmx trjconv with -pbc mol

Could you kindly suggest the correct procedure for handling PBC corrections in such drug–bilayer systems?

Thank you for your guidance.

Mohan

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBC correction for ionisable lipid–lipid bilayer system (GROMACS 2025.4)User discussionsanalysis-tools,gmx-trjconv | 0 | 47 | July 10, 2026 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 201 | January 15, 2025 |  |
| Removing PBC for peptide-lipid systemUser discussionsgmx-trjconv | 8 | 2259 | November 3, 2024 |  |
| Removing jumps from the simulation trajectoryUser discussions | 18 | 1560 | June 28, 2024 |  |
