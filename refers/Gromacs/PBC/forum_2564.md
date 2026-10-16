# Difference in Coulomb interaction energy for a two particle system with and without PBC and PME

> Hi everyone,  I have calculated the interaction energy for a system with two single atoms and was quite surprised how much the Coulomb interaction differs when using periodic boundary conditions (PBC), Particle Mesh Ewald (PME) or no periodic boundary conditions.  I calculated the interaction energy for a system with 2 particles (0.4nm distance, q1=-1e, q2= 0.0842e)  for the following three situations:  1. PBC with PME  2. PBC withou PME  3. no PBC (not possible with the latest version of gromac...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[mdp-parameters](https://gromacs.bioexcel.eu/tag/mdp-parameters)[DSeiferth](https://gromacs.bioexcel.eu/u/DSeiferth) July 21, 2021, 10:01pm 1

Hi everyone,

I have calculated the interaction energy for a system with two single atoms and was quite surprised how much the Coulomb interaction differs when using periodic boundary conditions (PBC), Particle Mesh Ewald (PME) or no periodic boundary conditions.

 I calculated the interaction energy for a system with 2 particles (0.4nm distance, q1=-1e, q2= 0.0842e) for the following three situations:

 1. PBC with PME

 2. PBC withou PME

 3. no PBC (not possible with the latest version of gromacs, so one need to travel back in versions)

The short range Coulomb interactions (Coulomb (SR) ) and the Coul-SR:a_1-a_2 differed for both situations with PBC. Only for a system with no PBC, the analytical (-29.2468 kJ/mol) and simulated result were the same and Coulomb (SR) = Coul-SR:a_1-a_2.

 Is this expected? And if yes, does anyone have a good intuition to explain this?

I used the following mdp parameters:

 • PBC with PME (Coulomb (SR) = -209.594 and Coul-SR:a_1-a_2 = -4.12159)

 ◦ pbc = xyz

 ◦ energygrps = a_1 a_2

 ◦ cutoff-scheme = Verlet

 ◦ ns_type = grid

 ◦ nstlist = 20

 ◦ rlist = 1.2

 ◦ vdwtype = cutoff

 ◦ vdw-modifier = force-switch

 ◦ rvdw-switch = 1.0

 ◦ rvdw = 1.2

 ◦ coulombtype = PME

 ◦ rcoulomb = 1.2

 ◦ pme_order = 4

 ◦ fourierspacing = 0.16

 • PBC without PME (Coulomb (SR) = -77.7984 and Coul-SR:a_1-a_2 =-19.4982)

 ◦ pbc = xyz

 ◦ energygrps = a_1 a_2

 ◦ cutoff-scheme = Verlet

 ◦ ns_type = grid

 ◦ nstlist = 20

 ◦ rlist = 1.2

 ◦ vdwtype = cutoff

 ◦ vdw-modifier = force-switch

 ◦ rvdw-switch = 1.0

 ◦ rvdw = 1.2

 ◦ coulombtype = Cut-off;

 ◦ rcoulomb = 1.2

 • no PBC Coulomb (SR)=-29.2468 and Coul-SR:a_1-a_2 = -29.2468

 ◦ energygrps = a_1 a_2

 ◦ pbc = no

 ◦ cutoff-scheme = group

 ◦ nstlist = 0

 ◦ rvdw = 0

 ◦ rcoulomb =0

 ◦ rlist = 0

For the systems with PBC, I have used gromacs/2020.3-AVX2-GPU.

 For the system without PBC, I used gromacs/5.1/64.

[pjohansson](https://gromacs.bioexcel.eu/u/pjohansson) July 22, 2021, 3:46am 2

Hi,

yes, this is perfectly expected. With PBC each charge is interacting with all infinite periodic replicas. You can truncate the interaction with a cutoff but then the Coulomb interaction is no longer correctly modeled. Unlike the LJ interaction* the Coulomb interaction trends too slowly towards 0 to be simply cutoff without a large artifact. Using PME includes the complete interaction.

Regards,

 Petter

* Although in certain setups cutting the LJ interaction can introduce notable artifacts.

[DSeiferth](https://gromacs.bioexcel.eu/u/DSeiferth) July 22, 2021, 8:36am 3

Hi Petter,

Thanks for your reply.

 What I find surprising is that the short range Coulomb interaction (Coul-SR:a_1-a_2) energy between two atoms whose distance is below the cutoff differs from the analytical result by a factor of 7.

 I used a cubic box with 4.6nm side length.

When turning off PME, the short range Coulomb interaction energy between the two atoms in the original cell increases.

 When turning off PBC, the short range Coulomb interaction energy between the two atoms increases even further (and equals the expected analytical result).

 With PBC, the atoms interact with 26 other unit cells and there are attracting contributions (between atoms with different charge sign) and repulsive contributions (between atoms with same charge sign). Considering the box size (4.6nm length of the side of the box vs. 1.4nm cutoff), the atoms should not “see” the atoms in the periodic images, right?

Just to clarify: Coulomb (SR) refers to all short range Coulomb interactions in the system and Coul-SR:a_1-a_2 refers to short range Coulomb interactions between atom 1 and atom 2 in all the periodic images, right?

[pjohansson](https://gromacs.bioexcel.eu/u/pjohansson) July 23, 2021, 9:16am 4

Re: the difference with PBC+cutoff and no-PBC. I would indeed expect them to be the same if your box is that large that neighboring images should not be seen. My one thought is, what is your setting for `coulomb-modifier`? It should be set to `None` to get the unmodified potential.

[https://manual.gromacs.org/documentation/current/user-guide/mdp-options.html#mdp-coulomb-modifier](https://manual.gromacs.org/documentation/current/user-guide/mdp-options.html#mdp-coulomb-modifier)

Petter

1 Like

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Protein-ligand atom groups coulombic interaction energies discrepancies between PME and cut-offUser discussions | 2 | 761 | June 23, 2021 |  |
| Problem in interaction energy calculationUser discussions | 1 | 292 | March 18, 2021 |  |
| Cation-cation and anion-anion short-range Coulomb negative energyUser discussions | 6 | 815 | May 5, 2025 |  |
| Manual Calculation of Coulomb (SR) is inconsistent with GromacsUser discussions | 14 | 409 | March 20, 2025 |  |
| Energy groups find self interacting Na+ and Cl+ for Coulombic interaction energy?User discussions | 6 | 583 | May 2, 2025 |  |
