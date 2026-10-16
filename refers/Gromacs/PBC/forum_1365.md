# Pbc nojump not working?

> Hello everyone,  I have a gro file from an equilibration run of my protein. When I opened this using VMD, parts of the protein have moved out of the water box. I tried the following command to move the protein back into the water box as follows,  gmx trjconv -f equilibration.gro -s equilibration.tpr -o equilibration_pbc.gro -pbc nojump  However, the new gro file still looks the same as the old one. Am I doing something wrong? Also, does this have anything to do with comm-grps or compressed-x grp...

### [Terminology — GROMACS 2020.4 documentation](https://manual.gromacs.org/current/user-guide/terminology.html#suggested-workflow)
