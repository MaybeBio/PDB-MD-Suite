# Membrane box distorted after removing pbc

> GROMACS version: 2023.2  GROMACS modification: Yes/No  Here post your question  I have a membrane box with around 27000 atoms, which I need to add it to a water box so I can do swelling simulation. I was able to remove pbc from the water box with the following command:  gmx_mpi trjconv -f water.gro -s water.tpr -o water.gro -pbc whole  I tried doing the same thing for the membrane box, but it gave a very distorted structure.  The strange thing is that the same structure that was produced in this...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[forcefield](https://gromacs.bioexcel.eu/tag/forcefield), [grompp](https://gromacs.bioexcel.eu/tag/grompp), [mdrun](https://gromacs.bioexcel.eu/tag/mdrun), [gpu](https://gromacs.bioexcel.eu/tag/gpu), [simulation-setup](https://gromacs.bioexcel.eu/tag/simulation-setup)[Nasseralhamdani](https://gromacs.bioexcel.eu/u/Nasseralhamdani) November 2, 2023, 3:25pm 1

GROMACS version: 2023.2

 GROMACS modification: Yes/No

 Here post your question

 I have a membrane box with around 27000 atoms, which I need to add it to a water box so I can do swelling simulation. I was able to remove pbc from the water box with the following command:

 gmx_mpi trjconv -f water.gro -s water.tpr -o water.gro -pbc whole

I tried doing the same thing for the membrane box, but it gave a very distorted structure.

 The strange thing is that the same structure that was produced in this step was exactly obtained before doing an EM.

To understand better,

 The membrane went through about 20 cycles of NVT/NPT to create the box fully combat with boundary conditions. This gave a structure with the desired density but when visualized, the structure would appear very weird occupying only half of the box. But once I did an EM for the file, it produced a nicely structured box. Then when I removed the pbc with the above command, as a step to merge this membrane with the water box, I got the same weird structure again.

note that I am a beginner in Gromacs, so please forgive my poor explanation. And let me know if you need any further info.

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) November 4, 2023, 11:33am 2

Hi,

If you’re using VMD for visualization, use the “Periodic” tab in representations to add more PBC images and see if that makes sense. If you still think it is weird, post the screenshots here to better understand the problem.

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) November 6, 2023, 9:20am 4

So I’m not sure how big your membrane-forming molecule is, but `-pbc whole` just makes sure that molecules are made whole - not exactly that they are put in the desired periodic image. You can try `-pbc mol` (or `-pbc res` if the molecule is a single residue) which tries to do that besides just making them whole, but if a single molecule is large/long, it might not be physically doable.

Either way, the frame you get after the simulation has every atom placed in the central periodic image, so it shows the overall geometry of the system is correct.

Am I getting it right, you’re trying to generate an elongated box with your hydrophobic molecule only, simulate it, and then expand the box and fill the extra volume with water? If so, I don’t see a clear advantage of adding the water layer before starting the NVT/NPT cycles.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| GROMACS PBC Artifact: Protein Crossing Membrane in Visualization Despite CenteringUser discussionsanalysis-tools,simulation-setup | 5 | 658 | August 15, 2024 |  |
| System getting out of box upon simulationUser discussionsmdrun,pbc | 2 | 337 | October 29, 2024 |  |
| My production file - periodic boundaryUser discussions | 0 | 64 | February 5, 2025 |  |
| Removing PBC before gromppUser discussions | 5 | 512 | July 24, 2020 |  |
| Remove PBC effects on membrane+protein+ligandUser discussionspbc | 4 | 700 | October 20, 2022 |  |
