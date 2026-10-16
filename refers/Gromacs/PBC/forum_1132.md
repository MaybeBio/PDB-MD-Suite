# Pbc effect removal

> Hi all,  I need to remove PBC effect from a system containing a protein having four monomers, DNA, and metal atoms. I use four commands to remove the PBC effect and it seems to give me the best output possible, but still, I can see slight jumps in the trajectory. I also am concerned about the effect of a bad PBC removal on the resulting structure and its effect on further analysis.  I use -pbc whole, -pbc nojump, -pbc cluster + center, and finally -pbc mol + center.  Any help or comment would be...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[marko](https://gromacs.bioexcel.eu/u/marko) November 20, 2020, 8:45pm 1

Hi all,

 I need to remove PBC effect from a system containing a protein having four monomers, DNA, and metal atoms. I use four commands to remove the PBC effect and it seems to give me the best output possible, but still, I can see slight jumps in the trajectory. I also am concerned about the effect of a bad PBC removal on the resulting structure and its effect on further analysis.

 I use -pbc whole, -pbc nojump, -pbc cluster + center, and finally -pbc mol + center.

 Any help or comment would be appreciated.

 Thank you.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) November 23, 2020, 9:58am 2

Hi,

 This topic has been addressed several times in the forum. Maybe you find the answer already in the forum using the option search.

Maybe the answer to this post can help

![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/dmercadante/48/100_2.png)[Seemingly unresolvable PBC problem on protein complex](https://gromacs.bioexcel.eu/t/seemingly-unresolvable-pbc-problem-on-protein-complex/786)[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)

>  GROMACS version: 2019.4 GROMACS modification: No Dear All, I have a protein complex on which I ran some REMD and I want to solve PBC issues before analysis. However, no matter what I tried, one of the proteins still jumps out of the box. Firstly I make the system whole with: $gmx trjconv -f md.xtc -s nvt_298.15.tpr -pbc whole -o whole -n index.ndx This makes the molecules whole, although both proteins in the complex “jump around”. I have then centered the system on an interfacial residue… 

Best regards

 Alessandra

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) December 4, 2020, 3:56pm 4

Hi,

 If you want to calculate RMSD respect the starting structure, I suggest to use the option -s with the tpr file of your first step of your simulation (probably EM).

 Alessandra

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3636 | October 25, 2022 |  |
| Removing pbc effectUser discussions | 13 | 11165 | April 3, 2023 |  |
| Unable to correct PBC effect of MD trajectory of a tetrameric protein + ligandUser discussions | 3 | 772 | January 3, 2024 |  |
| Remove PBC effects on membrane+protein+ligandUser discussionspbc | 4 | 699 | October 20, 2022 |  |
| Jumping residue after PBC removalUser discussionspbc,gmx-trjconv | 13 | 788 | August 26, 2024 |  |
