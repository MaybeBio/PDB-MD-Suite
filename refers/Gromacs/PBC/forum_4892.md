# RDF and PBC corrections

> GROMACS version: 2018  GROMACS modification: No  Dear all,  I want to calculate the RDF of water molecules close to my ligand. I have recentered my protein ligand system using the following commands:  gmx trjconv -s sys.md1.tpr -f sys.md1.xtc -o sys.md1.whole.xtc -pbc whole  gmx trjconv -s sys.md1.tpr -f sys.md1.whole.xtc -o sys.md1.whole.nojump.xtc -pbc nojump  gmx trjconv -s sys.md1.tpr -f sys.md1.whole.nojump.xtc -o sys.md1.whole.nojump.mol.xtc -pbc mol  After these steps, my protein-ligand s...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[analysis-tools](https://gromacs.bioexcel.eu/tag/analysis-tools), [gmx-trjconv](https://gromacs.bioexcel.eu/tag/gmx-trjconv)[sallaprat](https://gromacs.bioexcel.eu/u/sallaprat) September 27, 2022, 9:45pm 1

GROMACS version: 2018

 GROMACS modification: No

Dear all,

I want to calculate the RDF of water molecules close to my ligand. I have recentered my protein ligand system using the following commands:

gmx trjconv -s sys.md1.tpr -f sys.md1.xtc -o sys.md1.whole.xtc -pbc whole

gmx trjconv -s sys.md1.tpr -f sys.md1.whole.xtc -o sys.md1.whole.nojump.xtc -pbc nojump

gmx trjconv -s sys.md1.tpr -f sys.md1.whole.nojump.xtc -o sys.md1.whole.nojump.mol.xtc -pbc mol

After these steps, my protein-ligand system is whole and centered but the waters have drifted away from the box and are all over the place. I was wondering if there is a better way to fix the PBC in order to obtain sensible RDF results.

Thank you very much in advance,

Sara Llopart

[alevilla](https://gromacs.bioexcel.eu/u/alevilla) September 28, 2022, 10:25am 2

Hi,

 maybe this workflow may help

[https://manual.gromacs.org/current/user-guide/terminology.html?highlight=workflow](https://manual.gromacs.org/current/user-guide/terminology.html?highlight=workflow)

 \Alessandra

[sallaprat](https://gromacs.bioexcel.eu/u/sallaprat) September 28, 2022, 9:51pm 3

Thank you Alessandra,

I managed to fix the PBC using the following commands:

```
echo 0 | gmx trjconv -s sys.md1.tpr -f sys.md1.xtc -o sys.md1.whole.xtc -pbc whole

echo 0 | gmx trjconv -s sys.md1.tpr -f sys.md1.whole.xtc -o sys.md1.whole.nojump.xtc -pbc nojump

echo 1 0 | gmx trjconv -s sys.md1.tpr -f sys.md1.whole.nojump.xtc -o sys.md1.whole.nojump.tric.xtc -pbc mol -ur tric -c
```

Sara

1 Like[sallaprat](https://gromacs.bioexcel.eu/u/sallaprat) October 1, 2022, 4:28pm 4

This is the correct fix:

```
echo 0 | gmx trjconv -s sys.md1.tpr -f .sys.md1.xtc -o sys.md1.whole.xtc -pbc whole -skip 100

echo 0 | gmx trjconv -s sys.md1.tpr -f sys.md1.whole.xtc -o sys.md1.whole.nojump.xtc -pbc nojump -ur tric

echo 1  0 | gmx trjconv -s sys.md1.tpr -f sys.md1.whole.nojump.xtc -o sys.md1.whole.nojump.tric.xtc -pbc atom -ur tric -center 

echo 0 | gmx trjconv -s sys.md1.tpr -f sys.md1.whole.nojump.tric.xtc -o sys.md1.fixed.xtc -pbc whole -ur tric
```

Sara

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Correcting Periodicity in GMXUser discussions | 9 | 6575 | May 28, 2020 |  |
| Re-centering the protein in the box after MD simulationUser discussions | 6 | 7551 | March 22, 2022 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 202 | January 15, 2025 |  |
| Seemingly unresolvable PBC problem on protein complexUser discussions | 3 | 3637 | October 25, 2022 |  |
