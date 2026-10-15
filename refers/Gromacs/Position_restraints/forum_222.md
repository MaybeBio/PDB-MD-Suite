# Freezing the surface and positioning of liquid

> GROMACS version: 2018  GROMACS modification: Yes with plumed  Dear all,  I want to ask couple of questions in which I am facing some trouble. I want to study the wettability of droplets on different surfaces. Now coming to the questions,    How can I freeze the surface so that while the simulation is running it’s position doesn’t get changed or it doesn’t get deformed.    I have an equilibrated droplet and I want to place it above the surface suppose at a distance of say 0.6nm from the surface. ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Dev](https://gromacs.bioexcel.eu/u/Dev) June 1, 2020, 9:02am 1

GROMACS version: 2018

 GROMACS modification: Yes with plumed

 Dear all,

 I want to ask couple of questions in which I am facing some trouble. I want to study the wettability of droplets on different surfaces. Now coming to the questions,

1. How can I freeze the surface so that while the simulation is running it’s position doesn’t get changed or it doesn’t get deformed.
2. I have an equilibrated droplet and I want to place it above the surface suppose at a distance of say 0.6nm from the surface. I am finding this part a bit tricky. Can anybody help me with this.

Thanks

 Devargya

[Debashish](https://gromacs.bioexcel.eu/u/Debashish) June 1, 2020, 5:21pm 2

Hello Dev, I have never used freeze command but I think position restraints can help you regarding this issue.

In order to do so, you can create a special index file (index.ndx) containing your atoms in the surface, say (100 atoms):

 gmx_mpi make_ndx -f yourfile.gro -n index.ndx

 Now you have a certain group, say number 10 in your index file: Surface (containing 100 atoms).

Once you have created the surface, we will put position restraints on them:

 gmx_mpi genrestr -f yourfile.gro -n index.ndx -o posres_surface.itp -fc 1000 1000 1000

 When prompted, select the particular group numver that we had created in above step, (10). This will give you a file with the name posres_surface.itp with the position restraints. Check it’s content using any text editor and refer to the manual for a better insight.

Now that, you have your position restrained file, you need to edit your .mdp files accordingly using define statement:

 define = -DPOSRES

Also, edit your topology file like this:

#ifdef POSRES

#include “posres_surface.itp”

#endif

Hope this method can help you if you are looking for an alternative approach than FREEZE.

Best regards,

 Debashish

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) June 1, 2020, 5:54pm 3![](https://avatars.discourse-cdn.com/v4/letter/d/e8c25b/48.png) Dev:> How can I freeze the surface so that while the simulation is running it’s position doesn’t get changed or it doesn’t get deformed.

This is what `freezegrps` in the `.mdp` file is for, though it is extremely artificial.

![](https://avatars.discourse-cdn.com/v4/letter/d/e8c25b/48.png) Dev:> I have an equilibrated droplet and I want to place it above the surface suppose at a distance of say 0.6nm from the surface. I am finding this part a bit tricky. Can anybody help me with this.

Use `gmx editconf -center` to set its position, and concatenate the coordinates with those of the surface.

[Dev](https://gromacs.bioexcel.eu/u/Dev) June 2, 2020, 10:26am 4

Thank you for helping.

Devargya

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Position restraints freezes unrestrained molecule alsoUser discussionsforcefield,simulation-setup | 2 | 678 | April 27, 2022 |  |
| Gromacs Gold Surface restraints/freezegrpsUser discussionsmdp-parameters | 8 | 1196 | March 22, 2024 |  |
| Frozen atoms still moveUser discussionsmdrun | 16 | 1520 | December 13, 2022 |  |
| Problems with freezegrpsUser discussionsmdp-parameters | 0 | 451 | July 25, 2021 |  |
| Frozen beads - no movementsUser discussionsmdp-parameters | 2 | 68 | July 7, 2025 |  |
