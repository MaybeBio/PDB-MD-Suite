# GROMACS PBC Artifact: Protein Crossing Membrane in Visualization Despite Centering

> GROMACS version: 2023.2  GROMACS modification: No  Here post your question :  I ran a 100ns molecular dynamics simulation of a protein-membrane system where the protein is 10 angstroms away from the membrane. After concatenating the trajectory files and performing post-processing (centering the protein-membrane complex), I noticed that the protein sometimes appears to go below the membrane for some frames in the visualization (Figure 2_462thframe) from the normal orientation (figure1_461thframe)...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[smit](https://gromacs.bioexcel.eu/u/smit) August 13, 2024, 4:08pm 1

GROMACS version: 2023.2

 GROMACS modification: No

 Here post your question :

 I ran a 100ns molecular dynamics simulation of a protein-membrane system where the protein is 10 angstroms away from the membrane. After concatenating the trajectory files and performing post-processing (centering the protein-membrane complex), I noticed that the protein sometimes appears to go below the membrane for some frames in the visualization (Figure 2_462thframe) from the normal orientation (figure1_461thframe).

I’m unsure if this is an issue with the simulation itself or if I’m handling the periodic boundary conditions (PBC) incorrectly during post-processing. I’ve tried various gmx trjconv -pbc options, including -ur rect and -ur compact, but the problem persists.

Could someone please provide guidance on how to resolve this issue in GROMACS?

[![figure1_461thframe](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/b/ba8cb2fce00fa606bbaf5909cca561fd9dca49ff_2_414x500.png)figure1_461thframe618×745 184 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/b/ba8cb2fce00fa606bbaf5909cca561fd9dca49ff.png)

[![figure2_462thframe](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/d/d986ac4ed7165c55a7ce878e19b4006f77a5659d_2_414x500.png)figure2_462thframe618×745 184 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/d/d986ac4ed7165c55a7ce878e19b4006f77a5659d.png)[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) August 13, 2024, 4:24pm 2

Have you tried `gmx trjconv` in three steps:

1. -center (on the membrane)
2. -pbc whole
3. -pbc nojump

I think that should work (otherwise try switching the order of step 2 and 3). But keep in mind that this is just a matter of visualisation. If the protein should not be able to pass from one side to the other, e.g., if one leaflet is the “interior” and one is the “exterior”, possibly different in composition, you would need another mirrored bilayer to separate the two solvent volumes.

[smit](https://gromacs.bioexcel.eu/u/smit) August 14, 2024, 11:13am 3![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/magnusl/48/2380_2.png) MagnusL:> If the protein should not be able to pass from one side to the other, e.g., if one leaflet is the “interior” and one is the “exterior”, possibly different in composition, you would need another mirrored bilayer to separate the two solvent volumes

Thanks very much for the reply. Could you clarify if I should use the `-center` option along with `-pbc mol` or just use the `-center` option on its own for removing periodic boundary conditions?

 These are the commands I’m giving for the removing pbc:

 1)Command line:

 gmx trjconv -s step7_1.tpr -f 100ns.xtc -o test2.xtc -center -pbc mol -n index.ndx

Note that major changes are planned in future for trjconv, to improve usability and utility.

 Will write xtc: Compressed trajectory (portable xdr format): xtc

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Select group for centering

 Group 0 ( SOLU) has 2047 elements

 Group 1 ( MEMB) has 50960 elements

 Group 2 ( SOLV) has 100754 elements

 Group 3 ( SOLU_MEMB) has 53007 elements

 Group 4 ( SYSTEM) has 153761 elements

 Select a group: 1

 Selected 1: ‘MEMB’

 Select group for output

 Group 0 ( SOLU) has 2047 elements

 Group 1 ( MEMB) has 50960 elements

 Group 2 ( SOLV) has 100754 elements

 Group 3 ( SOLU_MEMB) has 53007 elements

 Group 4 ( SYSTEM) has 153761 elements

 Select a group: 4

 Selected 4: ‘SYSTEM’

 Reading frame 0 time 0.000

 Precision of 100ns.xtc is 0.001 (nm)

 Using output precision of 0.001 (nm)

Back Off! I just backed up test2.xtc to ./#test2.xtc.1#

 Last frame 1000 time 100000.000 → frame 999 time 99900.000

 → frame 1000 time 100000.000

 Last written: frame 1000 time 100000.000

2)Command line:

 gmx trjconv -s step7_1.tpr -f test2.xtc -pbc whole -n index.ndx

Note that major changes are planned in future for trjconv, to improve usability and utility.

 Will write xtc: Compressed trajectory (portable xdr format): xtc

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Select group for output

 Group 0 ( SOLU) has 2047 elements

 Group 1 ( MEMB) has 50960 elements

 Group 2 ( SOLV) has 100754 elements

 Group 3 ( SOLU_MEMB) has 53007 elements

 Group 4 ( SYSTEM) has 153761 elements

 Select a group: 3

 Selected 3: ‘SOLU_MEMB’

 Reading frame 0 time 0.000

 Precision of test2.xtc is 0.001 (nm)

 Using output precision of 0.001 (nm)

 Last frame 1000 time 100000.000 → frame 999 time 99900.000

 → frame 1000 time 100000.000

 Last written: frame 1000 time 100000.000

