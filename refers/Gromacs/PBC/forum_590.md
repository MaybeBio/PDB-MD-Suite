# Removing pbc effect

> Hi all  I use trjconv in 3 consecutive commands to remove pbc effect, however, after a half of the trajectory I still can observe some jumps. Could you help me out with this issue?  Commands are as follows:  gmx trjconv -s md.tpr -f md.trr -o md1.trr -center -pbc whole -n index.ndx  gmx trjconv -s md.tpr -f md1.trr -o md2.trr -pbc nojump -n index.ndx  gmx trjconv -s md.tpr -f md2.trr -o md3.trr -pbc mol -ur compact -n index.ndx  Thank you.

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[marko](https://gromacs.bioexcel.eu/u/marko) July 28, 2020, 9:25pm 1

Hi all

 I use trjconv in 3 consecutive commands to remove pbc effect, however, after a half of the trajectory I still can observe some jumps. Could you help me out with this issue?

 Commands are as follows:

 gmx trjconv -s md.tpr -f md.trr -o md1.trr -center -pbc whole -n index.ndx

 gmx trjconv -s md.tpr -f md1.trr -o md2.trr -pbc nojump -n index.ndx

 gmx trjconv -s md.tpr -f md2.trr -o md3.trr -pbc mol -ur compact -n index.ndx

 Thank you.

[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) July 29, 2020, 5:51am 2> `compact` puts all atoms at the closest distance from the center of the box.
> `mol` puts the center of mass of molecules in the box

So you removed the jumping molecules in step 2, then reintroduced it again in 3.

I’d recommend taking things one step at a time, visualise it after each step, then identify exactly what you want to do.

[marko](https://gromacs.bioexcel.eu/u/marko) July 29, 2020, 3:31pm 3

Thank you for your reply. Could you give me the commands which solved the issue? I tried different ways but not effective. It takes a lot of time to test all the ways, download the trajectories and visualize them.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 29, 2020, 6:40pm 4

Does the protein you are simulating have multiple chains?

[marko](https://gromacs.bioexcel.eu/u/marko) July 29, 2020, 6:58pm 5

Yes it does. What should I do for that?

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 29, 2020, 8:53pm 6

Your commands are possibly not working because they centre the protein based on the centre of mass, which is the same point if the chains are together or wrapped over the periodic boundary conditions.

What you should try is making an index group using ‘gmx make_ndx’ that contains the atom numbers of one of the protein chains. Let’s say you name the index file “chain_index.ndx”.

Then try the following command (using your original trajectory as the input):

gmx trjconv -s md.tpr -f md.trr -n chain_index.ndx -pbc mol -ur compact -center -o md1.trr

Choose the group you made containing the atoms of one of the chains for centering and then “System” for output. Hopefully that works!

1 Like[Gmx ndx usage](https://gromacs.bioexcel.eu/t/gmx-ndx-usage/1350)[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) July 29, 2020, 10:54pm 7

For testing make a smaller trajectory, say putting out every 10th or more frames, and use that for testing.

[marko](https://gromacs.bioexcel.eu/u/marko) July 31, 2020, 4:02pm 8

I did so. It just centers chain A. Chains B and C are still apart! Would it affect the rmsd and mmpbsa calculations?

[marko](https://gromacs.bioexcel.eu/u/marko) July 31, 2020, 4:02pm 9

Yeah, I skip every 100 frames. But still takes time!

[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) July 31, 2020, 11:59pm 10

Then reduce further.

Note, you need to use the reduced trajectory for testing, not reprocess the original trajectory every time with the skip.

You really only need a couple of frames, ones that exhibit the visual artifact you are attempting to remove.

[L_k](https://gromacs.bioexcel.eu/u/L_k) September 5, 2020, 12:46pm 11

Hello [@marko](https://gromacs.bioexcel.eu/u/marko),

I have been using a similar approach to remove the pbc effect. I was wondering if you have resolved this issue. Previously, what has worked for me were the following:

1. gmx trjconv -s protein.tpr -f protein.xtc -o protein.whole.xtc -pbc whole
2. gmx trjconv -s protein.tpr -f protein.whole.xtc -o protein.whole.nojump.xtc -pbc nojump
3. gmx trjconv -s protein.tpr -f protein.whole.nojump.xtc -o protein.whole.nojump.mol.xtc -pbc mol -center

But I have reached a point where these are no longer working and there are jumps. I was wondering what your final approach to resolving this is?

Thank you.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) December 10, 2020, 9:44am 12

Hi,

 what about to try

1. -nojump
2. -center

Best regards

 Alessandra

[Jumping residue after PBC removal](https://gromacs.bioexcel.eu/t/jumping-residue-after-pbc-removal/9818/12)[L_k](https://gromacs.bioexcel.eu/u/L_k) December 28, 2020, 7:46pm 13

Hello [@alevilla](https://gromacs.bioexcel.eu/u/alevilla) ,

Thank you, this worked for some of the files but now I am running into a similar error. This time, -pbc whole helped to resolve this but now -pbc whole will not make my protein whole. Essentially, my protein is split in half and after applying whole there is still only two halves. And then if I apply nojump or cluster there is a split down the center of my protein causing calculation errors. Have you run into any similar issues before?

Again, thank you for the help in my previous post!

[pragya004](https://gromacs.bioexcel.eu/u/pragya004) April 3, 2023, 5:40pm 14

[@marko](https://gromacs.bioexcel.eu/u/marko) Could you please tell me how you were able to resolve this PBC issue. As I am also facing a similar issue after removing the PBC condition at certain frames, specific two chains along with ligand are jumping out. How did you resolve this issue? Please share.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBCs in a slightly complex systemUser discussionspbc | 7 | 132 | September 15, 2026 |  |
| Jumping residue after PBC removalUser discussionspbc,gmx-trjconv | 13 | 788 | August 26, 2024 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3637 | October 25, 2022 |  |
| Pbc effect removalUser discussions | 2 | 1566 | December 4, 2020 |  |
| Removing PBC for peptide-lipid systemUser discussionsgmx-trjconv | 8 | 2260 | November 3, 2024 |  |
