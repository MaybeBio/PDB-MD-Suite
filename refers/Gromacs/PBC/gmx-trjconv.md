# gmx trjconv - GROMACS 2026.4 documentation

# gmx trjconv[¶](#gmx-trjconv)

## Synopsis[¶](#synopsis)

```
gmx trjconv [**-f** *[<.xtc/.trr/...>]*] [**-s** *[<.tpr/.gro/...>]*] [**-n** *[<.ndx>]*]
            [**-fr** *[<.ndx>]*] [**-sub** *[<.ndx>]*] [**-drop** *[<.xvg>]*]
            [**-o** *[<.xtc/.trr/...>]*] [**-b** *<time>*] [**-e** *<time>*]
            [**-tu** *<enum>*] [**-[no]w**] [**-xvg** *<enum>*] [**-skip** *<int>*]
            [**-dt** *<time>*] [**-[no]round**] [**-dump** *<time>*] [**-t0** *<time>*]
            [**-timestep** *<time>*] [**-pbc** *<enum>*] [**-ur** *<enum>*]
            [**-[no]center**] [**-boxcenter** *<enum>*] [**-box** *<vector>*]
            [**-trans** *<vector>*] [**-shift** *<vector>*] [**-fit** *<enum>*]
            [**-ndec** *<int>*] [**-[no]vel**] [**-[no]force**] [**-trunc** *<time>*]
            [**-exec** *<string>*] [**-split** *<time>*] [**-[no]sep**]
            [**-nzero** *<int>*] [**-dropunder** *<real>*] [**-dropover** *<real>*]
            [**-[no]conect**]
```

## Description[¶](#description)

`gmxtrjconv` can convert trajectory files in many ways:

