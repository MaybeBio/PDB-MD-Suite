# Using positional restraints for atoms of the perimeter

> GROMACS version:2019  GROMACS modification: No  Here post your question  Dear Gromacs users,  I have a RNA-Protein complex with a ligand with multiple chains ( about 10 chains ) , now what I want is to position restraint the atoms which are 30 Angstroms beyond that ligand.  I have tried multiple ways to generate the positional restraint files including using the the coordinates of those restraint atoms and use pdb2gmx to generate positional restraints(posre.itp) files of individual chains and in...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[restraints](https://gromacs.bioexcel.eu/tag/restraints)[s.pallav](https://gromacs.bioexcel.eu/u/s.pallav) August 20, 2021, 10:36am 1

GROMACS version:2019

 GROMACS modification: No

 Here post your question

 Dear Gromacs users,

 I have a RNA-Protein complex with a ligand with multiple chains ( about 10 chains ) , now what I want is to position restraint the atoms which are 30 Angstroms beyond that ligand.

 I have tried multiple ways to generate the positional restraint files including using the the coordinates of those restraint atoms and use pdb2gmx to generate positional restraints(posre.itp) files of individual chains and include them in the main system topology but what I think is that would be a wrong way to go about doing things as these posre.itp files would have a different atom index and would possibly restrain the atoms which I wanted it to restrain in the first hand as the posre.itp file would read the heavy atoms from the topol.itp files from the corresponding chains which would have the atom index positions.

 Another easy way could have been if it were a single chain protein or RNA to use genrestr but then again for my case as there are many chains in the complex generating a posre.itp file using genrestr and merely including it in my topology would lead to errors.

Could there be a easy way out to specifically restrain the desired atoms of these chains?

Here is a print out of the topol.top where I had physically added the restraint files after using pdb2gmx to generate the position restraint files which seems to be the wrong way of doing things:

```
;
;	File 'topol.top' was generated
;	By user: psg (1000)
;	On host: pslab
;	At date: Wed Aug 18 17:09:36 2021
;
;	This is a standalone topology file
;
;	Created by:
;	                     :-) GROMACS - gmx pdb2gmx, 2019 (-:
;	
;	Executable:   /usr/local/gromacs/bin/gmx
;	Data prefix:  /usr/local/gromacs
;	Working dir:  /home/psg/Desktop/new_trial
;	Command line:
;	  gmx pdb2gmx -f rib_U_mutated.pdb -o rib.gro -ter
;	Force field was read from the standard GROMACS share directory.
;


; Include forcefield parameters
#include "charmm36-mar2019_psg.ff/forcefield.itp"

; include paromomycin parameters
#include "par.prm"

; Include chain topologies
#include "topol_Ion_chain_7.itp"
#include "topol_RNA_chain_A.itp"
#include "topol_RNA_chain_A2.itp"
#include "topol_RNA_chain_a.itp"
#include "topol_RNA_chain_a2.itp"
#include "topol_RNA_chain_a3.itp"
#include "topol_RNA_chain_a4.itp"
#include "topol_RNA_chain_a5.itp"
#include "topol_RNA_chain_a6.itp"
#include "topol_Protein_chain_c.itp"
#include "topol_Protein_chain_e.itp"
#include "topol_Protein_chain_i.itp"
#include "topol_Protein_chain_k.itp"
#include "topol_Protein_chain_l.itp"
#include "topol_RNA_chain_v.itp"
#include "topol_RNA_chain_x.itp"
#include "topol_RNA_chain_y.itp"

#ifdef POSRES_RES
#include "posre_RNA_chain_A_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a2_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a3_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a4_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a5_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a6_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a7_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a8_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_a9_.itp"
#endif

#ifdef POSRES_RES
#include "posre_Protein_chain_c.itp"
#endif

#ifdef POSRES_RES
#include "posre_Protein_chain_e_.itp"
#endif

#ifdef POSRES_RES
#include "posre_Protein_chain_l_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_v_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_v2_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_x_.itp"
#endif

#ifdef POSRES_RES
#include "posre_RNA_chain_y_.itp"
#endif

; Include water topology
#include "charmm36-mar2019_psg.ff/tip3p.itp"

#ifdef POSRES_WATER
; Position restraint for each water oxygen
[ position_restraints ]
;  i funct       fcx        fcy        fcz
   1    1       1000       1000       1000
#endif

; Include topology for paramomycin
#include "par.itp"

; Include topology for ions
#include "charmm36-mar2019_psg.ff/ions.itp"

[ system ]
; Name
Protein in water

[ molecules ]
; Compound        #mols
Ion_chain_7         1
RNA_chain_A         1
RNA_chain_A2        1
RNA_chain_a         1
RNA_chain_a2        1
RNA_chain_a3        1
RNA_chain_a4        1
RNA_chain_a5        1
RNA_chain_a6        1
Protein_chain_c     1
Protein_chain_e     1
Protein_chain_i     1
Protein_chain_k     1
Protein_chain_l     1
RNA_chain_v         1
RNA_chain_x         1
RNA_chain_y         1
PAR		1
SOL                 9
SOL         67458
NA               224
```

P.S.: The chains included in POSRES_RES are those chains which were added physically by including the positional restraints file which were generated by using pdb2gmx to generate the position restraints file.(I admit this would be very wrong as it possibly read the wrong atoms and put restraint on those atoms)

It would be helpful if someone could point out where I am going wrong and help me figure a easy way out to generate the positional restraints and include them in the system topology to succesfully to restrain those particular atoms ? or could it be possible I could use the topology file (topol.top) of those restraint coordinates and not that of system topology file?

Thanking you in advance.

 Regards,

 Pallav

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) August 24, 2021, 8:18am 2

