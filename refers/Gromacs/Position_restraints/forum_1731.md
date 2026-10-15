# GROMACS simulation of dimers using the Amber FF14SB forcefield

> GROMACS version: 2018.4  GROMACS modification: No  Hi there,  I am attempting to perform MD simulations on a functional dimer Using the Amber FF14SB forcefield set.  The current workflow has me importing the PDB file containing the dimer to amber, generating the box, solvation and ion topology and perameters using tleap, then converting the resultant files to GROMACS .top and .gro formats using parmed. As this process dosent generate positional restraints in the same way that pdb2gmx does, I the...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[gtitchiner](https://gromacs.bioexcel.eu/u/gtitchiner) March 10, 2021, 4:43pm 1

GROMACS version: 2018.4

 GROMACS modification: No

Hi there,

I am attempting to perform MD simulations on a functional dimer Using the Amber FF14SB forcefield set.

 The current workflow has me importing the PDB file containing the dimer to amber, generating the box, solvation and ion topology and perameters using tleap, then converting the resultant files to GROMACS .top and .gro formats using parmed. As this process dosent generate positional restraints in the same way that pdb2gmx does, I then generate positional restraints using gmx genrestr.

The issue I am encountering is in the way the topology file is generated in this method. It essentially lists the topology for the monomer in this case termed ‘system1’ and then simply lists ‘system 1’ twice in the [ molecules ] section of the topology file. This becomes an issue as I wish to be able to restrain one half of the dimer pair in order to perform umbrella sampling, as the atom numbering in any POSRE.itp file, generated using gmx genrestr from index groups, wont match the numbering in the general topology file as it essentially only defines topolgy for half the atoms and then duplicates it.

Any recomendations on how to get around it? I havent been able to idenitfy if this is due to the way that tleap or parmed treats protein chains? I am of course happy to provide any of the files I am working with.

Thanks!

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) March 12, 2021, 5:03pm 2

Hi,

 An option is to generate manually posre.itp file, putting the desired atoms number. Below an example of position restrains file

; In this topology include file, you will find position restraint

 ; entries for all the heavy atoms in your original pdb file.

 ; This means that all the protons which were added by pdb2gmx are

 ; not restrained.

[ position_restraints ]

 ; atom type fx fy fz

 1 1 1000 1000 1000

 5 1 1000 1000 1000

 7 1 1000 1000 1000

Best regards

 Alessandra

[gtitchiner](https://gromacs.bioexcel.eu/u/gtitchiner) April 1, 2021, 12:27pm 3

Hi, Alessandra

Thanks this did the job!

All the best,

Gabe

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| How to define position restrains on the two monomers of a dimer?User discussionsmdp-parameters,simulation-setup | 4 | 312 | August 6, 2024 |  |
| Position restraints missing when .itp is printed to .topUser discussionspdb2gmx,simulation-setup | 2 | 132 | January 21, 2025 |  |
| Using positional restraints for atoms of the perimeterUser discussionsrestraints | 4 | 1479 | August 24, 2021 |  |
| Positional restraint, grompp -r error, restraint coordinates does not match topologyUser discussionsrestraints | 1 | 1048 | August 19, 2021 |  |
| Grompp -r --does not match the number of atoms in the topologyUser discussions | 6 | 2248 | August 19, 2021 |  |
