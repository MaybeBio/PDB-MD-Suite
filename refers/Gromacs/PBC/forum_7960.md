# Unable to correct PBC effect of MD trajectory of a tetrameric protein + ligand

> GROMACS version: 2023.2  GROMACS modification: No  Dear GMX users,  I need to remove the PBC effect of my MD trajectory to perform MM/PB(GB)SA calculations. My system is made of a tetrameric protein (dimer of dimers) with one of the monomers bound to a ligand (for the binding energy calculation). Here you can see the complex:     The issue is that I have tried several approaches suggested in this forum, but none of them has worked. For instance, here is how the unprocessed trajectory looks like ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[GuhLelouch](https://gromacs.bioexcel.eu/u/GuhLelouch) January 2, 2024, 8:09pm 1

GROMACS version: 2023.2

 GROMACS modification: No

Dear GMX users,

I need to remove the PBC effect of my MD trajectory to perform MM/PB(GB)SA calculations. My system is made of a tetrameric protein (dimer of dimers) with one of the monomers bound to a ligand (for the binding energy calculation). Here you can see the complex:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/8/8df822a837c0365825bf03923f1b6b2cb25cd686_2_359x499.png)image480×667 176 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/8/8df822a837c0365825bf03923f1b6b2cb25cd686.png)

The issue is that I have tried several approaches suggested in this forum, but none of them has worked. For instance, here is how the unprocessed trajectory looks like (I open the .gro file in PyMOL and then drop the .xtc file into it):

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/a/a915e0716de45a2e3e0a559c9c2580b1a7548d53.jpeg)image719×596 132 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/a/a915e0716de45a2e3e0a559c9c2580b1a7548d53.jpeg)

When I try to correct the PBC effect with

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC.xtc -pbc mol -center -ur compact
1 (protein) 0 (system)
```

I get:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/1/145dd1ffab529383d4dab6a1f4488cc37c7107ea.jpeg)image667×605 98 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/1/145dd1ffab529383d4dab6a1f4488cc37c7107ea.jpeg)

With

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC2.xtc -pbc mol -center
1 (protein) 0 (system)
```

I get:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/9/98091e37e79cbbbf67d61c0e8ed7230e3b9a6303.jpeg)image652×579 99.8 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/9/98091e37e79cbbbf67d61c0e8ed7230e3b9a6303.jpeg)

I created an index file with a group containing only the atoms of one of the chains, and then I centered using this group:

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC.xtc -n index_pbc.ndx -pbc mol -center -ur compact
1 (Chain_A) 0 (system)
```

This improved the situation, but the complex was not correctly centralized in the box:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/6/65d30ee8ed84a43484c9077b66d25ac277a76194.jpeg)image605×566 98.6 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/6/65d30ee8ed84a43484c9077b66d25ac277a76194.jpeg)

I tried [mdvwhole](https://github.com/BartBruininks/mdvwhole) using the command

`mdvwhole -f md_0_1.gro -x md_0_1.xtc -o whole.xtc`

but it didn’t help:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/f/f46fb9b9e5e67af6059e8dea83f30cf10a6df050.jpeg)image573×554 85.5 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/f/f46fb9b9e5e67af6059e8dea83f30cf10a6df050.jpeg)

And with

`mdvwhole -fmd_0_1.tpr -x md_0_1.xtc -mol True -o whole_sm.xtc`

the issue persisted:

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/3/3b6c1e97df2c9d0032e26132288d5e36074a7ee7.jpeg)image676×610 110 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/3/3b6c1e97df2c9d0032e26132288d5e36074a7ee7.jpeg)

I would appreciate it if anyone could suggest a possible solution for this issue.

Best regards,

Gustavo

**Edit:**

I also tried to re-center (not sure which of the options below is appropriate) the trajectory previously “centered” using a single chain:

`gmx_mpi trjconv -s md_0_1.tpr -f md_0_1_noPBC3.xtc -o md_0_1_noPBC7.xtc -center`

`gmx_mpi trjconv -s md_0_1.tpr -f md_0_1_noPBC3.xtc -o md_0_1_noPBC8.xtc -pbc mol -center`

…but no success.

I also tried the “-pbc cluster” in two different ways:

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC9.xtc -pbc cluster -center -ur compact
Cluster: 1 (Protein)
Center: 1 (Protein)
Output: 0 (System)
```

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC10.xtc -n index.ndx -pbc cluster -center -ur compact
Cluster: 21 (Protein+Ligand)
Center: 1 (Protein)
Output: 0 (System)
```

…however, this also failed.

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) January 3, 2024, 3:40pm 2

What often helps in such cases is to (1) first `-center` using a single chosen atom that is as close to the middle point of the molecule as possible so that the complex gets translated to fit inside the box, and (2) run with `-pbc mol` that will put each molecule in its nearest periodic image.

It might take a while to find the right reference atom, but as long the complex doesn’t change its shape much, it should work eventually.

[GuhLelouch](https://gromacs.bioexcel.eu/u/GuhLelouch) January 3, 2024, 4:35pm 3

Dear [milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor),

Thanks for the input.

Just to clarify: in (1), do you mean a single atom that is near the center of the complex and that is part of a single protein chain?

If that is the case, then I would need to do (starting from the unprocessed trajectory):

1. Create an index file with a group containing only that atom.

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_centered.xtc -n index.ndx -center
21 (Atom_X) 0 (system)
```

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1_centered.xtc -o md_0_1_centered_noPBC.xtc -pbc mol
0 (system)
```

Does that make sense?

Should “-ur compact” be present in any of these commands to recover the dodecahedron? Or is it something that I have to try out if the previous commands are not sufficient?

Best regards,

Gustavo

**Edit:**

The commands I proposed above didn’t work, so I tried

```
gmx_mpi trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_noPBC11.xtc -n index_atom.ndx -pbc mol -center -ur compact
21 (Atom_X) 0 (system)
```

This appears to have solved the issue (see the system below).

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/d/d6b4dde3a6cc1d8f10355c6403d88a21fc8f60fc_2_574x499.jpeg)image1545×1345 533 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/d/d6b4dde3a6cc1d8f10355c6403d88a21fc8f60fc.jpeg)

Here, “Atom_X” was a single atom near the center of the complex, in a single protein chain.

Now, I have the following questions: How do I know whether or not the complex is properly centralized? Does the centralization have to be perfect for correct analysis?

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) January 3, 2024, 7:24pm 4

Glad to see it worked!

If you plan to run an MM/PBSA calculation, then you’d usually want remove the solvent, and so the layout of the water box is irrelevant. For the solute, I’d say the most basic prerequisite for any energy calculation software is that it should be translation- and rotation- (or SE(3)-) invariant, so no, the details of centering shouldn’t affect your result at all.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Removing pbc effectUser discussions | 13 | 11165 | April 3, 2023 |  |
| Pbc effect removalUser discussions | 2 | 1565 | December 4, 2020 |  |
| PBC centering IssueUser discussions | 3 | 285 | March 25, 2026 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3636 | October 25, 2022 |  |
