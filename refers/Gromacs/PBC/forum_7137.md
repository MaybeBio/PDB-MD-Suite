# RMSD with trjconv and -pbc no

> Hi All,  My system contains polymers and water. I want to calculate the RMSD of polymer chains after the simulation. For this purpose, I used the following commands.  A i) gmx trjconv -f md01.tpr -f md01.xtc -o md01_nopbc.xtc -pbc nojump  ii) gmx rms -s md01.tpr -f md01_nopbc.xtc -o rmsd_chainA.xvg -n index.ndx -tu ns  Also, I tried with the following command separately (didn’t do any trjconv).  B) gmx rms -s md01.tpr -f md01.xtc -o rmsd_ChainA_2.xvg -n index.ndx -tu ns -pbc no  I removed the pb...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools)[amaligg](https://gromacs.bioexcel.eu/u/amaligg) September 6, 2023, 1:28pm 1

Hi All,

My system contains polymers and water. I want to calculate the RMSD of polymer chains after the simulation. For this purpose, I used the following commands.

A i) gmx trjconv -f md01.tpr -f md01.xtc -o md01_nopbc.xtc -pbc nojump

 ii) gmx rms -s md01.tpr -f md01_nopbc.xtc -o rmsd_chainA.xvg -n index.ndx -tu ns

Also, I tried with the following command separately (didn’t do any trjconv).

B) gmx rms -s md01.tpr -f md01.xtc -o rmsd_ChainA_2.xvg -n index.ndx -tu ns -pbc no

I removed the pbc conditions in A (using trjconv) and B (using -pbc no) methods (as per my understanding, please correct me if I am wrong). Yet, I got two different graphs for RMSD.

Appreciate your help in understanding this.

Thank you.

Best regards

 Amali

[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) October 3, 2023, 7:58am 2

`gmx rms` with `-pbc no` means that you are not taking periodic boundary conditions into account. That would probably work after having run your `trjconv` command, but not without it.

I think (but cannot promise) that you would get similar results with:

```
A i) gmx trjconv -f md01.tpr -f md01.xtc -o md01_nopbc.xtc -pbc nojump
ii) gmx rms -s md01.tpr -f md01_nopbc.xtc -o rmsd_chainA.xvg -n index.ndx -tu ns -pbc no
```

and

```
B) gmx rms -s md01.tpr -f md01.xtc -o rmsd_ChainA_2.xvg -n index.ndx -tu ns
```

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBC effect on RMSD calculationUser discussionspbc,analysis-tools,gmx-trjconv | 2 | 142 | October 1, 2025 |  |
| How to fix RMSD analysis results?User discussionsgmx-trjconv | 7 | 709 | November 5, 2023 |  |
| RMSD shoots upUser discussions | 18 | 1941 | May 5, 2026 |  |
| PBC artifact issueUser discussionsforcefield,pbc,simulation-setup | 0 | 85 | April 12, 2025 |  |
| Rmsd calculation using gmx rmsUser discussions | 4 | 155 | February 18, 2025 |  |