Hi

Position restraints are interactions within molecules, therefore they must be included within the correct `[ moleculetype ]` block in the topology. In your case [moleculetype] block are defined in each topol…itp

The atom indices within the `[ position_restraints ]` block must be within the range of the atom indices for that molecule type. Note that the atom numbers in every moleculetype (topol…itp) in the topology start at 1 .

 If you use gmx genrest to generate the position restraints file, `gmx genrestr` will only produce a useful file only for the first molecule. You may wish to construct a suitable index group to provide as input to `gmx genrestr` .

Once all the posre_XXX.itp file have a numbering in line with [moleculetype], than the posre…itp file should include under the corresponding [moleculetype] (see below)

It should work and I hope this help.

 \Alessandra

 …

```
; Include forcefield parameters
#include "charmm36-mar2019_psg.ff/forcefield.itp"

; include paromomycin parameters
#include "par.prm"

; Include chain topologies
#include "topol_Ion_chain_7.itp"

#include "topol_RNA_chain_A.itp"
#ifdef POSRES_RES_A
#include "posre_RNA_chain_A_.itp"
#endif

#include "topol_RNA_chain_A2.itp"
#include "topol_RNA_chain_a.itp"

#ifdef POSRES_RES_a
#include "posre_RNA_chain_a_.itp"
#endif

and so on.....
```

1 Like[s.pallav](https://gromacs.bioexcel.eu/u/s.pallav) August 24, 2021, 9:00am 3![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/alevilla/48/439_2.png) alevilla:> If you use gmx genrest to generate the position restraints file, `gmx genrestr` will only produce a useful file only for the first molecule. You may wish to construct a suitable index group to provide as input to `gmx genrestr` .

Hello alevilla,

 This is exactly the problem where I am stuck at, as I want to restraint the outer portion of a RNA-protein complex. And I have atoms which I want to restraint don’t start with 1 in the chain topology(topol…itp),

 which seems to be a hurculean task at the outset.

 Then, I looked around making index groups but it seems `gmx make_ndx` does not allow one to create index groups according to residue number which would have been much easier.

 Moreover, the posre.itp file reads the topol.itp file from 1 which is the main issue, had there been some sort of easier design so that I could specifically select those residues and restrain them via this posre.itp file, maybe there could be some way to make my posre files generated by genrestr to read those desired specific residues and atoms in the topology as I want it to.

 Regards,

 Pallav

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) August 24, 2021, 10:44am 4

Hi,

![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/s.pallav/48/1099_2.png) s.pallav:> I looked around making index groups but it seems `gmx make_ndx` does not allow one to create index groups according to residue number which would have been much easier.

I guess you have tried the opition `-ri ` in gmx make_ndx or in alternative you have used gmx select to create the desired index file.

If gmx genrest does not work in your case, the alternative is manually generated the position restrain files.

An other thing not related to your answer. In my original post, I forgot to mention that it is good to check that a position restrain file is not already included in topol_…itp. In that case use different name or replace it.

 That is not related to the answer above. But I want to clarify to avoid misunderstanding.

1 Like[s.pallav](https://gromacs.bioexcel.eu/u/s.pallav) August 24, 2021, 1:10pm 5![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/alevilla/48/439_2.png) alevilla:> If gmx genrest does not work in your case, the alternative is manually generated the position restrain files.

It seems to be the only way forward but rather a tedious task to do.

![](https://dub1.discourse-cdn.com/flex017/user_avatar/gromacs.bioexcel.eu/alevilla/48/439_2.png) alevilla:> I guess you have tried the opition `-ri ` in gmx make_ndx or in alternative you have used gmx select to create the desired index file.

No matter how I make the index files, ultimately it would end up giving me posre.itp files(generated by `genrestr’) from 1 and would read the topol.itp files from 1.

 Thanks a lot,

 It seems to be much clearer now.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Atom index in position_restraints out of boundsUser discussions | 5 | 964 | October 25, 2024 |  |
| How to define position restrains on the two monomers of a dimer?User discussionsmdp-parameters,simulation-setup | 4 | 312 | August 6, 2024 |  |
| Positional restraint, grompp -r error, restraint coordinates does not match topologyUser discussionsrestraints | 1 | 1048 | August 19, 2021 |  |
| Grompp -r --does not match the number of atoms in the topologyUser discussions | 6 | 2248 | August 19, 2021 |  |
| Fix coordinates of specific residues for simulationUser discussions | 1 | 471 | August 18, 2023 |  |
