# Terminology - GROMACS 2026.4 documentation

## Periodic boundary conditions[¶](#periodic-boundary-conditions)

Periodic boundary conditions (PBC) are used in molecular dynamics simulations to avoid problems with boundary effects caused by finite size, and make the system more like an infinite one, at the cost of possible periodicity effects.

Beginners visualizing a trajectory sometimes think they are observing a problem when

- the molecule(s) does not stay in the centre of the box, or
- it appears that (parts of) the molecule(s) diffuse out of the box, or
- holes are created, or
- broken molecules appear, or
- their unit cell was a rhombic dodecahedron or cubic octahedron but it looks like a slanted cube after the simulation, or
- crazy bonds all across the simulation cell appear.

This is not a problem or error that is occurring, it is what you should expect.

The existence of PBC means that any atom that leaves a simulation box by, say, the right-hand face, then enters the simulation box by the left-hand face. In the example of a large protein, if you look at the face of the simulation box that is opposite to the one from which the protein is protruding, then a hole in the solvent will be visible. The reason why the molecule(s) move from where they were initially located within the box is that they are (for the vast majority of simulations) free to diffuse around. And so they do. They are not held in a magic location of the box. The box is not centered around anything while performing the simulation. Molecules are not made whole as a matter of course. Moreover, any periodic cell shape can be expressed as a parallelepiped (a.k.a. triclinic cell), and GROMACS does so internally regardless of the initial shape of the box.

These visual issues can be fixed after the conclusion of the simulation by judicious use of the optional inputs to [gmx trjconv](../onlinehelp/gmx-trjconv.html#gmx-trjconv) to process the trajectory files. Similarly, analyses such as RMSD of atomic positions can be flawed when a reference structure is compared with a structure that needs adjusting for periodicity effects, and the solution with [gmx trjconv](../onlinehelp/gmx-trjconv.html#gmx-trjconv) follows the same lines. Some complex cases needing more than one operation will require more than one invocation of [gmx trjconv](../onlinehelp/gmx-trjconv.html#gmx-trjconv) in order to work.

For further information, see the corresponding section in the [Reference Manual](../reference-manual/algorithms/periodic-boundary-conditions.html#pbc).

### Suggested workflow[¶](#suggested-workflow)

Fixing periodicity effects with [gmx trjconv](../onlinehelp/gmx-trjconv.html#gmx-trjconv) to suit visualization or analysis can be tricky. Multiple invocations can be necessary. You may need to create custom index groups (e.g. to keep your ligand with your protein) Following the steps below in order (omitting those not required) should help get a pleasant result. You will need to consult `gmxtrjconv-h` to find out the details for each step. That is deliberate – there is no magic “do what I want” recipe. You have to decide what you want, first. :-)

1. First make your molecules whole if you want them whole.
2. Cluster your molecules/particles if you want them clustered.
3. If you want jumps removed, extract the first frame from the trajectory to use as the reference, and then use `-pbcnojump` with that first frame as reference.
4. Center your system using some criterion. Doing so shifts the system, so do not use `-pbcnojump` after this step.
5. Perhaps put everything in some box with the other `-pbc` or `-ur` options.
6. Fit the resulting trajectory to some (other) reference structure (if desired), and do not use any PBC related option afterwards.

With point three, the issue is that [gmx trjconv](../onlinehelp/gmx-trjconv.html#gmx-trjconv) removes the jumps from the first frame using the reference structure provided with -s. If the reference structure (run input file) is not clustered/whole, using `-pbcnojump` will undo steps 1 and 2.

