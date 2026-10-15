# How can we generate itp file for flat-bottom position restraint?

> GROMACS version: 2020.1  GROMACS modification: Yes/No  Here post your question  Hi GROMACS users,  When we use pdb2gmx, it automatically gives us a position restraint itp for our system. If special position restraints [.itp file] are required, one can use genrestr utility of the gromacs. I want to apply a flat-bottom position restraint on a water layer in z+ and z- directions. There are other molecules also in the system but they are above and below the water layer. The thickness of water layer ...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[hosyadav](https://gromacs.bioexcel.eu/u/hosyadav) May 27, 2020, 9:52am 1

GROMACS version: 2020.1

 GROMACS modification: Yes/No

 Here post your question

 Hi GROMACS users,

When we use pdb2gmx, it automatically gives us a position restraint itp for our system. If special position restraints [.itp file] are required, one can use genrestr utility of the gromacs. I want to apply a flat-bottom position restraint on a water layer in z+ and z- directions. There are other molecules also in the system but they are above and below the water layer. The thickness of water layer is 1 nm. As much I understood, the format of the flat-bottom position restraint for water would be as following:

; Position restraint for each water oxygen

 [ position_restraints ]

 ; i funct g r k

 1 2 5 0.5 1000

where funct = 2 will ensure the flat-bottom potential, g = 5 will ensure its applicability only in the z-direction, r = 0.5 is the half-width of the flat-bottom potential, and k = 1000 is of course force constant. Possibly, this itp will apply force on water molecules if any water molecule is below [COM_water (z) - 0.5] nm or above [COM_water(z) + 0.5] nm, where COM_water(z) is the center of mass of the water molecules.

Now my question is following:

 I wrote the above itp by hand. Is it possible to get this itp by “gmx genrestr” utility or by other utility of GROMACS? In the present example, I have water. So it is easy to write it by hand. But other complex system, it might be difficult. I don’t see any option in genrestr to define function type etc.

[cblau](https://gromacs.bioexcel.eu/u/cblau) May 27, 2020, 2:12pm 2

Hi Hosyadav,

gmx genrestr does not allow setting the function type.

It will help you half-way through though in generating the vanilla function type 1 harmonic restraints; you will have to edit the generated files yourself though to update the function type and the other following parameters.

1 Like[hosyadav](https://gromacs.bioexcel.eu/u/hosyadav) May 27, 2020, 3:09pm 3

Dear cblau,

 Thank you so much for replying the query. I suspected the same. Anyway I will use some script to write itp.

 Thanks once again for your response.

[s.pallav](https://gromacs.bioexcel.eu/u/s.pallav) June 28, 2022, 1:45pm 4

Hi [@hosyadav](https://gromacs.bioexcel.eu/u/hosyadav),

 how did you generate one?

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Flat-bottom restraints on specific atomsUser discussionsrestraints,simulation-setup | 3 | 79 | March 10, 2026 |  |
| Applying flat bottom potential on substrateUser discussionsforcefield | 2 | 1646 | January 14, 2023 |  |
| Spherical position restraintsUser discussions | 5 | 1575 | October 19, 2020 |  |
| Inverted Flat-bottomed position restraintUser discussionsrestraints | 7 | 1496 | September 7, 2023 |  |
| Flat-bottomed position restraints not workingUser discussions | 4 | 540 | February 9, 2021 |  |
