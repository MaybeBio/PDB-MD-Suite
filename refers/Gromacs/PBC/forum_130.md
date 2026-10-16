# Multiple pbc options for gmx trjconv?

> GROMACS version: gromacs/2018.1-openmpi3-5ds3yf7  GROMACS modification: No  I am wanting to use multiple pbc options when converting the trajs of my simulation, namely “mol” and “nojump”. Can this be done? And if so, how?  I have tried a few different ways already:  “-pbc mol nojump” --> received error “too many values”  “-pbc mol -pbc nojump” --> received error “option specified multiple times”

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[jazellim](https://gromacs.bioexcel.eu/u/jazellim) May 13, 2020, 3:39pm 1

GROMACS version: gromacs/2018.1-openmpi3-5ds3yf7

 GROMACS modification: No

 I am wanting to use multiple pbc options when converting the trajs of my simulation, namely “mol” and “nojump”. Can this be done? And if so, how?

I have tried a few different ways already:

 “-pbc mol nojump” --&gt; received error “too many values”

 “-pbc mol -pbc nojump” --&gt; received error “option specified multiple times”

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) May 13, 2020, 3:55pm 2

You can only specify one type of PBC operation. If you want/need multiple types of PBC correction, they have to be done in separate, sequential, invocations of `trjconv`.

1 Like

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Handling of PBCs with multiple peptidesUser discussionspbc | 2 | 58 | January 7, 2025 |  |
| Issue: Unable to Remove PBC in GROMACS Using trjconv OptionsUser discussionsgmx-trjconv | 1 | 189 | March 24, 2025 |  |
| Issue with correcting PBC for DNA Separation in GROMACSUser discussionspbc | 7 | 202 | January 15, 2025 |  |
| PBC correction doesn't remove all PBCsUser discussionspbc,gmx-trjconv | 0 | 706 | November 2, 2022 |  |
| Gmx trjconv -fitUser discussionsanalysis-tools | 4 | 886 | November 29, 2023 |  |