3)Command line:

 gmx trjconv -s step7_1.tpr -f test2.xtc -pbc nojump -n index.ndx

Note that major changes are planned in future for trjconv, to improve usability and utility.

 Will write xtc: Compressed trajectory (portable xdr format): xtc

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Reading file step7_1.tpr, VERSION 2023.3 (single precision)

 Select group for output

 Group 0 ( SOLU) has 2047 elements

 Group 1 ( MEMB) has 50960 elements

 Group 2 ( SOLV) has 100754 elements

 Group 3 ( SOLU_MEMB) has 53007 elements

 Group 4 ( SYSTEM) has 153761 elements

 Select a group: 3

 Selected 3: ‘SOLU_MEMB’

 Reading frame 0 time 0.000

 Precision of test2.xtc is 0.001 (nm)

 Using output precision of 0.001 (nm)

Back Off! I just backed up trajout.xtc to ./#trajout.xtc.1#

 Last frame 1000 time 100000.000 → frame 999 time 99900.000

 → frame 1000 time 100000.000

 Last written: frame 1000 time 100000.000

If I follow these steps, I don’t encounter the same problem. However, my membrane is no longer intact (

[![figure3](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/5/567e2226d16f8155c18249e77648ffa29b8b8784_2_414x500.png)figure3618×745 137 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/5/567e2226d16f8155c18249e77648ffa29b8b8784.png)

 Figure 3). Could you advise where I should make changes? I also tried changing the order (3 to 2), but the protein still shifts below the membrane…[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) August 14, 2024, 11:44am 4

I don’t think you should need `-pbc mol` in the first step.

What do you mean that your membrane is no longer intact? Isn’t it just that some residues are drifting outside the periodic box (due to `-pbc nojump`)? If you visualize the periodic images in VMD (The `Periodic` tab in `Graphical Representations`) I think it will look fine. But it might be difficult for you to prevent the protein from jumping and still having the lipids to jump.

[smit](https://gromacs.bioexcel.eu/u/smit) August 14, 2024, 2:27pm 5![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/magnusl/48/2380_2.png) MagnusL:> I don’t think you should need `-pbc mol` in the first step.
> 
> What do you mean that your membrane is no longer intact? Isn’t it just that some residues are drifting outside the periodic box (due to `-pbc nojump`)? If you visualize the periodic images in VMD (The `Periodic` tab in `Graphical Representations`) I think it will look fine. But it might be difficult for you to prevent the protein from jumping and still having the lipids to jump.

Thank you for your feedback. I have checked the visualization using the Periodic tab in VMD to verify that it appears as intended. However, I still need to understand why the lipid residues are shifting and why the protein sometimes moves outside the PBC box. Could you provide some insight into managing trajectories in these situations, especially since PBC removal can be confusing for beginners? I am finding it challenging to keep the protein within the box while allowing the lipids to move. Do you have any suggestions on handling this effectively within the constraints of periodic boundary conditions?

[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) August 15, 2024, 6:42am 6

It is not strange that the lipids are shifting and that the protein moves. Remember that the system is periodic (repeated infinitely) - atoms crossing the edge on one side enter on the other and all interactions are calculated across the periodic boundaries.

The treatments you have done using `gmx trjconv` help visualizing the system in a way you are more used to, but there is no difference in the atom locations. Making a molecule whole across periodic boundaries may definitely help the understanding. Preventing molecules from jumping can also make it easier to view a trajectory, but, as you notice, it also makes the molecules drift away from each other (in a visual representation without showing the periodic images) making it seem like there are gaps in the molecular system. I think you will learn a lot by using the periodic representation in VMD of the original trajectory and after each of the `gmx trjconv` steps you have done. I think you will understand better how it works. You can also experiment with the `-ur compact` option, but I think that helps more for systems with non-triclinic box types.

For analysis purposes, it does not make a difference what pbc treatments you have applied, but I usually recommend using the original trajectory.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Protein-Lipid system, protein keeps flipping or jumpingUser discussionsmdrun,analysis-tools,simulation-setup | 2 | 187 | April 25, 2025 |  |
| Removing PBC for peptide-lipid systemUser discussionsgmx-trjconv | 8 | 2260 | November 3, 2024 |  |
| My production file - periodic boundaryUser discussions | 0 | 64 | February 5, 2025 |  |
| PBC centering IssueUser discussions | 3 | 285 | March 25, 2026 |  |
| Removing jumps from the simulation trajectoryUser discussions | 18 | 1560 | June 28, 2024 |  |
