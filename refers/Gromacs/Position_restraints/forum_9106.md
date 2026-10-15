# Constraint in mdp

> Hi all,  I want to constrain 2 atoms in my molecule. For that I created the indeces with gmxmake and the pose.file with gmxrestr. Right now I wonder, how I should “acitivate” the constraints in the map, beaucse the option constraint = all-atoms works constrains all atom, right? And do I have to set up a constraint-algorithm?

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[juliara](https://gromacs.bioexcel.eu/u/juliara) May 8, 2024, 9:24am 1

Hi all,

I want to constrain 2 atoms in my molecule. For that I created the indeces with gmxmake and the pose.file with gmxrestr. Right now I wonder, how I should “acitivate” the constraints in the map, beaucse the option constraint = all-atoms works constrains all atom, right? And do I have to set up a constraint-algorithm?

[milosz.wieczor](https://gromacs.bioexcel.eu/u/milosz.wieczor) May 8, 2024, 4:00pm 2

You mean `gmx genrestr`? This command generates restraints, not constraints (make sure you know the difference between these two).

In a Gromacs topology file, the preprocessor allows you to use a syntax like

```
#ifdef MY_KEYWORD
#include "myposresfile.itp"
#endif
```

and then `myposresfile.itp` will be included in that site if your `.mdp` file contains

```
define = -DMY_KEYWORD ; (that's not a typo, the -D is needed)
```

which is useful if you want to include or exclude some sections based on your `.mdp` settings.

Of course, instead of writing `#include "myposresfile.itp"` you can literally paste the content of that file - works the same, except this way you don’t need to move this file around as a dependency before running `gmx grompp`.

1 Like[juliara](https://gromacs.bioexcel.eu/u/juliara) May 8, 2024, 5:12pm 3

Thank you for you response, but in the .mdp-file, do I need to put the actual name for the -DMY_KEYWORD e.g. -DCLAHIS_posre.itp?

[MagnusL](https://gromacs.bioexcel.eu/u/MagnusL) May 9, 2024, 8:48am 4

No, in the .mdp file, the `define` statement only defines/sets certain keywords/statements. These do not correspond to specific restraint files or anything like that. In the example provided above,

`-DMY_KEYWORD` should just correspond to `MY_KEYWORD` in the `#ifdef` statements in the topology file (or its included .itp files). The `#include "myposresfile.itp"` is where you should specify the file name of the file containing the restraings, e.g., `CLAHIS_posre.itp`. [https://manual.gromacs.org/current/user-guide/getting-started.html#topology-include-file-mechanism](https://manual.gromacs.org/current/user-guide/getting-started.html#topology-include-file-mechanism) might shed some more light on this.

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| Fix coordinates of specific residues for simulationUser discussions | 1 | 471 | August 18, 2023 |  |
| Position restraintsUser discussions | 1 | 6155 | August 13, 2020 |  |
| Missing define in .mdp Extracted from .tpr and Restraint ConfirmationUser discussionsmdp-parameters | 4 | 125 | January 10, 2025 |  |
| How to add Position restrain in .mdp fileUser discussionsmdp-parameters | 0 | 250 | October 3, 2023 |  |
| Using positional restraints for atoms of the perimeterUser discussionsrestraints | 4 | 1479 | August 24, 2021 |  |
