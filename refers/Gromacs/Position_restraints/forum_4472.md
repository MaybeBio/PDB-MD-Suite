# Running Protein simulation with multiple ligands

> GROMACS version: 2018  Hello everyone,  I am new to GROMACS and trying to run a protein simulation with chromophores FAD and DLZ and DNA as ligands using Amber ff99sb force field. While running the simulation how should I generate the index files for the chromophores? Should I generate three different index files each for FAD DLZ and DNA and then club it as one? In that case how should I do that? or is there any other way for indexing multiple ligands. Thank you very much for your help.

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[Bidisha](https://gromacs.bioexcel.eu/u/Bidisha) July 17, 2022, 8:05am 1

GROMACS version: 2018

Hello everyone,

 I am new to GROMACS and trying to run a protein simulation with chromophores FAD and DLZ and DNA as ligands using Amber ff99sb force field. While running the simulation how should I generate the index files for the chromophores? Should I generate three different index files each for FAD DLZ and DNA and then club it as one? In that case how should I do that? or is there any other way for indexing multiple ligands. Thank you very much for your help.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) July 26, 2022, 12:00pm 2

Hi,

 to generate an index file you can use the tool gmx make_ndx [gmx make_ndx — GROMACS 2022.2 documentation](https://manual.gromacs.org/current/onlinehelp/gmx-make_ndx.html) or gmx select [gmx select — GROMACS 2022.2 documentation](https://manual.gromacs.org/current/onlinehelp/gmx-select.html). An index file can contain several groups. You can define a group for each chromophore if you want.

 \Alessandra

[Bidisha](https://gromacs.bioexcel.eu/u/Bidisha) August 9, 2022, 5:34pm 3

Thank you very much for your help. It worked. Could help me regarding restraining the DNA ligand, in the same system? Thank you.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) August 11, 2022, 8:21am 4

Hi,

 do you mean how to position-restrain the DNA? Or do you refer to other type of restraints ([Restraints — GROMACS 2022.2 documentation](https://manual.gromacs.org/current/reference-manual/functions/restraints.html))?

 \Alessandra

[Bidisha](https://gromacs.bioexcel.eu/u/Bidisha) August 11, 2022, 8:38am 5

Hello,

Yes I mean the position restraint of DNA in a Protein-DNA simulation.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) August 12, 2022, 2:52pm 6

Hi,

 FIrst you need a posre.itp type of file in the working directory and this file has to be correctly included in the topology file. To do that you can use [https://manual.gromacs.org/current/onlinehelp/gmx-genrestr.html](https://manual.gromacs.org/current/onlinehelp/gmx-genrestr.html). The tool generate the file you needs and include them in the topology.

 If you have use gmx pdb2gmx to create the topology of the whole system, a position restrain file for DNA (e.i posre.itp type of file) has been already created and include in the proper place in the topology files.

Then you tell the program to use posre file, and you can do it in the in mdp file using the option `define`

> define
>  defines to pass to the preprocessor, default is no defines. You can use any defines to control options in your customized topology files. Options that act on existing [top](https://manual.gromacs.org/current/reference-manual/file-formats.html#top) file mechanisms include
> 
> `-DPOSRES` will trigger the inclusion of `posre.itp` into your topology, used for implementing position restraints.

For example at the end of the dna.itp file you read something like this

#ifdef POSRESdna

#include “posre_DNA.itp”

#endif

Then define = -DPOSRESdna in the mdp file. This will activate the position restrain only on the DNA, only if POSRESdna is only defined in the dna.itp.

\Alessandra

[Bidisha](https://gromacs.bioexcel.eu/u/Bidisha) August 16, 2022, 6:55am 7

Thank you so much for your help Ma’am. As I am new to this I have another query regarding a problem that I am facing. I shall be highly obliged if you could kindly help me out with this.

This molecule too has two chromophores. So I created two separate atomtypes.itp for two chromophores and incorporated the two files (ligand1_atomtypes.itp and ligand2_atomtypes.itp) separately in the topol.top file. and also incorporated the two Ligand.gro files of two separate ligands into the protein.gro and then while using gmx grompp -f ions.mdp -c solv.gro -p topol.top -o ions.tpr i am having to many warnings and error. What is the correct way to go about it? I am attaching the files here for your reference.

[![error3](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/a/ab6b1481486090188037b313e65be3aedbbcd583_2_666x500.jpeg)error31920×1440 205 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/a/ab6b1481486090188037b313e65be3aedbbcd583.jpeg)

[![error2](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/9/97967fa9993828ed2ccd436f2f70c95a29bebb76_2_641x500.jpeg)error21920×1497 218 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/9/97967fa9993828ed2ccd436f2f70c95a29bebb76.jpeg)

[![error1](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/b/b53cab94a908f266fbfea7a4aa17b8b9b43a7438_2_669x500.jpeg)error11920×1434 255 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/b/b53cab94a908f266fbfea7a4aa17b8b9b43a7438.jpeg)

Thank you for your time and consideration.

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) August 16, 2022, 9:23am 8

Hi,

the error says that parameters are re-refined in the topology files.

 You probably have a directive in *itp files before [ moleculetype ], where non-bonded parameters are defined. Those definitions overwrite any previous parameter definition.

 Do you want to redefine standard force field parameters? Then one should define those new parameters only once at the top of the topol files and not in each itp files.

 For topology format see [File formats — GROMACS 2022.2 documentation](https://manual.gromacs.org/current/reference-manual/topologies/topology-file-formats.html?highlight=force%20field%20table)

I hope it helps

 Alessandra

[sunilsthorat](https://gromacs.bioexcel.eu/u/sunilsthorat) March 29, 2024, 3:57am 9

Hello Madam,

 I am performing multi ligand MD simulation (5 ligands), I am following GROMACS Tutorials for Protein-ligand complex and created respective *.itp and *.prm files and included in the topol.top file. I have sucessfully done solvation and got stuck while assembling *.tpr files using grompp &lt;gmx grompp -f em.mdp -c solvated_ions.gro -p topol.top -o em.tpr&gt;.

 I am getting WARNING messages for 2 *.prm files out 5 and ERROR messages for the same. Fatal error: Syntax error was for first liand *.itp file at [ atomtypes ] as Invalid order for directive atomtypes.

###############ERROR MSG##################

 $ gmx grompp -f em.mdp -c solvated_ions.gro -p topol.top -o em.tpr

 :-) GROMACS - gmx grompp, 2020.1-Ubuntu-2020.1-1 (-:

Ignoring obsolete mdp entry ‘title’

 Ignoring obsolete mdp entry ‘ns_type’

NOTE 1 [file em.mdp]:

 With Verlet lists the optimal nstlist is &gt;= 10, with GPUs &gt;= 20. Note

 that with the Verlet scheme, nstlist has no effect on the accuracy of

 your simulation.

Setting the LD random seed to 1535351374

WARNING 1 [file astra_CHARMM.prm, line 1-98]:

 Too few parameters on line (source file

 /build/gromacs-NyEPF4/gromacs-2020.1/src/gromacs/gmxpreprocess/toppush.cpp, line 1039)

ERROR 21 [file astra_CHARMM.prm, line 99]:

 Trying to add Buck.ham (SR) while the default nonbond type is LJ (SR)

WARNING 74 [file ella_CHARMM.prm, line 1-4]:

 Too few parameters on line (source file

 /build/gromacs-NyEPF4/gromacs-2020.1/src/gromacs/gmxpreprocess/toppush.cpp, line 1039)

ERROR 35 [file ella_CHARMM.prm, line 5-12]:

 Trying to add Buck.ham (SR) while the default nonbond type is LJ (SR)

WARNING 77 [file ella_CHARMM.prm, line 14-44]:

 Too few parameters on line (source file

 /build/gromacs-NyEPF4/gromacs-2020.1/src/gromacs/gmxpreprocess/toppush.cpp, line 1039)

ERROR 44 [file ella_CHARMM.prm, line 45-51]:

 Trying to add Buck.ham (SR) while the default nonbond type is LJ (SR)

Generated 167799 of the 167910 non-bonded parameter combinations

 Generating 1-4 interactions: fudge = 1

 Generated 117432 of the 167910 1-4 parameter combinations

---

Program: gmx grompp, version 2020.1-Ubuntu-2020.1-1

 Source file: src/gromacs/gmxpreprocess/topio.cpp (line 553)

Fatal error:

 Syntax error - File astra_GMX.itp, line 3

 Last line read:

 ‘[ atomtypes ]’

 Invalid order for directive atomtypes

 #######################################################

I am attaching the topol.top and respective *.itp and *.prm files for your reference (renamed as log files for uploading)

[astra_GMX_itp.log](https://gromacs.bioexcel.eu/uploads/short-url/pQkSh8yPyeIaFhNhqVqdImwstxz.log) (37.9 KB)

[astra_CHARMM_prm.log](https://gromacs.bioexcel.eu/uploads/short-url/8qcXrLJ5mZn6cG4FAE1xq3WYpZj.log) (4.2 KB)

 .

 Please suggest the solution.

[topol.top](https://gromacs.bioexcel.eu/uploads/short-url/8Vttayh5lhpnZ6jSFyY8IZqra29.top) (1.2 MB)

[ella_CHARMM_prm.log](https://gromacs.bioexcel.eu/uploads/short-url/zPxZWOyS8G0PmQ7oI3djQhGNUov.log) (1.7 KB)

[scinikhil](https://gromacs.bioexcel.eu/u/scinikhil) March 29, 2024, 11:31pm 10

[https://manual.gromacs.org/2020.2/user-guide/run-time-errors.html#invalid-order-for-directive-xxx](https://manual.gromacs.org/2020.2/user-guide/run-time-errors.html#invalid-order-for-directive-xxx)

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Using positional restraints for atoms of the perimeterUser discussionsrestraints | 4 | 1479 | August 24, 2021 |  |
| Preparing index fileUser discussions | 0 | 61 | January 5, 2025 |  |
| RMSD analysis of the Protein-Ligand simulationUser discussions | 0 | 50 | July 5, 2026 |  |
| In Restraining the Ligand ligand option is not thereUser discussionsrestraints | 8 | 438 | November 1, 2023 |  |
| Can anyone please help meUser discussionsforcefield | 6 | 581 | October 31, 2023 |  |
