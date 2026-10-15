# gmx genrestr - GROMACS 2026.4 documentation

# gmx genrestr[¶](#gmx-genrestr)

## Synopsis[¶](#synopsis)

```
gmx genrestr [**-f** *[<.gro/.g96/...>]*] [**-n** *[<.ndx>]*] [**-o** *[<.itp>]*]
             [**-of** *[<.ndx>]*] [**-fc** *<vector>*] [**-freeze** *<real>*]
             [**-[no]disre**] [**-disre_dist** *<real>*] [**-disre_frac** *<real>*]
             [**-disre_up2** *<real>*] [**-cutoff** *<real>*] [**-[no]constr**]
```

## Description[¶](#description)

`gmxgenrestr` produces an #include file for a topology containing a list of atom numbers and three force constants for the *x*-, *y*-, and *z*-direction based on the contents of the `-f` file. A single isotropic force constant may be given on the command line instead of three components.

WARNING: Position restraints are interactions within molecules, therefore they must be included within the correct `[moleculetype]` block in the topology. The atom indices within the `[position_restraints]` block must be within the range of the atom indices for that molecule type. Since the atom numbers in every moleculetype in the topology start at 1 and the numbers in the input file for `gmxgenrestr` number consecutively from 1, `gmxgenrestr` will only produce a useful file for the first molecule. You may wish to edit the resulting index file to remove the lines for later atoms, or construct a suitable index group to provide as input to `gmxgenrestr`.

The `-of` option produces an index file that can be used for freezing atoms. In this case, the input file must be a [.pdb](../reference-manual/file-formats.html#pdb) file.

With the `-disre` option, half a matrix of distance restraints is generated instead of position restraints. With this matrix, that one typically would apply to Calpha atoms in a protein, one can maintain the overall conformation of a protein without tieing it to a specific position (as with position restraints).

## Options[¶](#options)

Options to specify input files:

`-f` [&lt;.gro/.g96/…&gt;] (conf.gro)

Structure file: [gro](../reference-manual/file-formats.html#gro)[g96](../reference-manual/file-formats.html#g96)[pdb](../reference-manual/file-formats.html#pdb) brk ent esp [tpr](../reference-manual/file-formats.html#tpr)

`-n` [&lt;.ndx&gt;] (index.ndx) (Optional)

Index file

Options to specify output files:

`-o` [&lt;.itp&gt;] (posre.itp)

Include file for topology

`-of` [&lt;.ndx&gt;] (freeze.ndx) (Optional)

Index file

Other options:

`-fc` &lt;vector&gt; (1000 1000 1000)

Force constants (kJ/mol nm^2)

`-freeze` &lt;real&gt; (0)

If the `-of` option or this one is given an index file will be written containing atom numbers of all atoms that have a B-factor less than the level given here

`-[no]disre` (no)

Generate a distance restraint matrix for all the atoms in index

`-disre_dist` &lt;real&gt; (0.1)

Distance range around the actual distance for generating distance restraints

`-disre_frac` &lt;real&gt; (0)

Fraction of distance to be used as interval rather than a fixed distance. If the fraction of the distance that you specify here is less than the distance given in the previous option, that one is used instead.

`-disre_up2` &lt;real&gt; (1)

Distance between upper bound for distance restraints, and the distance at which the force becomes constant (see manual)

`-cutoff` &lt;real&gt; (-1)

Only generate distance restraints for atoms pairs within cutoff (nm)

`-[no]constr` (no)

Generate a constraint matrix rather than distance restraints. Constraints of type 2 will be generated that do generate exclusions.