- from one format to another
- select a subset of atoms
- change the periodicity representation
- keep multimeric molecules together
- center atoms in the box
- fit atoms to reference structure
- reduce the number of frames
- change the timestamps of the frames (`-t0` and `-timestep`)
- select frames within a certain range of a quantity given in an [.xvg](../reference-manual/file-formats.html#xvg) file.

The option to write subtrajectories (-sub) based on the information obtained from cluster analysis has been removed from `gmxtrjconv` and is now part of [gmx extract-cluster]

[gmx trjcat](gmx-trjcat.html) is better suited for concatenating multiple trajectory files.

The following formats are supported for input and output: [.xtc](../reference-manual/file-formats.html#xtc), [.trr](../reference-manual/file-formats.html#trr), [.gro](../reference-manual/file-formats.html#gro), `.g96`, [.pdb](../reference-manual/file-formats.html#pdb) and [.tng](../reference-manual/file-formats.html#tng). The file formats are detected from the file extension. The precision of the [.xtc](../reference-manual/file-formats.html#xtc) output is taken from the input file for [.xtc](../reference-manual/file-formats.html#xtc), [.gro](../reference-manual/file-formats.html#gro) and [.pdb](../reference-manual/file-formats.html#pdb), and from the `-ndec` option for other input formats. The precision is always taken from `-ndec`, when this option is set. All other formats have fixed precision. [.trr](../reference-manual/file-formats.html#trr) output can be single or double precision, depending on the precision of the `gmxtrjconv` binary. Note that velocities are only supported in [.trr](../reference-manual/file-formats.html#trr), [.tng](../reference-manual/file-formats.html#tng), [.gro](../reference-manual/file-formats.html#gro) and `.g96` files.

Option `-sep` can be used to write every frame to a separate `.gro,.g96` or [.pdb](../reference-manual/file-formats.html#pdb) file. By default, all frames all written to one file. [.pdb](../reference-manual/file-formats.html#pdb) files with all frames concatenated can be viewed with `rasmol-nmrpdb`.

It is possible to select part of your trajectory and write it out to a new trajectory file in order to save disk space, e.g. for leaving out the water from a trajectory of a protein in water. **ALWAYS** put the original trajectory on tape! We recommend to use the portable [.xtc](../reference-manual/file-formats.html#xtc) format for your analysis to save disk space and to have portable files. When writing [.tng](../reference-manual/file-formats.html#tng) output the file will contain one molecule type of the correct count if the selection name matches the molecule name and the selected atoms match all atoms of that molecule. Otherwise the whole selection will be treated as one single molecule containing all the selected atoms.

There are two options for fitting the trajectory to a reference either for essential dynamics analysis, etc. The first option is just plain fitting to a reference structure in the structure file. The second option is a progressive fit in which the first timeframe is fitted to the reference structure in the structure file to obtain and each subsequent timeframe is fitted to the previously fitted structure. This way a continuous trajectory is generated, which might not be the case when using the regular fit method, e.g. when your protein undergoes large conformational transitions.

Option `-pbc` sets the type of periodic boundary condition treatment:

> - `mol` puts the center of mass of molecules in the box, and requires a run input file to be supplied with `-s`.
- `res` puts the center of mass of residues in the box.
- `atom` puts all the atoms in the box.
- `nojump` checks if atoms jump across the box and then puts them back. This has the effect that all molecules will remain whole (provided they were whole in the initial conformation). **Note** that this ensures a continuous trajectory but molecules may diffuse out of the box. The starting configuration for this procedure is taken from the structure file, if one is supplied, otherwise it is the first frame.
- `cluster` clusters all the atoms in the selected index such that they are all closest to the center of mass of the cluster, which is iteratively updated. **Note** that this will only give meaningful results if you in fact have a cluster. Luckily that can be checked afterwards using a trajectory viewer. Note also that if your molecules are broken this will not work either.
- `whole` only makes broken molecules whole.

Option `-ur` sets the unit cell representation for options `mol`, `res` and `atom` of `-pbc`. All three options give different results for triclinic boxes and identical results for rectangular boxes. `rect` is the ordinary brick shape. `tric` is the triclinic unit cell. `compact` puts all atoms at the closest distance from the center of the box. This can be useful for visualizing e.g. truncated octahedra or rhombic dodecahedra. The center for options `tric` and `compact` is `tric` (see below), unless the option `-boxcenter` is set differently.

Option `-center` centers the system in the box. The user can select the group which is used to determine the geometrical center. Option `-boxcenter` sets the location of the center of the box for options `-pbc` and `-center`. The center options are: `tric`: half of the sum of the box vectors, `rect`: half of the box diagonal, `zero`: zero. Use option `-pbcmol` in addition to `-center` when you want all molecules in the box after the centering.

Option `-box` sets the size of the new box. This option only works for leading dimensions and is thus generally only useful for rectangular boxes. If you want to modify only some of the dimensions, e.g. when reading from a trajectory, you can use -1 for those dimensions that should stay the same It is not always possible to use combinations of `-pbc`, `-fit`, `-ur` and `-center` to do exactly what you want in one call to `gmxtrjconv`. Consider using multiple calls, and check out the GROMACS website for suggestions.

With `-dt`, it is possible to reduce the number of frames in the output. This option relies on the accuracy of the times in your input trajectory, so if these are inaccurate use the `-timestep` option to modify the time (this can be done simultaneously). For making smooth movies, the program [gmx filter](gmx-filter.html) can reduce the number of frames while using low-pass frequency filtering, this reduces aliasing of high frequency motions.

Using `-trunc``gmxtrjconv` can truncate [.trr](../reference-manual/file-formats.html#trr) in place, i.e. without copying the file. This is useful when a run has crashed during disk I/O (i.e. full disk), or when two contiguous trajectories must be concatenated without having double frames.

Option `-dump` can be used to extract a frame at or near one specific time from your trajectory. If the frames in the trajectory are not in temporal order, the result is unspecified.

Option `-drop` reads an [.xvg](../reference-manual/file-formats.html#xvg) file with times and values. When options `-dropunder` and/or `-dropover` are set, frames with a value below and above the value of the respective options will not be written.

## Options[¶](#options)

Options to specify input files:

`-f` [&lt;.xtc/.trr/…&gt;] (traj.xtc)

Trajectory: [xtc](../reference-manual/file-formats.html#xtc)[trr](../reference-manual/file-formats.html#trr)[cpt](../reference-manual/file-formats.html#cpt)[gro](../reference-manual/file-formats.html#gro)[g96](../reference-manual/file-formats.html#g96)[pdb](../reference-manual/file-formats.html#pdb)[tng](../reference-manual/file-formats.html#tng) h5md

`-s` [&lt;.tpr/.gro/…&gt;] (topol.tpr) (Optional)

Structure+mass(db): [tpr](../reference-manual/file-formats.html#tpr)[gro](../reference-manual/file-formats.html#gro)[g96](../reference-manual/file-formats.html#g96)[pdb](../reference-manual/file-formats.html#pdb) brk ent

`-n` [&lt;.ndx&gt;] (index.ndx) (Optional)

Index file

`-fr` [&lt;.ndx&gt;] (frames.ndx) (Optional)

Index file

`-sub` [&lt;.ndx&gt;] (cluster.ndx) (Optional)

Index file

`-drop` [&lt;.xvg&gt;] (drop.xvg) (Optional)

xvgr/xmgr file

Options to specify output files:

`-o` [&lt;.xtc/.trr/…&gt;] (trajout.xtc)

Trajectory: [xtc](../reference-manual/file-formats.html#xtc)[trr](../reference-manual/file-formats.html#trr)[gro](../reference-manual/file-formats.html#gro)[g96](../reference-manual/file-formats.html#g96)[pdb](../reference-manual/file-formats.html#pdb)[tng](../reference-manual/file-formats.html#tng) h5md

Other options:

`-b` &lt;time&gt; (0)

Time of first frame to read from trajectory (default unit ps)

`-e` &lt;time&gt; (0)

Time of last frame to read from trajectory (default unit ps)

`-tu` &lt;enum&gt; (ps)

Unit for time values: fs, ps, ns, us, ms, s

`-[no]w` (no)

View output [.xvg](../reference-manual/file-formats.html#xvg), [.xpm](../reference-manual/file-formats.html#xpm), [.eps](../reference-manual/file-formats.html#eps) and [.pdb](../reference-manual/file-formats.html#pdb) files

`-xvg` &lt;enum&gt; (xmgrace)

xvg plot formatting: xmgrace, xmgr, none

`-skip` &lt;int&gt; (1)

Only write every nr-th frame

`-dt` &lt;time&gt; (0)

Only write frame when t MOD dt = first time (ps)

`-[no]round` (no)

Round measurements to nearest picosecond

`-dump` &lt;time&gt; (-1)

Dump frame nearest specified time (ps)

`-t0` &lt;time&gt; (0)

Starting time (ps) (default: don’t change)

`-timestep` &lt;time&gt; (0)

Change time step between input frames (ps)

`-pbc` &lt;enum&gt; (none)

PBC treatment (see help text for full description): none, mol, res, atom, nojump, cluster, whole

`-ur` &lt;enum&gt; (rect)

Unit-cell representation: rect, tric, compact

`-[no]center` (no)

Center atoms in box

`-boxcenter` &lt;enum&gt; (tric)

Center for -pbc and -center: tric, rect, zero

`-box` &lt;vector&gt; (0 0 0)

Size for new cubic box (default: read from input)

`-trans` &lt;vector&gt; (0 0 0)

All coordinates will be translated by trans. This can advantageously be combined with -pbc mol -ur compact.

`-shift` &lt;vector&gt; (0 0 0)

All coordinates will be shifted by framenr*shift

`-fit` &lt;enum&gt; (none)

Fit molecule to ref structure in the structure file: none, rot+trans, rotxy+transxy, translation, transxy, progressive

`-ndec` &lt;int&gt; (3)

Number of decimal places to write to .xtc output

`-[no]vel` (yes)

Read and write velocities if possible

`-[no]force` (no)

Read and write forces if possible

`-trunc` &lt;time&gt; (-1)

Truncate input trajectory file after this time (ps)

`-exec` &lt;string&gt;

Execute command for every output frame with the frame number as argument

`-split` &lt;time&gt; (0)

Start writing new file when t MOD split = first time (ps)

`-[no]sep` (no)

Write each frame to a separate .gro, .g96 or .pdb file

`-nzero` &lt;int&gt; (0)

If the -sep flag is set, use these many digits for the file numbers and prepend zeros as needed

`-dropunder` &lt;real&gt; (0)

Drop all frames below this value

`-dropover` &lt;real&gt; (0)

Drop all frames above this value

`-[no]conect` (no)

Add CONECT PDB records when writing [.pdb](../reference-manual/file-formats.html#pdb) files. Useful for visualization of non-standard molecules, e.g. coarse grained ones. Can only be done when a topology (tpr) file is present
