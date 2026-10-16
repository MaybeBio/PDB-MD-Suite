# Removing PBC for peptide-lipid system

> GROMACS version: 2021.3  GROMACS modification: No  Here post your question:  I ran an MD with a peptide in presence of POPG and POPE, the system was built using CHARMM-GUI with box-type HEXAGONAL, ran MD with Gromacs (2021.3). I am following instructions from the manual to design an optimal workflow for PBC connection. Few lipid molecules are still breaking and moving when I visualise in VMD.  Workflow I am using:  1. whole echo 0 | gmx trjconv -s step7_1.tpr -f step7_1.trr -o analysis2/step7_1_...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[sanjiv](https://gromacs.bioexcel.eu/u/sanjiv) February 18, 2022, 12:38pm 1

GROMACS version: 2021.3

 GROMACS modification: No

 Here post your question:

I ran an MD with a peptide in presence of POPG and POPE, the system was built using CHARMM-GUI with box-type HEXAGONAL, ran MD with Gromacs (2021.3). I am following instructions from the [manual](https://manual.gromacs.org/current/user-guide/terminology.html#suggested-workflow) to design an optimal workflow for PBC connection. Few lipid molecules are still breaking and moving when I visualise in VMD.

Workflow I am using:

# 1. whole

echo 0 | gmx trjconv -s step7_1.tpr -f step7_1.trr -o analysis2/step7_1_pbc_0_whole_trial7.xtc -pbc whole -tu ns

# 2. cluster

gmx make_ndx -f step5_input.pdb -o index2/index_POPG_POPE.ndx

 “POPG” | “POPE” # and q to save and quit

echo 18 0 | gmx trjconv -s step7_1.tpr -f analysis2/step7_1_pbc_0_whole_trial7.xtc -o analysis2/step7_1_pbc_4_whole_cluster_trial7.xtc -n index2/index_POPG_POPE.ndx -pbc cluster -tu ns

# 3. nojump

echo 0 | gmx trjconv -s step7_1.tpr -f analysis2/step7_1_pbc_4_whole_cluster_trial7.xtc -o analysis2/step7_1_pbc_4_whole_nojump_cluster_trial7.xtc -pbc nojump -tu ns

# 4. centering using -pbc mol

echo 1 0 | gmx trjconv -s step7_1.tpr -f analysis2/step7_1_pbc_4_whole_nojump_cluster_trial7.xtc -o analysis2/step7_1_pbc_4_whole_nojump_cluster_center_compact_mol_trial7.xtc -pbc mol -center -ur compact -tu ns

# visualization

vmd step7_1.gro analysis2/step7_1_pbc_4_whole_nojump_cluster_center_compact_mol_trial7.xtc

[![crop](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/d/d5d59c57634e3308f43d3aa966989d4581fbee2b_2_373x500.png)crop564×756 131 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/d/d5d59c57634e3308f43d3aa966989d4581fbee2b.png)

I am not able to figure out a way to keep those lipids intact.

Please suggest.

Thank you,

Sanjiv Kumar

1 Like[Centering a micelle in a gro file, but it's cut by box boundary](https://gromacs.bioexcel.eu/t/centering-a-micelle-in-a-gro-file-but-its-cut-by-box-boundary/12444/2)[Marius](https://gromacs.bioexcel.eu/u/Marius) February 18, 2022, 2:01pm 2

Hi Sanjiv,

 I had the same issue with pure bilayers in small rectangular boxes. Something which worked for me:

1. Center an atom in the middle of the bilayer with -pbc atom
2. Center the bilayer with -pbc mol

For your case the workflow would be:

1. Make an index group with an atom in the middle of the bilayer (Last atom in an acyl chain for example) → e.g. CenterAtom.ndx
2. gmx trjconv -s step7_1.tpr -f step7_1.trr -o analysis2/step7_1_pbc_0_atom_trial7.xtc -pbc atom -tu ns -center -n CenterAtom.ndx → Choose first the group with the atom and then the group “System”
3. Make an index group with the whole bilayer → e.g. Bilayer.ndx
4. gmx trjconv -s step7_1.tpr -f analysis2/step7_1_pbc_0_atom_trial7.xtc -o analysis2/step7_1_pbc_0_mol_trial7.xtc -pbc mol -tu ns -center -n Bilayer.ndx → Choose first the group with the bilayer and then the group “System”

Hope that helps! :)

 Cheers,

 Marius

[sanjiv](https://gromacs.bioexcel.eu/u/sanjiv) February 18, 2022, 3:41pm 3

Dear Marius,

Thank you for your quick response.

I tried your suggestions for the workflow, it took me some time to understand making an index file for the last atom in the acyl chain.

Just wanted to check with you if I am doing it right. I did the following:

### 1. Making index group with an atom in the middle of the bilayer

gmx make_ndx -f ../step5_input.pdb -o CenterAtom.ndx

a C218 | a C316 # (selected atom C218 | atom C316 (which are at the end of POPE and POPG))

### 2. Centering for the selected atoms

gmx trjconv -s ../step7_1.tpr -f ../step7_1.trr -o step7_1_pbc_0_atom_trial10.xtc -pbc atom -tu ns -center -n CenterAtom.ndx # selected new group created by index above (C218_C316) for centering and ‘system’ for output

### 3. Making an index group with the whole bilayer e.g. Bilayer.ndx

gmx make_ndx -f ../step5_input.pdb -o Bilayer.ndx

 “POPG” | “POPE” # Selecting both POPG and POPE

### 4. Centering for the selected mol (i.e. bilayer)

gmx trjconv -s ../step7_1.tpr -f step7_1_pbc_0_atom_trial10.xtc -o step7_1_pbc_0_mol_trial10.xtc -pbc mol -tu ns -center -n Bilayer.ndx # Selected POPG_POPE group created above

### 5. Visualization

vmd ../step7_1.gro step7_1_pbc_0_mol_trial10.xtc

And this worked, this time bilayer (POPG and POPE) are together during the whole run.

The only problem left now is that protein is jumping around, I guess need to use nojump using the step7_1_pbc_0_mol_trial10.xtc, without any index file?

Again, thanks a lot for your help. This was driving me crazy.

Sanjiv Kumar

[Marius](https://gromacs.bioexcel.eu/u/Marius) February 18, 2022, 6:23pm 4

Hi Sanjiv,

nice to hear that it worked! :)

 To center the protein in the box I would suggest to use again center to “fix” your protein at the center of your box:

gmx trjconv -s …/step7_1.tpr -f step7_1_pbc_0_mol_trial10.xtc -o step7_1_pbc_0_mol_protein_trial10.xtc -tu ns -center → Choose first the Protein Group and then the system.

Hope that works, too. It could fail maybe if your box in z-direction is too small…

 I would not suggest using no jump since your lipids and the protein will then “diffuse” out of the box. If you are familiar with Python you could take a look at the trajectory transformation tools of the MDAnalysis library.

Cheers,

 Marius

[sanjiv](https://gromacs.bioexcel.eu/u/sanjiv) February 21, 2022, 10:16am 5

Dear Marius,

You were right again. nojump did not work when applied directly.

Following your suggestions, centred whole thing around the ‘protein’ and selected ‘system’ for output. It gave better results, but then the membrane was jumping. So, created an index file for protein and bilayer combined and centred for the combined index, but there was some jumps in the protein. It looks much better though. I guess need to use ‘rotate and translate’ for it to centre around the protein and stabilise, I will try.

I have limited knowledge of Python, but learning it and exploring MDAnalysis library as well, looks very promising.

I was wondering, how much of trajectory transformation is required for downstream analysis, I understand it may depend on the analysis. I intend to see the influence of peptide on bilayer, so probably LiPyphilic, which is based on MDAnalysis would be helpful, but was unsure about how much trajectory transformation (for removing PBC) before beginning those analysis.

Thanks a lot for the help again.

With regards,

Sanjiv Kumar

[subhomoiBK](https://gromacs.bioexcel.eu/u/subhomoiBK) November 3, 2024, 9:17am 6

Hi Sanjiv

Did you find a solution to your problem? I followed your steps. But at some time points my peptide appears on the opposite side of the membrane.

[Nik](https://gromacs.bioexcel.eu/u/Nik) November 3, 2024, 9:54am 7

Have you checked the minimum image convention with gmx mindist command? If in some frames distance between molecules in neighboring periodic boxes is much lower than the cutoff specified for non-bonded interactions in .mpd file, that also may be the reason for jumps.

[subhomoiBK](https://gromacs.bioexcel.eu/u/subhomoiBK) November 3, 2024, 11:51am 8

Yes I have checked the minimum image convention with gmx mindist command. I am using martini 3.0. and the `rcoulomb` and `rvdw`, which are both set to 1.1 nm.

[![image](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/2/2273003c6215b8dfc5ece5a6c702f0a0f0429346.png)image1348×742 13.6 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/2X/2/2273003c6215b8dfc5ece5a6c702f0a0f0429346.png)[Nik](https://gromacs.bioexcel.eu/u/Nik) November 3, 2024, 5:02pm 9

For protein-protein complexes (where there are several chains, but all of them are of protein nature) centering by one chain or by some amino acids in one chain that are close to the mass center helps to remove jumps in one step (i.e. -pbc mol -center - n index.ndx -ur compact).

 I don’t know if centering by one chain works fine for protein-lipid system.

 I see that in the previous posts there are several centering processes (first by atom in one chain and then by protein-lipid system). May be this has some impact.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Removing pbc effectUser discussions | 13 | 11165 | April 3, 2023 |  |
| Protein-Lipid system, protein keeps flipping or jumpingUser discussionsmdrun,analysis-tools,simulation-setup | 2 | 187 | April 25, 2025 |  |
| GROMACS PBC Artifact: Protein Crossing Membrane in Visualization Despite CenteringUser discussionsanalysis-tools,simulation-setup | 5 | 657 | August 15, 2024 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3636 | October 25, 2022 |  |
| PBCs in a slightly complex systemUser discussionspbc | 7 | 132 | September 15, 2026 |  |
