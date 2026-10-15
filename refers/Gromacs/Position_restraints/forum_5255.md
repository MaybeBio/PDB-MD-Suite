# How to immobilize magnesium ions in protein pockets

> GROMACS version:  GROMACS modification: Yes/No  Here post your question  Hi everyone, how to maintain magnesium ions in protein pockets? Tried using -diser to select the amino acid atoms that interact with magnesium ions, but it still doesn’t work too well, is there another good way?

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[HXY](https://gromacs.bioexcel.eu/u/HXY) November 15, 2022, 10:30am 1

GROMACS version:

 GROMACS modification: Yes/No

 Here post your question

Hi everyone, how to maintain magnesium ions in protein pockets? Tried using -diser to select the amino acid atoms that interact with magnesium ions, but it still doesn’t work too well, is there another good way?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) November 15, 2022, 3:35pm 2

Please define what you mean by “it still doesn’t work too well.” Distance restraints are the appropriate method here, though there are different ways to do it (e.g. `[distance_restraints]` or harmonic bond type 6 or 10).

[HXY](https://gromacs.bioexcel.eu/u/HXY) November 15, 2022, 4:17pm 3

First of all, thank you for your reply, maybe due to my unclear presentation, when I created the index group of magnesium ion and interacting amino acid atoms, I wanted to use the gmx genrestr command for distance restriction selected by -diser, then selected the corresponding index group and added it in the topology file, ran the NVT and NPT under restriction, and finally ran the MD without restriction. But the magnesium ion eventually got out of the protein pocket. Is it because I only set the distance constraint for one key? Or should I use another method?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) November 15, 2022, 5:39pm 4

Mg<sup>2+</sup> ligates residues in an octahedral geometry, so you should have probably 6 distances that you restrain to preserve its relative position. What does your `[distance_restraints]` directive look like? Are all the distances appropriately set? Are you sure the apparent diffusion is not simply a PBC issue?

[HXY](https://gromacs.bioexcel.eu/u/HXY) November 16, 2022, 2:39am 5

Here I used the magnesium ion in the structure of the homologous protein and then superimposed the structure with my own protein. The only interactions with the magnesium ion were found to be an OD2 atom on the aspartic acid at position 103 and an oxygen atom on the ADP molecule of the ligand, other than that no other interactions existed. After imposing position restrictions on the ligand, the command is used gmx genrestr … -n index -diser imposes distance restrictions on the magnesium ion, and the index group r103&aOD2_MG is selected, generating:

 [ distance_restraints ]

 ; i j ? label funct lo up1 up2 weight

 1573 4727 1 0 1 0.0817967 0.281797 1.2818 1

 Position in the topology file：

 [ moleculetype ]

 ;name nrexcl

 ADP_fix 3

; Include ligand topology

#include “ADP_fix_GMX.itp”

#ifdef POSRES

#include “posre_ADP.itp”

#endif

; Include chain topologies

#include “topol_Protein_chain_A.itp”

[ distance_restraints ]

 ; i j ? label funct lo up1 up2 weight

 1573 4727 1 0 1 0.0817967 0.281797 1.2818 1

; Include water topology

#include “amber99sb-ildn.ff/tip3p.itp”

#ifdef POSRES_WATER

 ; Position restraint for each water oxygen

 [ position_restraints ]

 ; i funct fcx fcy fcz

 1 1 1000 1000 1000

#endif

 The command to correct the period is：

 gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -n index.ndx -o md_center.xtc -center -pbc mol -ur compact

gmx trjconv -s md_0_1.tpr -f md_center.xtc -n index.ndx -o md_fit.xtc -fit rot+trans

The position of the ligand viewed with VMD is always good, but the magnesium ion is not in the protein pocket

[HXY](https://gromacs.bioexcel.eu/u/HXY) November 16, 2022, 4:13pm 6

Is the pull code command worth a try?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) November 16, 2022, 4:25pm 7

Distance restraints don’t work between `[moleculetypes]` unless within an `[intermolecular_interactions]` directive at the end of the system topology, so probably whatever you’ve been trying simply hasn’t been working at all. `gmx genrestr` only works for the first molecule, as the documentation notes. Global atom indices cannot be used in `[distance_restraints]` unless they are in `[intermolecular_interactions]`.

[HXY](https://gromacs.bioexcel.eu/u/HXY) November 16, 2022, 5:01pm 8

Hello, thank you for your reply, I’m not quite sure what you’re talking about "Global atom indices cannot be used in `[distance_restraints]` unless they are in `[intermolecular_interactions]` ". I’m a bit confused about what to do, could you please give me an example? Thank you very much!

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) November 17, 2022, 3:55am 9

Like any restraints, distance restraints are intended to be applied within only one `[moleculetype]`, which it appears is not the case in your topology. You have multiple `[distance_restraints]` directives between different chain topologies. This should not work. If you want to use distance restraints, you need a topology in which the protein, Mg<sup>2+</sup>, and ADP are all merged into one `[moleculetype]`, and the only valid atom numbers in `[distance_restraints]` are from 1…N, where N is the number of atoms in that `[moleculetype]` definition.

The `[intermolecular_interactions]` directive is a special thing that can use global atom numbers rather than only those that are local to a given `[moleculetype]`. It is probably better to try to produce a merged `[moleculetype]` and generate suitable distance restraints with it.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| How to put distance restraints into topology fileUser discussionsmdrun,restraints | 25 | 2280 | January 16, 2025 |  |
| Applying distance constraints to ligand and Mg ionUser discussions | 33 | 6031 | June 26, 2025 |  |
| Imposing restraints between protein and ligandUser discussionsrestraints | 24 | 2415 | June 27, 2025 |  |
| Trouble to apply distance restraintsUser discussionsmdp-parameters,restraints,simulation-setup | 2 | 1517 | April 4, 2022 |  |
| Distance Restraints type 6User discussions | 2 | 1622 | January 5, 2025 |  |
