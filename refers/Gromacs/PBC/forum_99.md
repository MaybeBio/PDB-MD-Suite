# PBC after energy minimization

> Hello everybody,  This email has been sent before on the mailing list but I couldn’t reply, so I wrote the complete question again, sorry for that.  I want to visualize the initial structure and also the structures between the different simulation steps to know if anything wrong happened. I can’t visualize my structure after the energy minimization due to the PBC. I know how to solve that at the end after finishing the simulation using the below commands  gmx trjconv -s md_0_1.tpr -f md_0_1.xtc ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[M_Abdelaal](https://gromacs.bioexcel.eu/u/M_Abdelaal) May 9, 2020, 10:36pm 1

Hello everybody,

This email has been sent before on the mailing list but I couldn’t reply, so I wrote the complete question again, sorry for that.

I want to visualize the initial structure and also the structures between the different simulation steps to know if anything wrong happened. I can’t visualize my structure after the energy minimization due to the PBC. I know how to solve that at the end after finishing the simulation using the below commands

gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_noPBC.xtc -pbc mol

followed by:

mx trjconv -s md_0_1.tpr -f md_noPBC.xtc -o md_noPBC.pdbds:

Justin has replied previously that “Trajectories” from energy minimization are generally unreadable as the interval of saved frames is uneven. Is there another way to solve or visualize my structure without the PBC after the energy minimization without the trajectories ?

I have attached below an image of my structure after the energy minimization with the PBC.

[https://drive.google.com/file/d/19Q_4aGA1MLaO3FrtETGYs9CsBmIzNUIu/view?usp=sharing](https://drive.google.com/file/d/19Q_4aGA1MLaO3FrtETGYs9CsBmIzNUIu/view?usp=sharing)

Thanks,

 Mohamed

[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) May 11, 2020, 2:17am 2

What do you mean you can’t visualise it? Why not?

If it is simply because the movement of molecules/atoms across the PBC have made it difficult to see what you want, then simply recenter as appropriate and make sure all molecules are whole again.

Note that PBC means that if something leaves say the left hand face of the simulation box, then it then enters in the right hand side and you essentially have an infinite system. Because of this where the “box” is “drawn” when you visualise it is entirely arbitrary. So you adjust things as you see fit to give the visualisation you required.

Also see [http://manual.gromacs.org/documentation/current/user-guide/terminology.html#gmx-pbc](http://manual.gromacs.org/documentation/current/user-guide/terminology.html#gmx-pbc)

1 Like[M_Abdelaal](https://gromacs.bioexcel.eu/u/M_Abdelaal) May 11, 2020, 9:38am 3

Thanks for your reply :)

Yes, my problem is that the molecules are not whole and parts of the substrate have been moved from the bottom to the top as in the image I have attached and as your description.

How can I solve these problem after the energy minimization if I don’t have the .xtc file ? Is there another way to fix them without using the .xtc file ?

Thanks,

 Mohamed

[Dr_DBW](https://gromacs.bioexcel.eu/u/Dr_DBW) May 11, 2020, 9:44am 4

You don’t need a trajectory file, gmx trjconv will run fine on coordination files too.

1 Like[M_Abdelaal](https://gromacs.bioexcel.eu/u/M_Abdelaal) May 12, 2020, 10:50pm 5

It worked with the .gro file. Many thanks :)

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Removing PBC before gromppUser discussions | 5 | 512 | July 24, 2020 |  |
| Assistance Needed: Issue with Simulation Setup and VisualizationUser discussions | 2 | 193 | March 27, 2024 |  |
| DNA visualtion disortionUser discussionsmdp-parameters,mdrun,analysis-tools | 0 | 214 | May 15, 2023 |  |
| About the trajectoryUser discussionsmdrun | 4 | 330 | January 15, 2024 |  |
| To get position of my molecule without pbcUser discussions | 2 | 327 | February 2, 2021 |  |
