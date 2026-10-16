# How to deal with the PBC of trajectory file for dsDNA

> GROMACS version:2019.6  GROMACS modification: No  Hello everyone,  I have encountered some problems after using Gromacs 2019.6 to simulate a 36bp long double-stranded DNA in water and ionic solutions(X Y Z of box size: 14.66438nm x 6.70097nm x 6.82766nm) and I can’t solve them. The specific problems are as follows:        Fisrtly, I have carried out  a 500ns simulation for dsDNA in solution without setting the md.mdp of  removing center of mass translation and rotation around the center of mass(...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mdp-parameters](https://gromacs.bioexcel.eu/tag/mdp-parameters), [analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools)[HZW](https://gromacs.bioexcel.eu/u/HZW) May 26, 2022, 1:55am 1

GROMACS version:2019.6

 GROMACS modification: No

 Hello everyone,

I have encountered some problems after using Gromacs 2019.6 to simulate a 36bp long double-stranded DNA in water and ionic solutions(X Y Z of box size: 14.66438nm x 6.70097nm x 6.82766nm) and I can’t solve them. The specific problems are as follows:

```
Fisrtly, I have carried out  a 500ns simulation for dsDNA in solution without setting the md.mdp of  removing center of mass translation and rotation around the center of mass(comm-mode = Angular ; comm-grps   = DNA). Then I use gmx_trjconv to deal the md trajectory(use first gmx trjconv -f md.xtc -s md.tpr -o md_mol.xtc -pbc mol -center, then gmx trjconv -f md.xtc -s md.tpr -o md_nojump.xtc -pbc nojump -center, and try -pbc atom , -pbc whole). After visualize the  PBC dealed md trajectory  , the single chain of dsDNA is separated and the complete double-stranded DNA molecules can not appear. I want to show  the complete double-stranded DNA molecules conformation in my article. 
    Secondly, I I have carried out  a 500ns simulation for dsDNA in solution with setting the md.mdp of  removing center of mass translation and rotation around the center of mass(comm-mode = Angular ; comm-grps   = DNA). The same problems occurred when I deal the md trajectory file in the same way, except that it didn't appear in the first 100ns of the simulation, but it appeared later.
   Note:I try dealing the PBC of md trajectory with VMD. However the problem remains unsolved.
  How I can solve it. Thank those who can help in advance.
```

Best Regards,

 Lesile Han

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) June 2, 2022, 7:52am 2

Hi,

 did you try to use gmx trjconv (see here for suggested workflow [Terminology — GROMACS 2022.1 documentation](https://manual.gromacs.org/current/user-guide/terminology.html#suggested-workflow)) ?

 Alessandra

[HZW](https://gromacs.bioexcel.eu/u/HZW) June 4, 2022, 5:53am 3

Firtly, thanks for your reply, Prof Alessandra. I’m sorry to reply to you so late. I’m going to have a try again and look carefully at the official suggestions on dealing with the PBC of trajectory files . However, I’m not sure I can solve this problem. That’s because I have tried many methods before. If I can’t solve the problem, I’ll ask you for help again. Thank you very much in advance!

Best Regards,

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) June 8, 2022, 2:13am 4

Using `comm-mode = Angular` is for vacuum simulations only and should not be used for MD in the condensed phase. If the issue is simply imaging, then center on one strand of the dsDNA first (create an index group to do this), after which the other strand will be wrapped to the center of the unit cell with it. Then (if you want), center on the entire DNA. With two steps in `gmx trjconv` this should be resolved.

[HZW](https://gromacs.bioexcel.eu/u/HZW) June 16, 2022, 2:31pm 5

Okay, thanks for your reply. I’m going to adopt your advice.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 202 | January 15, 2025 |  |
| DNA visualtion disortionUser discussionsmdp-parameters,mdrun,analysis-tools | 0 | 214 | May 15, 2023 |  |
| Making DNA whole in a triclinic boxUser discussions | 1 | 400 | January 29, 2021 |  |
| Unable to correct PBC effect of MD trajectory of a tetrameric protein + ligandUser discussions | 3 | 772 | January 3, 2024 |  |
| Fix two separate DNA strands after simulation using -pbc clusterUser discussionspbc,analysis-tools | 0 | 67 | July 22, 2024 |  |
