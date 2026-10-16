# PBC consideration during mindist calculation

> Dear all  I had submitted an all atom md simulation for two docked(using HDOCK Server) protein stretches containing 103 and 9 residues.As per my knowledge during mindist calculation it automatically consider PBC but when I am calculating mindist between two protein chains I am getting a large jump in distance even when  I am using PBC yes.Can any one suggest  a solution for this ?

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Devid](https://gromacs.bioexcel.eu/u/Devid) April 6, 2024, 7:02am 1

Dear all

 I had submitted an all atom md simulation for two docked(using HDOCK Server) protein stretches containing 103 and 9 residues.As per my knowledge during mindist calculation it automatically consider PBC but when I am calculating mindist between two protein chains I am getting a large jump in distance even when I am using PBC yes.Can any one suggest a solution for this ?

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/9/93b2304683102c52059a121dbc578cba668e35d4_2_612x500.png)image945×772 52.9 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/9/93b2304683102c52059a121dbc578cba668e35d4.png)[Seyilaxa](https://gromacs.bioexcel.eu/u/Seyilaxa) April 6, 2024, 9:16am 2

That’s unusual if the trajectory is normal. You might need to observe the trajectory to determine what happened at the jump point, and then try the solution based on this.

[Devid](https://gromacs.bioexcel.eu/u/Devid) April 9, 2024, 11:54am 3

Hi Seyilaxa

 As per my observation trajectory is looking fine.I have calculated mindist using the command

 gmx_mpi mindist -f complex_500dt.xtc -s em.tpr -n index.ndx -od mindist_chA_chB

 I found the first during time scale from 205ns to 206ns i.e 0.19nm to 1.27nm(snapshot attached)

[![205-206ns](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/e/e8c8a36d02bbf9878d67a3acea4acf37bdcca69e_2_690x388.jpeg)205-206ns1280×720 39.5 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/e/e8c8a36d02bbf9878d67a3acea4acf37bdcca69e.jpeg)

I have tried following steps for pbc correction as per suggestions given by different peoples

 First I tried to centerd and then fitted by these commands

 gmx_mpi trjconv -s em.tpr -f complex_dt500.xtc -o centered.xtc -center -pbc mol -ur compact(selecting 1 - Protein and 0 - system for output

 gmx_mpi trjconv -s em.tpr -f centered.xtc -o fitted.xtc -fit rot+trans(selecting 4 - Backbone)

By using these out I have calculated mindist between these protein chains but I found these jump again.

 Then I have tried these commands

 gmx_mpi trjconv -s em.tpr -f complex_dt500.xtc -o whole.xtc -pbc whole

 gmx_mpi trjconv -s em.tpr -f whole.xtc -o whole_nojump -pbc nojump

 gmx_mpi trjconv -s em.tpr -f whole_nojump.xtc -o whole_nojump_mol.xtc -pbc mol

Then also I didn’t get any fruitful results.

 After that I have gone through this link [GitHub - BartBruininks/mdvwhole: Density based object completion over PBC.](https://github.com/BartBruininks/mdvwhole) and follwed the steps then also didn’t found the pbc correction and still getting such jump during mindist calculation.

[Seyilaxa](https://gromacs.bioexcel.eu/u/Seyilaxa) April 9, 2024, 12:46pm 4

I think you should show the box and determine whether the separation caused by PBC or the protein and peptide are exactly separated.

[Devid](https://gromacs.bioexcel.eu/u/Devid) April 10, 2024, 7:44am 5[![205-206ns_PBC](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/b/b291b662680797da26616c5b95ddb2f50e2d4d26_2_690x388.jpeg)205-206ns_PBC1280×720 68.2 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/b/b291b662680797da26616c5b95ddb2f50e2d4d26.jpeg)

 I am getting a jump of 1.08nm for a 1ns i.e from 205ns to 206ns.Is such separation for a single ns acceptable ?[Seyilaxa](https://gromacs.bioexcel.eu/u/Seyilaxa) April 10, 2024, 11:06am 6

It depends on your research objective. If you want to confirm the complex’s stability by MD simulation, you should at least provide a reasonable viewpoint to explain the separation like these.

[Devid](https://gromacs.bioexcel.eu/u/Devid) April 12, 2024, 9:31am 7[![555_556](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/7/71bb981159eb9c2f7a34a7e7eea43116f088c220_2_690x388.jpeg)555_5561280×720 39.5 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/7/71bb981159eb9c2f7a34a7e7eea43116f088c220.jpeg)

 I was thinking that the jump is due to PBC but it’s not because of PBC.It’s becomes closer after certain times.In literature it is found that it bounds but during MD simulation I am getting such separation.I want to check the stability of the binding of the complex.Is there any other possible reasons for this separation.[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) April 12, 2024, 9:36am 8

Perhaps it’s just an ordinary unbinding event. I guess the peptide is moving freely in the solution after separating from the protein. If you simulate long enough (could be very long) it may bind again.

[Seyilaxa](https://gromacs.bioexcel.eu/u/Seyilaxa) April 12, 2024, 1:14pm 9

There might be many reasons for this.

 First, the simulation result largely depends on whether your initial complex structure is stable or not. Mostly, the crystall structure obtained through experment will be more credible than the docking result. So if you use the molecules docking to get the initial complex, you might need to try more docking result.

 Additionally, sometimes the randomly generated speed can lead to an unstable initial strucure, so changing the seed and repeating the simulation from different initial structure may change the simulation result. Before that, make sure your forcefied is chosen reasonably to exclude the reason caused by forcefield parameters.

 Finally, ligands and protein also do not always be bound in reality. Perhaps you just get the separation process. Extending the simulation time may demonstrate the stability and trend of binding from the time of binding and separation, but the time needs to be extended is unknown (maybe far beyond the time you can accept ).

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Large differences in gmx mindist values with and without PBC correctionUser discussions | 5 | 153 | November 25, 2025 |  |
| Regarding usage of -pbc yes while calculating mindistUser discussions | 0 | 37 | December 5, 2025 |  |
| PBC-related jumps in protein–protein contact analysis of a Martini CG simulationUser discussions | 0 | 40 | August 12, 2026 |  |
| Mindist usage on multichain systemsUser discussionsgmx-mindist | 0 | 35 | May 11, 2026 |  |
| How to calculate mindist for complex systems?User discussions | 5 | 1836 | September 24, 2020 |  |
