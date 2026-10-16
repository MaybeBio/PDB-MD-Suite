# Calculating RMSF if the reference structure is broken across PBC

> GROMACS version: 2020.3  GROMACS modification: No  Here post your question:  Hello everyone,  I would like to discuss about RMSF calculation, if the protein happens to be broken over the periodic boundary at the start of the production run. Most of the gromacs tutorials online suggest using the run input file as the reference structure on a cleaned trajectory -   echo “Protein” | gmx convert-tpr -s run.tpr -o protein.tpr  echo -e “Protein\nProtein” | gmx trjconv -f traj.xtc -s run.tpr -o traj_cl...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools)[Arkadeep](https://gromacs.bioexcel.eu/u/Arkadeep) August 13, 2021, 6:27am 1

**GROMACS version:** 2020.3

**GROMACS modification:** No

**Here post your question:**

Hello everyone,

I would like to discuss about RMSF calculation, if the protein happens to be broken over the periodic boundary at the start of the production run. Most of the gromacs tutorials online suggest using the run input file as the reference structure on a cleaned trajectory -

> echo “Protein” | gmx convert-tpr -s run.tpr -o protein.tpr
>  echo -e “Protein\nProtein” | gmx trjconv -f traj.xtc -s run.tpr -o traj_clean.xtc -center -ur compact -pbc mol
>  echo -e “C-alpha\nC-alpha” | gmx rmsf -f traj_clean.xtc -s protein.tpr -o rmsf.xvg

but I think a broken protein molecule would produce a wrong RMSF plot. Since it is not possible to alter the tpr file and make the protein whole, a pdb having the unbroken protein seems like a better choice for the reference structure. I am new to gromacs and it would be very helpful if the more experienced users can provide some advice.

For some context, I am doing an MD simulation of a protein in water, with two replicates. But the RMSF plots do not match between the replicates (Figure 1). Since new users cannot have more than 1 image in a post, [I have uploaded the images to this google drive folder](https://drive.google.com/drive/folders/1JD3f-IzWQ8tVRqmt99-1YnqZq2qZ1xRV?usp=sharing).

Upon closer inspection, I realized that the protein was broken across the periodic boundary at time t=0 in replicate B but not in A. This was because before the production run of 600ns, I had an NPT equilibration step of 10ns, during which the protein drifted out of the box in replicate B.

To check if protein being broken is the reason behind the RMSF mismatch, I calculated RMSF of the two replicates using the same run input file (from replicate A, with a whole protein) as the reference structure for both. The RMSF obtained this way was very similar between the replicates (Figure 2A). The vice-versa was also true - RMSF of both the replicates was very similar when the same run input file (from replicate B, with a broken protein) was used for both (Figure 2B).

To better understand the effect of PBC artifacts while calculating RMSF, I obtained RMSF with various combinations of broken and whole reference structures on raw trajectories and cleaned trajectories. The raw trajectory was just the actual trajectory and clean trajectory had the protein centered and PBC effects removed. The whole reference structures were the run input file or the first frame of replicate A, while the broken reference structures were those files from replicate B.

> echo “Protein” | gmx trjconv -f traj.xtc -s run.tpr -o traj_raw.xtc
>  echo -e “Protein\nProtein” | gmx trjconv -f traj.xtc -s run.tpr -o traj_clean.xtc -center -ur compact -pbc mol
>  echo “Protein” | gmx trjconv -f traj.xtc -s run.tpr -o frame_0.pdb -dump 0
>  echo “Protein” | gmx convert-tpr -s run.tpr -o run_protein.tpr

Thus, RMSF could be calculated in 8 different ways for each replicate (reference structure being **whole** or **broken**, reference structure format being **tpr** or **pdb**, trajectory being **raw** or **clean**). I compared RMSF among these combinations and [these results are available here](https://docs.google.com/spreadsheets/d/1Wd9U-Fh_-XpyyN6CtSjLPgdcBsbRjxpeChIaa7d6yZE/edit?usp=sharing). The main takeaways are -

1. When the reference structure is in pdb format, a clean trajectory has to be provided to generate a realistic RMSF plot. This is expected as gromacs itself gives a warning about broken molecules not being made whole in the trajectory when not using a tpr file as the reference.
2. When the reference structure is in tpr format, the trajectory need not be cleaned - RMSF of a raw trajectory and that of a clean trajectory are identical.
3. If the trajectory is clean, then RMSF does not depend on the format of the reference structure - using both pdb and tpr gives identical plots.
4. The RMSF calculated from a broken reference structure is always higher, irrespective of the reference structure format being tpr/pdb and the trajectory being raw/clean (except in case of a raw trajectory used with a non-tpr reference structure, as stated in point 1). Gromacs can make a broken trajectory whole when provided with a tpr file, but I speculate that it cannot make the reference structure itself whole in the tpr file. As it is probably difficult to align a whole protein to a broken reference, the RMSF becomes higher.

To confirm the issue, RMSF should be different when calculated using reference structures which were broken differently. In the replicate which had the protein broken at the end of NPT equilibration, I extracted the protein every 500th frame of the NPT step. This produced 11 different structures and conincidentally, all of them were broken. These structures were used as references to calculate RMSF over the clean (production run) trajectory. To ensure the RMSF differences (if any) were due to the protein being broken differently and not due to different conformations of the protein, RMSF should be identical if the protein was made whole in the reference structure.

> echo “Protein” | gmx trjconv -f traj.xtc -s run.tpr -skip 500 -sep -o NPT_raw_out.pdb
>  echo “Protein” | gmx trjconv -f traj.xtc -s run.tpr -skip 500 -sep -o NPT_clean_out.pdb -center -ur compact -pbc mol

Indeed, RMSF is quite different if the reference structures are broken differently (Figure 3A), and identical if those reference structures are made whole (Figure 3B). Thus, it seems like the reference structure used for calculating RMSF should always have the protein whole. And since it is not possible to always ensure the protein is unbroken in the run input file, using a pdb/gro file as the reference would be a safer way (despite the gromacs warning).

Sorry for the long post. More than a question, I would really like to have a discussion about reference structures for gmx rmsf. I had spent a lot of time trying to figure this out and any input would be appreciated.

Thanks in advance,

 Arkadeep

[rjtpunia](https://gromacs.bioexcel.eu/u/rjtpunia) August 19, 2021, 12:11pm 2

You can use .tpr file of NPT equilibration run as the reference structure for RMSF calculation.

 Or for both cases you can find the average structure in the cleaned production trajectory (e.g. using gmx cluster) and use it as a reference structure for rmsf calculation

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| PBC effect on RMSD calculationUser discussionspbc,analysis-tools,gmx-trjconv | 2 | 142 | October 1, 2025 |  |
| Large RMSD Differences of Homologous ProteinsUser discussions | 30 | 3812 | November 4, 2020 |  |
| Rmsf according to referans gro filesUser discussionsanalysis-tools | 1 | 296 | October 4, 2023 |  |
| Fit Gromacs trajectory to a "broken" pdb file (transmembrane protein RMSF)User discussionsanalysis-tools | 3 | 653 | May 12, 2022 |  |
| Rmsd drops at the last framesUser discussions | 3 | 932 | December 4, 2020 |  |
