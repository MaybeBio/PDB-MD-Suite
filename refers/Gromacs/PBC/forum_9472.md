# -pbc flag in hbond calculation not working

> GROMACS version: 2021.5  GROMACS modification: No  Hii  In my simulation box, the protein and the DNA are totally out of the boxes. I modified the trajectory with -pbc whole and -pbc nojump. Now I’m trying to calculate the hbonds between them. The distance between them is more than 4nm, and it should not make any hbonds. However I’m still getting it. I was facing similar problem with the gmx mindist but there -pbc flag worked and gave me proper distances, however in gmx hbond, -pbc flag is not w...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Sahil](https://gromacs.bioexcel.eu/u/Sahil) June 22, 2024, 7:57am 1

GROMACS version: 2021.5

 GROMACS modification: No

Hii

 In my simulation box, the protein and the DNA are totally out of the boxes. I modified the trajectory with -pbc whole and -pbc nojump. Now I’m trying to calculate the hbonds between them. The distance between them is more than 4nm, and it should not make any hbonds. However I’m still getting it. I was facing similar problem with the gmx mindist but there -pbc flag worked and gave me proper distances, however in gmx hbond, -pbc flag is not working.

Any kind of help is highly appreciated.

 Thank you for reading.

[Karis](https://gromacs.bioexcel.eu/u/Karis) June 27, 2024, 5:04am 2

Did you also include the -pbc flag as part of the hbond command? I’ve found that for the analysis modules, even if you’re running them on trajectories with pbc removed, the results returned are still for the trajectory with pbc unless you also include the -pbc flag in the analysis command

[Sahil](https://gromacs.bioexcel.eu/u/Sahil) June 27, 2024, 5:19am 3

For the hbond analysis I used "gmx hbond -f *.xtc -s *.tpr -n *.ndx -num *.xvg -pbc no ". The trajectory is already modified with pbc removed. It is still not working.

[Karis](https://gromacs.bioexcel.eu/u/Karis) June 27, 2024, 5:44am 4

Could you try visualizing the system and seeing which hbonds are being identified? It might be that pbc removal isn’t working perfectly, and especially in the case of multiple freely floating molecules, it might be difficult to stop objects from interacting with mirror images of a different object.

You can find a description of how each pbc option works here: [gmx trjconv - GROMACS 2024.2 documentation](https://manual.gromacs.org/current/onlinehelp/gmx-trjconv.html). While they mostly work to stop an object from interacting with its own mirror image, if you have 2 separate objects floating at opposite ends of the box, preventing interactions might require altering the set up of the simulation

[Sahil](https://gromacs.bioexcel.eu/u/Sahil) June 27, 2024, 5:58am 5

My question is, does the -pbc flag work with gmx hbond? Because in my case it is not working.

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/1/1d677b9ea6d5962733c40c97ff01c3d71b2af95a.png)image1276×286 8.83 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/1/1d677b9ea6d5962733c40c97ff01c3d71b2af95a.png)[Karis](https://gromacs.bioexcel.eu/u/Karis) June 27, 2024, 6:21am 6

I see it listed in the 2024.2 documentation but not in earlier versions so it might not work with older versions of gmx hbond

[obZehn](https://gromacs.bioexcel.eu/u/obZehn) June 27, 2024, 8:36am 7

Please take a look at the [manual](https://manual.gromacs.org/2021/onlinehelp/gmx-hbond.html). For GROMACS 2021, there is no `pbc` flag. There is for GROMACS 2024 but the tool is different (the one in previous versions has been moved to [hbond-legacy](https://manual.gromacs.org/current/onlinehelp/gmx-hbond-legacy.html)).

[Ligand1](https://gromacs.bioexcel.eu/u/Ligand1) June 28, 2024, 9:58pm 8

Hi,

I have a small followup question [@Karis](https://gromacs.bioexcel.eu/u/karis) . Do we need to give -pbc flag for every analysis? I am not familiar with this and this is something not mentioned in the Gromacs tutorials written by Dr. Justin Lemkul.

Thanks

[scinikhil](https://gromacs.bioexcel.eu/u/scinikhil) June 28, 2024, 11:41pm 9

fix the pbc with gmx trjconv and analyse the output trajectory. [@Ligand1](https://gromacs.bioexcel.eu/u/ligand1)

[Karis](https://gromacs.bioexcel.eu/u/Karis) June 29, 2024, 3:24am 10

You’ll have to check the gromacs manual for the specific analysis module you’re considering to see whether a -nopbc flag is present, I only know that using gmx distance on a trajectory where pbc was removed still did not account for pbc being removed until I added a -nopbc flag to the gmx distance command, and that this might be the case for other modules where -nopbc flag is an option

[Ligand1](https://gromacs.bioexcel.eu/u/Ligand1) July 1, 2024, 10:19pm 11

Hi Karis,

Thanks for replying to my comment. I went ahead and tested this myself. I am using Gromacs 2022.5. In the gmx rms module there is an option for -nopbc. My trajectory is already corrected for PBC. I used the following commands:

gmx trjconv -s md_100.tpr -f md_100.xtc -o md_100_center.xtc -center -pbc mol -ur compact

 Choose “Protein” for centering and “System” for output.

gmx trjconv -s md_100.tpr -f md_100_center.xtc -o Finalcenterfir0_100.xtc -fit rot+trans

 Choose “Backbone” to perform least-squares fitting to the protein backbone, and “System” for output.

Now I went ahead and analyzed the RMSD of the Calpha atoms of my protein by using gmx rmsd module:

First I used this command: gmx rms -s md_100.tpr -f Finalcenterfit0_100.xtc -o 1CArmsd.xvg -tu ns

Then I used the second command with -nopbc flag:

 gmx rms -s md_100.tpr -f Finalcenterfit0_100.xtc -nopbc -o 2CArmsd.xvg -tu ns

When I am looking at the two XVG files I cannot see any difference. They are exactly the same. I guess this observation might be unique to your case. Let me know what are your thoughts on this.

Best Regards

[Karis](https://gromacs.bioexcel.eu/u/Karis) July 2, 2024, 2:37am 12

It might depend on the version of gromacs or the modules used, I’m not familiar enough with how they work to be sure. That being said, it might also be that your protein didn’t reach the sides of the box during the simulation, in which case correcting for pbc wouldn’t make a difference.

[Ligand1](https://gromacs.bioexcel.eu/u/Ligand1) July 2, 2024, 5:16pm 13

Yes I do have a big box. There could be other reasons too. Anyways, Thanks for the insights.

Best regards

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Is PBC correction necessary for some particular type of analysis?User discussionspbc,analysis-tools,gmx-trjconv | 2 | 1227 | May 30, 2023 |  |
| Regarding usage of -pbc yes while calculating mindistUser discussions | 0 | 37 | December 5, 2025 |  |
| Pbc effect removalUser discussions | 2 | 1566 | December 4, 2020 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 202 | January 15, 2025 |  |
