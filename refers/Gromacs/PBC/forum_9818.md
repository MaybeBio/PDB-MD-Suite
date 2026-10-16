# Jumping residue after PBC removal

> GROMACS version: 2022.5  GROMACS modification: No  Hi everyone, so i’m doing my first complete MD simulation and extended the prodcution run to 503ns. After finishing the simulation i used the following commands to correcet for PBC and rot- and translations:   trjconv -pbc nojump trjconv -pbc mol -center trjconv -fit rot+trans  Following this i looked at the trajectory, which seemed fine for the most part, but after about 460ns one residue jumps far away from the rest. Therefore i tried to corre...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[pbc](https://gromacs.bioexcel.eu/tag/pbc), [gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 5, 2024, 11:46am 1

GROMACS version: 2022.5

 GROMACS modification: No

 Hi everyone, so i’m doing my first complete MD simulation and extended the prodcution run to 503ns. After finishing the simulation i used the following commands to correcet for PBC and rot- and translations:

1. trjconv -pbc nojump
2. trjconv -pbc mol -center
3. trjconv -fit rot+trans
 Following this i looked at the trajectory, which seemed fine for the most part, but after about 460ns one residue jumps far away from the rest. Therefore i tried to correct this by using trjconv -pbc whole. The residue is now closer to the position it should be, but is still not in the correct positon. Any ideas on how i can fix this?

[Karis](https://gromacs.bioexcel.eu/u/Karis) August 6, 2024, 9:10am 2

Could you try visualizing the simulation at the points where the jumps are happening?

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 6, 2024, 3:45pm 3

Here is one picture of the first frame with the jumping residue. After that the residue keeps like that for a big portion of the simulation and even moves away.

[![jumping_residue.00053](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/6/6f43cd6cdd4cdd08e4a5b14cb4455ff16e6f6ee1_2_396x500.png)jumping_residue.00053672×848 99 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/6/6f43cd6cdd4cdd08e4a5b14cb4455ff16e6f6ee1.png)[Karis](https://gromacs.bioexcel.eu/u/Karis) August 7, 2024, 7:02am 4

When you say you used the 3 commands listed to correct for PBC/rot+trans, do you mean you applied them all at once or just one at a time? What was the effect from each other the corrections individually? It might help to compare those trajectories affected by each command individually to one without any correction to see what’s causing what

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 7, 2024, 11:05am 5

Since i had problems before hand i checked here and found another discussion where they used pretty much this commands. Therefore i tried them and i worked for the most part at least. So i’m currently looking at the intermediate trajectories.

 Without any correction the protein rotates after the extension of the production run and jumps around, but when looking specifically at the problematic residue it does not make this long line. Therefore it should be a problem of the commands in use.

 When i look at the nojump.xtc it looks really weird and is just full of lines so i guess thats the problematic command or is this normal?

 After using the pbc mol -center command the lines mostly vanish.

 After using the fitted command there is only one line, which is the residue in question.

 And as said before the pbc whole command did shorten this line but did not correct it completely.

 I guess the nojump command is the one making the problem. Here a picture of my protein after using nojump:

[![nojump_xtc](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/9/970387324ba31f0c7fe2c5837e5b9d5490a81fd6_2_396x500.png)nojump_xtc672×848 88.7 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/9/970387324ba31f0c7fe2c5837e5b9d5490a81fd6.png)

Before i used this command and only used pbc mol -center my protein still jumped sometimes during the trajectory. So any idea how i could fix the jumping without using nojump?

[Karis](https://gromacs.bioexcel.eu/u/Karis) August 7, 2024, 1:27pm 6

What was the problem you were trying to fix with these commands? Could you share that post you mentioned and the visualizations of the issue with each of the commands you tried (it’s hard to figure out what’s going on from verbal descriptions of VMD)?

This [page](https://manual.gromacs.org/current/onlinehelp/gmx-trjconv.html) describes what each nopbc option actually does to the simulation, it might help to take a look. Also, when you look at the unaltered trajectory, could you check the points where the proteins cross the pbc box boundaries? It might help to see what the commands are trying to fix that’s resulting in the jumping

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 7, 2024, 4:34pm 7

Well, the unaltered trajectory had two main problems and one smaller one:

 First: Sometimes the whole protein jumped back and forth, but that seems to be a common problem, which is caused by leaving the box from one side and entering from the opposite side.

 Second: The protein consists of 4 diffferent chains and sometimes a single chain jumped out of the box.

 third: after the extension starts the protein is rotated.

So first it tried to get rid of the first problem by following this tutorial ([Lysozyme in Water](http://www.mdtutorials.com/gmx/lysozyme/09_analysis.html)) and use -pbc mol -center. This did not solve my problem so i searched for a different way. i found a discussion here on gromacs forum (which i’m searching right now, but cant find it). There the suggestion was as i wrote in my first message.

 I applied the commands and it seems to have worked since the two main problems got solved. And the -fit command solved the problem of rotation which occured during the extension. But as said before the last 40ns one residue jumps around. Therefore i tried to fix it using the whole command, which did not solve my problem.

 So the visualization for nojump is in my post above.

 Visualization after center command:

[![after_center](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/c/c595d71d4e19bfa5fef478def7039619cffba6cd_2_396x500.png)after_center672×848 20.4 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/c/c595d71d4e19bfa5fef478def7039619cffba6cd.png)

Visualization after fitting:

[![after_fit](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/e/ee31c969cf2ec5542d69b06919f2fbd33a0d4b93_2_396x500.png)after_fit672×848 25.4 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/e/ee31c969cf2ec5542d69b06919f2fbd33a0d4b93.png)

Viszualisation after whole command is in my second post

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 7, 2024, 4:45pm 8

Here is an example of the unaltered trajectory where the chain are seperated:

[![unaltered_mult_chain](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/3/36e8b980b5c48ceb7705bb1d14b9825f00ccc2c7_2_396x500.png)unaltered_mult_chain672×848 17.8 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/3/36e8b980b5c48ceb7705bb1d14b9825f00ccc2c7.png)

And an example of the jumping of the whole protein. Here i put two frames into one to get a single frame showing the difference in position:

[![jump_wholeprotein](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/3/3e95c22cdd14f1ec6a5e4f6655e4369967dcf059_2_396x500.png)jump_wholeprotein672×848 51.2 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/3/3e95c22cdd14f1ec6a5e4f6655e4369967dcf059.png)[Karis](https://gromacs.bioexcel.eu/u/Karis) August 8, 2024, 5:48am 9

When you say the protein is rotated after the extension, is this to say there was some rotational motion you weren’t expecting or is it that some reflection happened over one of the axis? After extending the simulation, did you use [trjcat](https://manual.gromacs.org/current/onlinehelp/gmx-trjcat.html) to [combine the simulation with its extension](https://www.compchems.com/extend-or-continue-a-gromacs-simulation/#example) before visualizing it? I haven’t used the -fit option myself, but searching it up, it seems to be intended for essential dynamics analysis and clustering rather than fixing the visualization and you mentioned that the 2 main problems were solved before the fit command, is the rotation problem still there once you concatenate the trajectories?

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 8, 2024, 9:02am 10

No the rotation is (as far as i know) normal when extending a simulation and can be fixed with fit rot+trans. In general the Protein was just rotated in place at the first frame of the extension and got completely fixed by the command. So it is only a “one time” event when looking at the transition from production run to extension. The main problems of the whole protein jumping and parts of it jumping got also completely fixed by the commands, but i think since the nojump command had some periodic problem it left some artifacts in the trajectory which could only be seen in the last 40ns (the line of the residue).

 And yes i used trjcat to concatenate the extension and production run.

 So just to be clear i first concatenate production run and extension and then i used the trjconv commands.

[Karis](https://gromacs.bioexcel.eu/u/Karis) August 8, 2024, 1:53pm 11

Is this the [post](https://gromacs.bioexcel.eu/t/issues-when-using-fit-rot-trans/9323/5) you were referring to? They used -pbc whole in the place of -pbc nojump, does that still cause the same issues?

Also, found this [page](https://manual.gromacs.org/current/user-guide/terminology.html#suggested-workflow) in the manual which should be helpful if there are still further issues

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 8, 2024, 2:21pm 12

i think it was this post: [Removing pbc effect - #12 by alevilla](https://gromacs.bioexcel.eu/t/removing-pbc-effect/590/12)

 in particular one of the answers which suggested nojump and the center. The -fit rot+trans was one i found somewhere else.

 The suggested workflow you posted i tried before, with a similiar result to my first try. I think the problem is with the nojump command. Currently I’m making another trajectory because i think i used the center command when i was removing the solvent from the trajectory which could be the reason why nojump made problems. And thank you for your help.

[MaryumIrs](https://gromacs.bioexcel.eu/u/MaryumIrs) August 22, 2024, 1:54am 13

Did you try -pbc whole, then -pbc nojump? or -pbc cluster?

[lepersch](https://gromacs.bioexcel.eu/u/lepersch) August 26, 2024, 2:28pm 14

Sorry for the late reply. The problem was that when i removed the solvent i used -center which should not be used before the nojump command. So i tried it again, but this time with the trajectory were i removed the solvent without the center command which fixed my problem and then the suggested workflow for gromacs.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBCs in a slightly complex systemUser discussionspbc | 7 | 132 | September 15, 2026 |  |
| Removing pbc effectUser discussions | 13 | 11165 | April 3, 2023 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3636 | October 25, 2022 |  |
| Removing jumps from the simulation trajectoryUser discussions | 18 | 1560 | June 28, 2024 |  |
| Trjconv jumping DNAUser discussions | 2 | 631 | March 23, 2023 |  |
