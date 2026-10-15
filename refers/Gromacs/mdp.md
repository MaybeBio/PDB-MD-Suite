# Molecular dynamics parameters (.mdp options) - GROMACS 2026.4 documentation

# Molecular dynamics parameters (.mdp options)[¶](#molecular-dynamics-parameters-mdp-options)

## General information[¶](#general-information)

Default values are given in parentheses, or listed first among choices. The first option in the list is always the default option. Units are given in square brackets. The difference between a dash and an underscore is ignored.

A [sample mdp file](../reference-manual/file-formats.html#mdp) is available. This should be appropriate to start a normal simulation. Edit it to suit your specific needs and desires.

### Preprocessing[¶](#preprocessing)

include[¶](#mdp-include)

directories to include in your topology. Format: `-I/home/john/mylib-I../otherlib`

define[¶](#mdp-define)

defines to pass to the preprocessor, default is no defines. You can use any defines to control options in your customized topology files. Options that act on existing [top](../reference-manual/file-formats.html#top) file mechanisms include

> `-DFLEXIBLE` will use flexible water instead of rigid water into your topology, this can be useful for normal mode analysis.
> 
> `-DPOSRES` will trigger the inclusion of `posre.itp` into your topology, used for implementing position restraints.

### Run control[¶](#run-control)

integrator[¶](#mdp-integrator)

(Despite the name, this list includes algorithms that are not actually integrators over time. [`integrator=steep`](#mdp-value-integrator-steep) and all entries following it are in this category)

md[¶](#mdp-value-integrator-md)

A leap-frog algorithm for integrating Newton’s equations of motion.

md-vv[¶](#mdp-value-integrator-md-vv)

A velocity Verlet algorithm for integrating Newton’s equations of motion. For constant NVE simulations started from corresponding points in the same trajectory, the trajectories are analytically, but not binary, identical to the [`integrator=md`](#mdp-value-integrator-md) leap-frog integrator. The kinetic energy is determined from the whole step velocities and is therefore slightly too high. The advantage of this integrator is more accurate, reversible Nose-Hoover and Parrinello-Rahman coupling integration based on Trotter expansion, as well as (slightly too small) full step velocity output. This all comes at the cost of extra computation, especially with constraints and extra communication in parallel. Note that for nearly all production simulations the [`integrator=md`](#mdp-value-integrator-md) integrator is accurate enough.

md-vv-avek[¶](#mdp-value-integrator-md-vv-avek)

A velocity Verlet algorithm identical to [`integrator=md-vv`](#mdp-value-integrator-md-vv), except that the kinetic energy is determined as the average of the two half step kinetic energies as in the [`integrator=md`](#mdp-value-integrator-md) integrator, and this thus more accurate. With Nose-Hoover and/or Parrinello-Rahman coupling this comes with a slight increase in computational cost.

sd[¶](#mdp-value-integrator-sd)

An accurate and efficient leap-frog stochastic dynamics integrator. With constraints, coordinates needs to be constrained twice per integration step. Depending on the computational cost of the force calculation, this can take a significant part of the simulation time. The temperature for one or more groups of atoms ([`tc-grps`](#mdp-tc-grps)) is set with [`ref-t`](#mdp-ref-t), the inverse friction constant for each group is set with [`tau-t`](#mdp-tau-t). The parameters [`tcoupl`](#mdp-tcoupl) and [`nsttcouple`](#mdp-nsttcouple) are ignored. The random generator is initialized with [`ld-seed`](#mdp-ld-seed). When used as a thermostat, an appropriate value for [`tau-t`](#mdp-tau-t) is 2 ps, since this results in a friction that is lower than the internal friction of water, while it is high enough to remove excess heat NOTE: temperature deviations decay twice as fast as with a Berendsen thermostat with the same [`tau-t`](#mdp-tau-t).

bd[¶](#mdp-value-integrator-bd)

An Euler integrator for Brownian or position Langevin dynamics. The velocity is the force divided by a friction coefficient ([`bd-fric`](#mdp-bd-fric)) plus random thermal noise ([`ref-t`](#mdp-ref-t)). When [`bd-fric`](#mdp-bd-fric) is 0, the friction coefficient for each particle is calculated as mass/ [`tau-t`](#mdp-tau-t), as for the integrator [`integrator=sd`](#mdp-value-integrator-sd). The random generator is initialized with [`ld-seed`](#mdp-ld-seed).

steep[¶](#mdp-value-integrator-steep)

A steepest descent algorithm for energy minimization. The maximum step size is [`emstep`](#mdp-emstep), the tolerance is [`emtol`](#mdp-emtol).

cg[¶](#mdp-value-integrator-cg)

A conjugate gradient algorithm for energy minimization, the tolerance is [`emtol`](#mdp-emtol). CG is more efficient when a steepest descent step is done every once in a while, this is determined by [`nstcgsteep`](#mdp-nstcgsteep). For a minimization prior to a normal mode analysis, which requires a very high accuracy, GROMACS should be compiled in double precision.

l-bfgs[¶](#mdp-value-integrator-l-bfgs)

A quasi-Newtonian algorithm for energy minimization according to the low-memory Broyden-Fletcher-Goldfarb-Shanno approach. In practice this seems to converge faster than Conjugate Gradients, but due to the correction steps necessary it is not (yet) parallelized.

nm[¶](#mdp-value-integrator-nm)

Normal mode analysis is performed on the structure in the [tpr](../reference-manual/file-formats.html#tpr) file. GROMACS should be compiled in double precision.

tpi[¶](#mdp-value-integrator-tpi)

Test particle insertion. The last molecule in the topology is the test particle. A trajectory must be provided to `mdrun-rerun`. This trajectory should not contain the molecule to be inserted. Insertions are performed [`nsteps`](#mdp-nsteps) times in each frame at random locations and with random orientations of the molecule. When [`nstlist`](#mdp-nstlist) is larger than one, [`nstlist`](#mdp-nstlist) insertions are performed in a sphere with radius [`rtpi`](#mdp-rtpi) around a the same random location using the same pair list. Since pair list construction is expensive, one can perform several extra insertions with the same list almost for free. The random seed is set with [`ld-seed`](#mdp-ld-seed). The temperature for the Boltzmann weighting is set with [`ref-t`](#mdp-ref-t), this should match the temperature of the simulation of the original trajectory. Dispersion correction is implemented correctly for TPI. All relevant quantities are written to the file specified with `mdrun-tpi`. The distribution of insertion energies is written to the file specified with `mdrun-tpid`. No trajectory or energy file is written. Parallel TPI gives identical results to single-node TPI. For charged molecules, using PME with a fine grid is most accurate and also efficient, since the potential in the system only needs to be calculated once per frame.

tpic[¶](#mdp-value-integrator-tpic)

Test particle insertion into a predefined cavity location. The procedure is the same as for [`integrator=tpi`](#mdp-value-integrator-tpi), except that one coordinate extra is read from the trajectory, which is used as the insertion location. The molecule to be inserted should be centered at 0,0,0. GROMACS does not do this for you, since for different situations a different way of centering might be optimal. Also [`rtpi`](#mdp-rtpi) sets the radius for the sphere around this location. Neighbor searching is done only once per frame, [`nstlist`](#mdp-nstlist) is not used. Parallel [`integrator=tpic`](#mdp-value-integrator-tpic) gives identical results to single-rank [`integrator=tpic`](#mdp-value-integrator-tpic).

mimic[¶](#mdp-value-integrator-mimic)

Enable MiMiC QM/MM coupling to run hybrid molecular dynamics. Keey in mind that its required to launch CPMD compiled with MiMiC as well. In this mode all options regarding integration (T-coupling, P-coupling, timestep and number of steps) are ignored as CPMD will do the integration instead. Options related to forces computation (cutoffs, PME parameters, etc.) are working as usual. Atom selection to define QM atoms is read from [`QMMM-grps`](#mdp-QMMM-grps)

tinit[¶](#mdp-tinit)

(0) [ps] starting time for your run (only makes sense for time-based integrators)

dt[¶](#mdp-dt)

(0.001) [ps] time step for integration (only makes sense for time-based integrators)

nsteps[¶](#mdp-nsteps)

(0) maximum number of steps to integrate or minimize, -1 is no maximum

init-step[¶](#mdp-init-step)

(0) The starting step. The time at step i in a run is calculated as: t = [`tinit`](#mdp-tinit) + [`dt`](#mdp-dt) * ([`init-step`](#mdp-init-step) + i). The free-energy lambda is calculated as: lambda = [`init-lambda`](#mdp-init-lambda) + [`delta-lambda`](#mdp-delta-lambda) * ([`init-step`](#mdp-init-step) + i). Also non-equilibrium MD parameters can depend on the step number. Thus for exact restarts or redoing part of a run it might be necessary to set [`init-step`](#mdp-init-step) to the step number of the restart frame. [gmx convert-tpr](../onlinehelp/gmx-convert-tpr.html#gmx-convert-tpr) does this automatically.

simulation-part[¶](#mdp-simulation-part)

(0) A simulation can consist of multiple parts, each of which has a part number. This option specifies what that number will be, which helps keep track of parts that are logically the same simulation. This option is generally useful to set only when coping with a crashed simulation where files were lost.

mts[¶](#mdp-mts)no[¶](#mdp-value-mts-no)

Evaluate all forces at every integration step.

yes[¶](#mdp-value-mts-yes)

Use a multiple timing-stepping integrator to evaluate some forces, as specified by [`mts-level2-forces`](#mdp-mts-level2-forces) every [`mts-level2-factor`](#mdp-mts-level2-factor) integration steps. All other forces are evaluated at every step. MTS is currently only supported with [`integrator=md`](#mdp-value-integrator-md).

mts-levels[¶](#mdp-mts-levels)

(2) The number of levels for the multiple time-stepping scheme. Currently only 2 is supported.

mts-level2-forces[¶](#mdp-mts-level2-forces)

(longrange-nonbonded) A list of one or more force groups that will be evaluated only every [`mts-level2-factor`](#mdp-mts-level2-factor) steps. Supported entries are: `longrange-nonbonded`, `nonbonded`, `pair`, `dihedral`, `angle`, `pull` and `awh`. With `pair` the listed pair forces (such as 1-4) are selected. With `dihedral` all dihedrals are selected, including cmap. All other forces, including all restraints, are evaluated and integrated every step. When PME or Ewald is used for electrostatics and/or LJ interactions, `longrange-nonbonded` can not be omitted here.

mts-level2-factor[¶](#mdp-mts-level2-factor)

(2) [steps] Interval for computing the forces in level 2 of the multiple time-stepping scheme

mass-repartition-factor[¶](#mdp-mass-repartition-factor)

(1) [] Scales the masses of the lightest atoms in the system by this factor to the mass mMin. All atoms with a mass lower than mMin also have their mass set to that mMin. The mass change is subtracted from the mass of the atom the light atom is bound to. If there is no bound atom a warning is generated. If there is more than one atom bound an error is generated. If the mass of the bound atom would become lower than mMin an error is generated. For typical atomistic systems only the masses of hydrogens are scaled. With [`constraints=h-bonds`](#mdp-value-constraints-h-bonds), a factor of 3 will usually enable a time step of 4 fs.

comm-mode[¶](#mdp-comm-mode)Linear[¶](#mdp-value-comm-mode-Linear)

Remove center of mass translational velocity

Angular[¶](#mdp-value-comm-mode-Angular)

Remove center of mass translational and rotational velocity

Linear-acceleration-correction[¶](#mdp-value-comm-mode-Linear-acceleration-correction)

Remove center of mass translational velocity. Correct the center of mass position assuming linear acceleration over [`nstcomm`](#mdp-nstcomm) steps. This is useful for cases where an acceleration is expected on the center of mass which is nearly constant over [`nstcomm`](#mdp-nstcomm) steps. This can occur for example when pulling on a group using an absolute reference.

None[¶](#mdp-value-comm-mode-None)

No restriction on the center of mass motion

nstcomm[¶](#mdp-nstcomm)

(100) [steps] interval for center of mass motion removal

comm-grps[¶](#mdp-comm-grps)

group(s) for center of mass motion removal, default is the whole system

### Langevin dynamics[¶](#langevin-dynamics)

bd-fric[¶](#mdp-bd-fric)

(0) [amu ps<sup>-1</sup>] Brownian dynamics friction coefficient. When [`bd-fric`](#mdp-bd-fric) is 0, the friction coefficient for each particle is calculated as mass/ [`tau-t`](#mdp-tau-t).

ld-seed[¶](#mdp-ld-seed)

(-1) [integer] used to initialize random generator for thermal noise for stochastic and Brownian dynamics. When [`ld-seed`](#mdp-ld-seed) is set to -1, a pseudo random seed is used. When running BD or SD on multiple processors, each processor uses a seed equal to [`ld-seed`](#mdp-ld-seed) plus the processor number.

### Energy minimization[¶](#energy-minimization)

emtol[¶](#mdp-emtol)

(10.0) [kJ mol<sup>-1</sup> nm<sup>-1</sup>] the minimization is converged when the maximum force is smaller than this value

emstep[¶](#mdp-emstep)

(0.01) [nm] initial step-size

nstcgsteep[¶](#mdp-nstcgsteep)

(1000) [steps] interval of performing 1 steepest descent step while doing conjugate gradient energy minimization.

nbfgscorr[¶](#mdp-nbfgscorr)

(10) Number of correction steps to use for L-BFGS minimization. A higher number is (at least theoretically) more accurate, but slower.

### Shell Molecular Dynamics[¶](#shell-molecular-dynamics)

When shells or flexible constraints are present in the system the positions of the shells and the lengths of the flexible constraints are optimized at every time step until either the RMS force on the shells and constraints is less than [`emtol`](#mdp-emtol), or a maximum number of iterations [`niter`](#mdp-niter) has been reached. Minimization is converged when the maximum force is smaller than [`emtol`](#mdp-emtol). For shell MD this value should be 1.0 at most.

niter[¶](#mdp-niter)

(20) maximum number of iterations for optimizing the shell positions and the flexible constraints.

fcstep[¶](#mdp-fcstep)

(0) [ps<sup>2</sup>] the step size for optimizing the flexible constraints. Should be chosen as mu/(d2V/dq2) where mu is the reduced mass of two particles in a flexible constraint and d2V/dq2 is the second derivative of the potential in the constraint direction. Hopefully this number does not differ too much between the flexible constraints, as the number of iterations and thus the runtime is very sensitive to fcstep. Try several values!

### Test particle insertion[¶](#test-particle-insertion)

rtpi[¶](#mdp-rtpi)

(0.05) [nm] the test particle insertion radius, see integrators [`integrator=tpi`](#mdp-value-integrator-tpi) and [`integrator=tpic`](#mdp-value-integrator-tpic)

### Output control[¶](#output-control)

nstxout[¶](#mdp-nstxout)

(0) [steps] number of steps that elapse between writing coordinates to the output trajectory file ([trr](../reference-manual/file-formats.html#trr)), the first and last coordinates are always written unless 0, which means coordinates are not written into the trajectory file.

nstvout[¶](#mdp-nstvout)

(0) [steps] number of steps that elapse between writing velocities to the output trajectory file ([trr](../reference-manual/file-formats.html#trr)), the first and last velocities are always written unless 0, which means velocities are not written into the trajectory file.

nstfout[¶](#mdp-nstfout)

(0) [steps] number of steps that elapse between writing forces to the output trajectory file ([trr](../reference-manual/file-formats.html#trr)), the first and last forces are always written, unless 0, which means forces are not written into the trajectory file.

nstlog[¶](#mdp-nstlog)

(1000) [steps] number of steps that elapse between writing energies to the log file, the first and last energies are always written.

nstcalcenergy[¶](#mdp-nstcalcenergy)

(100) number of steps that elapse between calculating the energies, 0 is never. This option is only relevant with dynamics. This option affects the performance in parallel simulations, because calculating energies requires global communication between all processes which can become a bottleneck at high parallelization.

nstenergy[¶](#mdp-nstenergy)

(1000) [steps] number of steps that elapse between writing energies to the energy file ([edr](../reference-manual/file-formats.html#edr)), the first and last energies are always written, should be a multiple of [`nstcalcenergy`](#mdp-nstcalcenergy). Note that the exact sums and fluctuations over all MD steps modulo [`nstcalcenergy`](#mdp-nstcalcenergy) are stored in the energy file, so [gmx energy](../onlinehelp/gmx-energy.html#gmx-energy) can report exact energy averages and fluctuations also when [`nstenergy`](#mdp-nstenergy) &gt; 1

nstxout-compressed[¶](#mdp-nstxout-compressed)

(0) [steps] number of steps that elapse between writing position coordinates using lossy compression ([xtc](../reference-manual/file-formats.html#xtc) file), the first and last coordinates are always written, unless 0, which means that there is no compressed coordinates output.

compressed-x-precision[¶](#mdp-compressed-x-precision)

(1000) [real] precision with which to write to the compressed trajectory file

compressed-x-grps[¶](#mdp-compressed-x-grps)

group(s) to write to the compressed trajectory file, by default the whole system is written (if [`nstxout-compressed`](#mdp-nstxout-compressed) &gt; 0)

energygrps[¶](#mdp-energygrps)

group(s) for which to write to write short-ranged non-bonded potential energies to the energy file (not supported on GPUs)

### Neighbor searching[¶](#neighbor-searching)

cutoff-scheme[¶](#mdp-cutoff-scheme)Verlet[¶](#mdp-value-cutoff-scheme-Verlet)

Generate a pair list with buffering. The buffer size is automatically set based on [`verlet-buffer-tolerance`](#mdp-verlet-buffer-tolerance), unless this is set to -1, in which case [`rlist`](#mdp-rlist) will be used.

group[¶](#mdp-value-cutoff-scheme-group)

Generate a pair list for groups of atoms, corresponding to the charge groups in the topology. This option is no longer supported.

nstlist[¶](#mdp-nstlist)

1. [steps]

&gt;0[¶](#mdp-value-nstlist-0)

Interval between steps that update the neighbor list. When dynamics and [`verlet-buffer-tolerance`](#mdp-verlet-buffer-tolerance) set, [`nstlist`](#mdp-nstlist) is actually a minimum value and [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) might increase it, unless it is set to 1. With parallel simulations and/or non-bonded force calculation on the GPU, a value of 20 or 40 often gives the best performance. With energy minimization this parameter is not used as the pair list is updated when at least one atom has moved by more than half the pair list buffer size.

0[¶](#mdp-value-0)

The neighbor list is only constructed once and never updated. This is mainly useful for vacuum simulations in which all particles see each other. But vacuum simulations are (temporarily) not supported.

&lt;0[¶](#mdp-value-1)

Unused.

pbc[¶](#mdp-pbc)xyz[¶](#mdp-value-pbc-xyz)

Use periodic boundary conditions in all directions.

no[¶](#mdp-value-pbc-no)

Use no periodic boundary conditions, ignore the box. To simulate without cut-offs, set all cut-offs and [`nstlist`](#mdp-nstlist) to 0. For best performance without cut-offs on a single MPI rank, set [`nstlist`](#mdp-nstlist) to zero.

xy[¶](#mdp-value-pbc-xy)

Use periodic boundary conditions in x and y directions only. This can be used in combination with [walls](#walls). Without walls or with only one wall the system size is infinite in the z direction. Therefore pressure coupling or Ewald summation methods can not be used. These disadvantages do not apply when two walls are used.

periodic-molecules[¶](#mdp-periodic-molecules)no[¶](#mdp-value-periodic-molecules-no)

molecules are finite, fast molecular PBC can be used

yes[¶](#mdp-value-periodic-molecules-yes)

for systems with molecules that couple to themselves through the periodic boundary conditions, this requires a slower PBC algorithm and molecules are not made whole in the output

verlet-buffer-tolerance[¶](#mdp-verlet-buffer-tolerance)

(0.005) [kJ mol<sup>-1</sup> ps<sup>-1</sup>]

Used when performing a simulation with dynamics. This sets the maximum allowed error for pair interactions per particle caused by the Verlet buffer, which indirectly sets [`rlist`](#mdp-rlist). As both [`nstlist`](#mdp-nstlist) and the Verlet buffer size are fixed (for performance reasons), particle pairs not in the pair list can occasionally get within the cut-off distance during [`nstlist`](#mdp-nstlist) -1 steps. This causes very small jumps in the energy. In a constant-temperature ensemble, these very small energy jumps can be estimated for a given cut-off and [`rlist`](#mdp-rlist). The estimate assumes a homogeneous particle distribution, hence the errors might be slightly underestimated for multi-phase systems. (See the [reference manual](../manual-2026.4.pdf) for details). For longer pair-list life-time ([`nstlist`](#mdp-nstlist) -1) * [`dt`](#mdp-dt) the buffer is overestimated, because the interactions between particles are ignored. Combined with cancellation of errors, the actual drift of the total energy is usually one to two orders of magnitude smaller. Note that the generated buffer size takes into account that the GROMACS pair-list setup leads to a reduction in the drift by a factor 10, compared to a simple particle-pair based list. Without dynamics (energy minimization etc.), the buffer is 5% of the cut-off. For NVE simulations the initial temperature is used, unless this is zero, in which case a buffer of 10% is used. For NVE simulations the tolerance usually needs to be lowered to achieve proper energy conservation on the nanosecond time scale. To override the automated buffer setting, use [`verlet-buffer-tolerance`](#mdp-verlet-buffer-tolerance) =-1 and set [`rlist`](#mdp-rlist) manually.

verlet-buffer-pressure-tolerance[¶](#mdp-verlet-buffer-pressure-tolerance)

(0.5) [bar]

Used when performing a simulation with dynamics and only active when [`verlet-buffer-tolerance`](#mdp-verlet-buffer-tolerance) is positive. This sets the maximum tolerated error in the average pressure due to missing Lennard-Jones interactions of particle pairs that are not in the pair list, but come within [`rvdw`](#mdp-rvdw) range as the pair list ages. As for the drift tolerance, the (over)estimate of the pressure error is tight at short times. At longer time it turns into a significant overestimate, because interactions limit the displacement of particles. Note that the default tolerance of 0.5 bar corresponds to a maximum relative deviation of the density of liquid water of 2e-5.

rlist[¶](#mdp-rlist)

(1) [nm] Cut-off distance for the short-range neighbor list. With dynamics, this is by default set by the [`verlet-buffer-tolerance`](#mdp-verlet-buffer-tolerance) and [`verlet-buffer-pressure-tolerance`](#mdp-verlet-buffer-pressure-tolerance) options and the value of [`rlist`](#mdp-rlist) is ignored. Without dynamics, this is by default set to the maximum cut-off plus 5% buffer, except for test particle insertion, where the buffer is managed exactly and automatically. For NVE simulations, where the automated setting is not possible, the advised procedure is to run [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) with an NVT setup with the expected temperature and copy the resulting value of [`rlist`](#mdp-rlist) to the NVE setup.

### Electrostatics[¶](#electrostatics)

coulombtype[¶](#mdp-coulombtype)Cut-off[¶](#mdp-value-coulombtype-Cut-off)

Plain cut-off with pair list radius [`rlist`](#mdp-rlist) and Coulomb cut-off [`rcoulomb`](#mdp-rcoulomb), where [`rlist`](#mdp-rlist) &gt;= [`rcoulomb`](#mdp-rcoulomb). Note that with the (default) setting of [`coulomb-modifier`](#mdp-coulomb-modifier) =Potential-shift not only the potentials between interacting pairs are shifted to be zero at the cut-off, but the same shift is also applied to excluded pairs. This does not lead to forces between excluded pairs, but does add a constant offset to the total Coulomb potential.

Ewald[¶](#mdp-value-coulombtype-Ewald)

Classical Ewald sum electrostatics. The real-space cut-off [`rcoulomb`](#mdp-rcoulomb) should be equal to [`rlist`](#mdp-rlist). Use *e.g.*[`rlist`](#mdp-rlist) =0.9, [`rcoulomb`](#mdp-rcoulomb) =0.9. The highest magnitude of wave vectors used in reciprocal space is controlled by [`fourierspacing`](#mdp-fourierspacing). The relative accuracy of direct/reciprocal space is controlled by [`ewald-rtol`](#mdp-ewald-rtol).

NOTE: Ewald scales as O(N<sup>3/2</sup>) and is thus extremely slow for large systems. It is included mainly for reference - in most cases PME will perform much better.

PME[¶](#mdp-value-coulombtype-PME)

Fast smooth Particle-Mesh Ewald (SPME) electrostatics. Direct space is similar to the Ewald sum, while the reciprocal part is performed with FFTs. Grid dimensions are controlled with [`fourierspacing`](#mdp-fourierspacing) and the interpolation order with [`pme-order`](#mdp-pme-order). With a grid spacing of 0.1 nm and cubic interpolation the electrostatic forces have an accuracy of 2-3*10<sup>-4</sup>. Since the error from the vdw-cutoff is larger than this you might try 0.15 nm. When running in parallel the interpolation parallelizes better than the FFT, so try decreasing grid dimensions while increasing interpolation.

P3M-AD[¶](#mdp-value-coulombtype-P3M-AD)

Particle-Particle Particle-Mesh algorithm with analytical derivative for for long-range electrostatic interactions. The method and code is identical to SPME, except that the influence function is optimized for the grid. This gives a slight increase in accuracy.

Reaction-Field[¶](#mdp-value-coulombtype-Reaction-Field)

Reaction field electrostatics with Coulomb cut-off [`rcoulomb`](#mdp-rcoulomb), where [`rlist`](#mdp-rlist) &gt;= [`rvdw`](#mdp-rvdw). The dielectric constant beyond the cut-off is [`epsilon-rf`](#mdp-epsilon-rf). The dielectric constant can be set to infinity by setting [`epsilon-rf`](#mdp-epsilon-rf) =0.

User[¶](#mdp-value-coulombtype-User)

Currently unsupported. [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) will now expect to find a file `table.xvg` with user-defined potential functions for repulsion, dispersion and Coulomb. When pair interactions are present, [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) also expects to find a file `tablep.xvg` for the pair interactions. When the same interactions should be used for non-bonded and pair interactions the user can specify the same file name for both table files. These files should contain 7 columns: the `x` value, `f(x)`, `-f'(x)`, `g(x)`, `-g'(x)`, `h(x)`, `-h'(x)`, where `f(x)` is the Coulomb function, `g(x)` the dispersion function and `h(x)` the repulsion function. When [`vdwtype`](#mdp-vdwtype) is not set to User the values for `g`, `-g'`, `h` and `-h'` are ignored. For the non-bonded interactions `x` values should run from 0 to the largest cut-off distance + [`table-extension`](#mdp-table-extension) and should be uniformly spaced. For the pair interactions the table length in the file will be used. The optimal spacing, which is used for non-user tables, is `0.002nm` when you run in mixed precision or `0.0005nm` when you run in double precision. The function value at `x=0` is not important. More information is in the printed manual.

PME-Switch[¶](#mdp-value-coulombtype-PME-Switch)

Currently unsupported. A combination of PME and a switch function for the direct-space part (see above). [`rcoulomb`](#mdp-rcoulomb) is allowed to be smaller than [`rlist`](#mdp-rlist).

PME-User[¶](#mdp-value-coulombtype-PME-User)

Currently unsupported. A combination of PME and user tables (see above). [`rcoulomb`](#mdp-rcoulomb) is allowed to be smaller than [`rlist`](#mdp-rlist). The PME mesh contribution is subtracted from the user table by [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun). Because of this subtraction the user tables should contain about 10 decimal places.

PME-User-Switch[¶](#mdp-value-coulombtype-PME-User-Switch)

Currently unsupported. A combination of PME-User and a switching function (see above). The switching function is applied to final particle-particle interaction, *i.e.* both to the user supplied function and the PME Mesh correction part.

coulomb-modifier[¶](#mdp-coulomb-modifier)Potential-shift[¶](#mdp-value-coulomb-modifier-Potential-shift)

Shift the Coulomb potential by a constant such that it is zero at the cut-off. This makes the potential the integral of the force. Note that this does not affect the forces or the sampling.

None[¶](#mdp-value-coulomb-modifier-None)

Use an unmodified Coulomb potential. This can be useful when comparing energies with those computed with other software.

rcoulomb-switch[¶](#mdp-rcoulomb-switch)

(0) [nm] where to start switching the Coulomb potential, only relevant when force or potential switching is used

rcoulomb[¶](#mdp-rcoulomb)

(1) [nm] The distance for the Coulomb cut-off. Note that with PME this value can be increased by the PME tuning in [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) along with the PME grid spacing.

epsilon-r[¶](#mdp-epsilon-r)

(1) The relative dielectric constant. A value of 0 means infinity.

epsilon-rf[¶](#mdp-epsilon-rf)

(0) The relative dielectric constant of the reaction field. This is only used with reaction-field electrostatics. A value of 0 means infinity.

### Van der Waals[¶](#van-der-waals)

vdwtype[¶](#mdp-vdwtype)Cut-off[¶](#mdp-value-vdwtype-Cut-off)

Plain cut-off with pair list radius [`rlist`](#mdp-rlist) and VdW cut-off [`rvdw`](#mdp-rvdw), where [`rlist`](#mdp-rlist) &gt;= [`rvdw`](#mdp-rvdw).

PME[¶](#mdp-value-vdwtype-PME)

Fast smooth Particle-mesh Ewald (SPME) for VdW interactions. The grid dimensions are controlled with [`fourierspacing`](#mdp-fourierspacing) in the same way as for electrostatics, and the interpolation order is controlled with [`pme-order`](#mdp-pme-order). The relative accuracy of direct/reciprocal space is controlled by [`ewald-rtol-lj`](#mdp-ewald-rtol-lj), and the specific combination rules that are to be used by the reciprocal routine are set using [`lj-pme-comb-rule`](#mdp-lj-pme-comb-rule).

Shift[¶](#mdp-value-vdwtype-Shift)

This functionality is deprecated and replaced by using [`vdwtype=Cut-off`](#mdp-value-vdwtype-Cut-off) with [`vdw-modifier=Force-switch`](#mdp-value-vdw-modifier-Force-switch). The LJ (not Buckingham) potential is decreased over the whole range and the forces decay smoothly to zero between [`rvdw-switch`](#mdp-rvdw-switch) and [`rvdw`](#mdp-rvdw).

Switch[¶](#mdp-value-vdwtype-Switch)

This functionality is deprecated and replaced by using [`vdwtype=Cut-off`](#mdp-value-vdwtype-Cut-off) with [`vdw-modifier=Potential-switch`](#mdp-value-vdw-modifier-Potential-switch). The LJ (not Buckingham) potential is normal out to [`rvdw-switch`](#mdp-rvdw-switch), after which it is switched off to reach zero at [`rvdw`](#mdp-rvdw). Both the potential and force functions are continuously smooth, but be aware that all switch functions will give rise to a bulge (increase) in the force (since we are switching the potential).

User[¶](#mdp-value-vdwtype-User)

Currently unsupported. See [`coulombtype=User`](#mdp-value-coulombtype-User) for instructions. The function value at zero is not important. When you want to use LJ correction, make sure that [`rvdw`](#mdp-rvdw) corresponds to the cut-off in the user-defined function. When [`coulombtype`](#mdp-coulombtype) is not set to User the values for the `f` and `-f'` columns are ignored.

vdw-modifier[¶](#mdp-vdw-modifier)Potential-shift[¶](#mdp-value-vdw-modifier-Potential-shift)

Shift the Van der Waals potential by a constant such that it is zero at the cut-off. This makes the potential the integral of the force. Note that this does not affect the forces or the sampling.

None[¶](#mdp-value-vdw-modifier-None)

Use an unmodified Van der Waals potential. This can be useful when comparing energies with those computed with other software.

Force-switch[¶](#mdp-value-vdw-modifier-Force-switch)

Smoothly switches the forces to zero between [`rvdw-switch`](#mdp-rvdw-switch) and [`rvdw`](#mdp-rvdw). This shifts the potential shift over the whole range and switches it to zero at the cut-off. Note that this is more expensive to calculate than a plain cut-off and it is not required for energy conservation, since Potential-shift conserves energy just as well.

Potential-switch[¶](#mdp-value-vdw-modifier-Potential-switch)

Smoothly switches the potential to zero between [`rvdw-switch`](#mdp-rvdw-switch) and [`rvdw`](#mdp-rvdw). Note that this introduces articifically large forces in the switching region and is much more expensive to calculate. This option should only be used if the force field you are using requires this.

rvdw-switch[¶](#mdp-rvdw-switch)

(0) [nm] where to start switching the LJ force and possibly the potential, only relevant when force or potential switching is used

rvdw[¶](#mdp-rvdw)

(1) [nm] distance for the LJ or Buckingham cut-off

DispCorr[¶](#mdp-DispCorr)no[¶](#mdp-value-DispCorr-no)

do not apply any correction

EnerPres[¶](#mdp-value-DispCorr-EnerPres)

apply long-range dispersion corrections for Energy and Pressure

Ener[¶](#mdp-value-DispCorr-Ener)

apply long-range dispersion corrections for Energy only

### Tables[¶](#tables)

table-extension[¶](#mdp-table-extension)

(1) [nm] Extension of the non-bonded potential lookup tables beyond the largest cut-off distance. With actual non-bonded interactions the tables are never accessed beyond the cut-off. But a longer table length might be needed for the 1-4 interactions, which are always tabulated irrespective of the use of tables for the non-bonded interactions.

energygrp-table[¶](#mdp-energygrp-table)

Currently unsupported. When user tables are used for electrostatics and/or VdW, here one can give pairs of energy groups for which separate user tables should be used. The two energy groups will be appended to the table file name, in order of their definition in [`energygrps`](#mdp-energygrps), separated by underscores. For example, if `energygrps=NaClSol` and `energygrp-table=NaNaNaCl`, [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) will read `table_Na_Na.xvg` and `table_Na_Cl.xvg` in addition to the normal `table.xvg` which will be used for all other energy group pairs.

### Ewald[¶](#ewald)

fourierspacing[¶](#mdp-fourierspacing)

(0.12) [nm] For ordinary Ewald, the ratio of the box dimensions and the spacing determines a lower bound for the number of wave vectors to use in each (signed) direction. For PME and P3M, that ratio determines a lower bound for the number of Fourier-space grid points that will be used along that axis. In all cases, the number for each direction can be overridden by entering a non-zero value for that [`fourier-nx`](#mdp-fourier-nx) direction. For optimizing the relative load of the particle-particle interactions and the mesh part of PME, it is useful to know that the accuracy of the electrostatics remains nearly constant when the Coulomb cut-off and the PME grid spacing are scaled by the same factor. Note that this spacing can be scaled up along with [`rcoulomb`](#mdp-rcoulomb) by the PME tuning in [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun).

fourier-nx[¶](#mdp-fourier-nx)fourier-ny[¶](#mdp-fourier-ny)fourier-nz[¶](#mdp-fourier-nz)

(0) Highest magnitude of wave vectors in reciprocal space when using Ewald. Grid size when using PME or P3M. These values override [`fourierspacing`](#mdp-fourierspacing) per direction. The best choice is powers of 2, 3, 5 and 7. Avoid large primes. Note that these grid sizes can be reduced along with scaling up [`rcoulomb`](#mdp-rcoulomb) by the PME tuning in [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun).

pme-order[¶](#mdp-pme-order)

(4) The number of grid points along a dimension to which a charge is mapped. The actual order of the PME interpolation is one less, e.g. the default of 4 gives cubic interpolation. Supported values are 3 to 12 (max 8 for P3M-AD). When running in parallel, it can be worth to switch to 5 and simultaneously increase the grid spacing. Note that on the CPU only values 4 and 5 have SIMD acceleration and GPUs only support the value 4.

ewald-rtol[¶](#mdp-ewald-rtol)

(10<sup>-5</sup>) The relative strength of the Ewald-shifted direct potential at [`rcoulomb`](#mdp-rcoulomb) is given by [`ewald-rtol`](#mdp-ewald-rtol). Decreasing this will give a more accurate direct sum, but then you need more wave vectors for the reciprocal sum.

ewald-rtol-lj[¶](#mdp-ewald-rtol-lj)

(10<sup>-3</sup>) When doing PME for VdW-interactions, [`ewald-rtol-lj`](#mdp-ewald-rtol-lj) is used to control the relative strength of the dispersion potential at [`rvdw`](#mdp-rvdw) in the same way as [`ewald-rtol`](#mdp-ewald-rtol) controls the electrostatic potential.

lj-pme-comb-rule[¶](#mdp-lj-pme-comb-rule)

(Geometric) The combination rules used to combine VdW-parameters in the reciprocal part of LJ-PME. Geometric rules are much faster than Lorentz-Berthelot and usually the recommended choice, even when the rest of the force field uses the Lorentz-Berthelot rules.

Geometric[¶](#mdp-value-lj-pme-comb-rule-Geometric)

Apply geometric combination rules

Lorentz-Berthelot[¶](#mdp-value-lj-pme-comb-rule-Lorentz-Berthelot)

Apply Lorentz-Berthelot combination rules

ewald-geometry[¶](#mdp-ewald-geometry)3d[¶](#mdp-value-ewald-geometry-3d)

The Ewald sum is performed in all three dimensions.

3dc[¶](#mdp-value-ewald-geometry-3dc)

The reciprocal sum is still performed in 3D, but a force and potential correction applied in the `z` dimension to produce a pseudo-2D summation. If your system has a slab geometry in the `x-y` plane you can try to increase the `z`-dimension of the box (a box height of 3 times the slab height is usually ok) and use this option.

epsilon-surface[¶](#mdp-epsilon-surface)

(0) This controls the dipole correction to the Ewald summation in 3D. The default value of zero means it is turned off. Turn it on by setting it to the value of the relative permittivity of the imaginary surface around your infinite system. Be careful - you should not use this if you have free mobile charges in your system. This value does not affect the slab 3DC variant of the long-range corrections.

### Temperature coupling[¶](#temperature-coupling)

ensemble-temperature-setting[¶](#mdp-ensemble-temperature-setting)auto[¶](#mdp-value-ensemble-temperature-setting-auto)

With this setting [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) will determine which of the next three settings is available and choose the appropriate one. When all atoms are coupled to a temperature bath with the same temperature, a constant ensemble temperature is chosen and the value is taken from the temperature bath.

constant[¶](#mdp-value-ensemble-temperature-setting-constant)

The system has a constant ensemble temperature given by [`ensemble-temperature`](#mdp-ensemble-temperature). A constant ensemble temperature is required for certain sampling algorithms such as AWH.

variable[¶](#mdp-value-ensemble-temperature-setting-variable)

The system has a variable ensemble temperature due to simulated annealing or simulated tempering. The system ensemble temperature is set dynamically during the simulation.

not-available[¶](#mdp-value-ensemble-temperature-setting-not-available)

The system has no ensemble temperature.

ensemble-temperature[¶](#mdp-ensemble-temperature)

(-1) [K]

The ensemble temperature for the system. The input value is only used with `ensemble-temperature-setting=constant`. By default the ensemble temperature is copied from the temperature of the thermal bath (when used).

tcoupl[¶](#mdp-tcoupl)no[¶](#mdp-value-tcoupl-no)

No temperature coupling.

berendsen[¶](#mdp-value-tcoupl-berendsen)

Temperature coupling with a Berendsen thermostat to a bath with temperature [`ref-t`](#mdp-ref-t), with time constant [`tau-t`](#mdp-tau-t). Several groups can be coupled separately, these are specified in the [`tc-grps`](#mdp-tc-grps) field separated by spaces. This is a historical thermostat needed to be able to reproduce previous simulations, but we strongly recommend not to use it for new production runs. Consult the manual for details.

nose-hoover[¶](#mdp-value-tcoupl-nose-hoover)

Temperature coupling using a Nose-Hoover extended ensemble. The reference temperature and coupling groups are selected as above, but in this case [`tau-t`](#mdp-tau-t) controls the period of the temperature fluctuations at equilibrium, which is slightly different from a relaxation time. For NVT simulations the conserved energy quantity is written to the energy and log files.

andersen[¶](#mdp-value-tcoupl-andersen)

Temperature coupling by randomizing a fraction of the particle velocities at each timestep. Reference temperature and coupling groups are selected as above. [`tau-t`](#mdp-tau-t) is the average time between randomization of each molecule. Inhibits particle dynamics somewhat, but has little or no ergodicity issues. Currently only implemented with velocity Verlet, and not implemented with constraints.

andersen-massive[¶](#mdp-value-tcoupl-andersen-massive)

Temperature coupling by randomizing velocities of all particles at infrequent timesteps. Reference temperature and coupling groups are selected as above. [`tau-t`](#mdp-tau-t) is the time between randomization of all molecules. Inhibits particle dynamics somewhat, but has little or no ergodicity issues. Currently only implemented with velocity Verlet.

v-rescale[¶](#mdp-value-tcoupl-v-rescale)

Temperature coupling using velocity rescaling with a stochastic term (JCP 126, 014101). This thermostat is similar to Berendsen coupling, with the same scaling using [`tau-t`](#mdp-tau-t), but the stochastic term ensures that a proper canonical ensemble is generated. The random seed is set with [`ld-seed`](#mdp-ld-seed). This thermostat works correctly even for [`tau-t`](#mdp-tau-t) =0. For NVT simulations the conserved energy quantity is written to the energy and log file.

nsttcouple[¶](#mdp-nsttcouple)

(-1) The interval between steps that couple the temperature. The default value of -1 sets [`nsttcouple`](#mdp-nsttcouple) equal to 100, or fewer steps if required for accurate integration (5 steps per tau for first order coupling, 20 steps per tau for second order coupling). Note that the default value is large in order to reduce the overhead of the additional computation and communication required for obtaining the kinetic energy. For velocity Verlet integrators [`nsttcouple`](#mdp-nsttcouple) is set to 1.

nh-chain-length[¶](#mdp-nh-chain-length)

(10) The number of chained Nose-Hoover thermostats for velocity Verlet integrators, the leap-frog [`integrator=md`](#mdp-value-integrator-md) integrator only supports 1. Data for the NH chain variables is not printed to the [edr](../reference-manual/file-formats.html#edr) file by default, but can be turned on with the [`print-nose-hoover-chain-variables`](#mdp-print-nose-hoover-chain-variables) option.

print-nose-hoover-chain-variables[¶](#mdp-print-nose-hoover-chain-variables)no[¶](#mdp-value-print-nose-hoover-chain-variables-no)

Do not store Nose-Hoover chain variables in the energy file.

yes[¶](#mdp-value-print-nose-hoover-chain-variables-yes)

Store all positions and velocities of the Nose-Hoover chain in the energy file.

tc-grps[¶](#mdp-tc-grps)

groups to couple to separate temperature baths

tau-t[¶](#mdp-tau-t)

[ps] time constant for coupling (one for each group in [`tc-grps`](#mdp-tc-grps)), -1 means no temperature coupling

ref-t[¶](#mdp-ref-t)

[K] reference temperature for coupling (one for each group in [`tc-grps`](#mdp-tc-grps))

### Pressure coupling[¶](#pressure-coupling)

pcoupl[¶](#mdp-pcoupl)no[¶](#mdp-value-pcoupl-no)

No pressure coupling. This means a fixed box size.

Berendsen[¶](#mdp-value-pcoupl-Berendsen)

Exponential relaxation pressure coupling with time constant [`tau-p`](#mdp-tau-p). The box is scaled every [`nstpcouple`](#mdp-nstpcouple) steps. This barostat does not yield a correct thermodynamic ensemble; it is only included to be able to reproduce previous runs, and we strongly recommend against using it for new simulations. See the manual for details.

C-rescale[¶](#mdp-value-pcoupl-C-rescale)

Exponential relaxation pressure coupling with time constant [`tau-p`](#mdp-tau-p), including a stochastic term to enforce correct volume fluctuations. The box is scaled every [`nstpcouple`](#mdp-nstpcouple) steps. It can be used for both equilibration and production.

Parrinello-Rahman[¶](#mdp-value-pcoupl-Parrinello-Rahman)

Extended-ensemble pressure coupling where the box vectors are subject to an equation of motion. The equation of motion for the atoms is coupled to this. No instantaneous scaling takes place. As for Nose-Hoover temperature coupling the time constant [`tau-p`](#mdp-tau-p) is the period of pressure fluctuations at equilibrium. This is a good method when you want to apply pressure scaling during data collection, but beware that you can get very large oscillations if you are starting from a different pressure. For simulations where the exact fluctations of the NPT ensemble are important, or if the pressure coupling time is very short, it may not be appropriate, as the previous time step pressure is used in some steps of the GROMACS implementation for the current time step pressure.

MTTK[¶](#mdp-value-pcoupl-MTTK)

Martyna-Tuckerman-Tobias-Klein implementation, only useable with [`integrator=md-vv`](#mdp-value-integrator-md-vv) or [`integrator=md-vv-avek`](#mdp-value-integrator-md-vv-avek), very similar to Parrinello-Rahman. As for Nose-Hoover temperature coupling the time constant [`tau-p`](#mdp-tau-p) is the period of pressure fluctuations at equilibrium. This is probably a better method when you want to apply pressure scaling during data collection, but beware that you can get very large oscillations if you are starting from a different pressure. This requires a constant ensemble temperature for the system. It only supports isotropic scaling, and only works without constraints. MTTK coupling is deprecated.

pcoupltype[¶](#mdp-pcoupltype)

Specifies the kind of isotropy of the pressure coupling used. Each kind takes one or more values for [`compressibility`](#mdp-compressibility) and [`ref-p`](#mdp-ref-p). Only a single value is permitted for [`tau-p`](#mdp-tau-p).

isotropic[¶](#mdp-value-pcoupltype-isotropic)

Isotropic pressure coupling with time constant [`tau-p`](#mdp-tau-p). One value each for [`compressibility`](#mdp-compressibility) and [`ref-p`](#mdp-ref-p) is required.

semiisotropic[¶](#mdp-value-pcoupltype-semiisotropic)

Pressure coupling which is isotropic in the `x` and `y` direction, but different in the `z` direction. This can be useful for membrane simulations. Two values each for [`compressibility`](#mdp-compressibility) and [`ref-p`](#mdp-ref-p) are required, for `x/y` and `z` directions respectively.

anisotropic[¶](#mdp-value-pcoupltype-anisotropic)

Same as before, but 6 values are needed for `xx`, `yy`, `zz`, `xy/yx`, `xz/zx` and `yz/zy` components, respectively. When the off-diagonal compressibilities are set to zero, a rectangular box will stay rectangular. Beware that anisotropic scaling can lead to extreme deformation of the simulation box.

surface-tension[¶](#mdp-value-pcoupltype-surface-tension)

Surface tension coupling for surfaces parallel to the xy-plane. Uses normal pressure coupling for the `z`-direction, while the surface tension is coupled to the `x/y` dimensions of the box. The first [`ref-p`](#mdp-ref-p) value is the reference surface tension times the number of surfaces `barnm`, the second value is the reference `z`-pressure `bar`. The two [`compressibility`](#mdp-compressibility) values are the compressibility in the `x/y` and `z` direction respectively. The value for the `z`-compressibility should be reasonably accurate since it influences the convergence of the surface-tension, it can also be set to zero to have a box with constant height.

nstpcouple[¶](#mdp-nstpcouple)

(-1) The interval between steps that couple the pressure. The default value of -1 sets [`nstpcouple`](#mdp-nstpcouple) equal to 100, or fewer steps if required for accurate integration (5 steps per tau for first order coupling, 20 steps per tau for second order coupling). Note that the default value is large in order to reduce the overhead of the additional computation and communication required for obtaining the virial and kinetic energy. For velocity Verlet integrators [`nsttcouple`](#mdp-nsttcouple) is set to 1.

tau-p[¶](#mdp-tau-p)

(5) [ps] The time constant for pressure coupling (one value for all directions).

compressibility[¶](#mdp-compressibility)

[bar<sup>-1</sup>] The compressibility (NOTE: this is now really in bar<sup>-1</sup>) For water at 1 atm and 300 K the compressibility is 4.5e-5 bar<sup>-1</sup>. The number of required values is implied by [`pcoupltype`](#mdp-pcoupltype).

ref-p[¶](#mdp-ref-p)

[bar] The reference pressure for coupling. The number of required values is implied by [`pcoupltype`](#mdp-pcoupltype).

refcoord-scaling[¶](#mdp-refcoord-scaling)no[¶](#mdp-value-refcoord-scaling-no)

The reference coordinates for position restraints are not modified. Note that with this option the virial and pressure might be ill defined, see [here](../reference-manual/functions/restraints.html#reference-manual-position-restraints) for more details.

all[¶](#mdp-value-refcoord-scaling-all)

The reference coordinates are scaled with the scaling matrix of the pressure coupling.

com[¶](#mdp-value-refcoord-scaling-com)

Scale the center of mass of the reference coordinates with the scaling matrix of the pressure coupling. The vectors of each reference coordinate to the center of mass are not scaled. Only one COM is used, even when there are multiple molecules with position restraints. For calculating the COM of the reference coordinates in the starting configuration, periodic boundary conditions are not taken into account. Note that with this option the virial and pressure might be ill defined, see [here](../reference-manual/functions/restraints.html#reference-manual-position-restraints) for more details.

### Simulated annealing[¶](#simulated-annealing)

Simulated annealing is controlled separately for each temperature group in GROMACS. The reference temperature is a piecewise linear function, but you can use an arbitrary number of points for each group, and choose either a single sequence or a periodic behaviour for each group. The actual annealing is performed by dynamically changing the reference temperature used in the thermostat algorithm selected, so remember that the system will usually not instantaneously reach the reference temperature!

annealing[¶](#mdp-annealing)

Type of annealing for each temperature group

no[¶](#mdp-value-annealing-no)

No simulated annealing - just couple to reference temperature value.

single[¶](#mdp-value-annealing-single)

A single sequence of annealing points. If your simulation is longer than the time of the last point, the temperature will be coupled to this constant value after the annealing sequence has reached the last time point.

periodic[¶](#mdp-value-annealing-periodic)

The annealing will start over at the first reference point once the last reference time is reached. This is repeated until the simulation ends.

annealing-npoints[¶](#mdp-annealing-npoints)

A list with the number of annealing reference/control points used for each temperature group. Use 0 for groups that are not annealed. The number of entries should equal the number of temperature groups.

annealing-time[¶](#mdp-annealing-time)

List of times at the annealing reference/control points for each group. If you are using periodic annealing, the times will be used modulo the last value, *i.e.* if the values are 0, 5, 10, and 15, the coupling will restart at the 0ps value after 15ps, 30ps, 45ps, etc. The number of entries should equal the sum of the numbers given in [`annealing-npoints`](#mdp-annealing-npoints).

annealing-temp[¶](#mdp-annealing-temp)

List of temperatures at the annealing reference/control points for each group. The number of entries should equal the sum of the numbers given in [`annealing-npoints`](#mdp-annealing-npoints).

Confused? OK, let’s use an example. Assume you have two temperature groups, set the group selections to `annealing=singleperiodic`, the number of points of each group to `annealing-npoints=34`, the times to `annealing-time=0360246` and finally temperatures to `annealing-temp=298280270298320320298`. The first group will be coupled to 298K at 0ps, but the reference temperature will drop linearly to reach 280K at 3ps, and then linearly between 280K and 270K from 3ps to 6ps. After this is stays constant, at 270K. The second group is coupled to 298K at 0ps, it increases linearly to 320K at 2ps, where it stays constant until 4ps. Between 4ps and 6ps it decreases to 298K, and then it starts over with the same pattern again, *i.e.* rising linearly from 298K to 320K between 6ps and 8ps. Check the summary printed by [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) if you are unsure!

### Velocity generation[¶](#velocity-generation)

gen-vel[¶](#mdp-gen-vel)no[¶](#mdp-value-gen-vel-no)

Do not generate velocities. The velocities are set to zero when there are no velocities in the input structure file.

yes[¶](#mdp-value-gen-vel-yes)

Generate velocities in [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) according to a Maxwell distribution at temperature [`gen-temp`](#mdp-gen-temp), with random seed [`gen-seed`](#mdp-gen-seed). This is only meaningful with [`integrator=md`](#mdp-value-integrator-md).

gen-temp[¶](#mdp-gen-temp)

(300) [K] temperature for Maxwell distribution

gen-seed[¶](#mdp-gen-seed)

(-1) [integer] used to initialize random generator for random velocities, when [`gen-seed`](#mdp-gen-seed) is set to -1, a pseudo random seed is used.

### Bonds[¶](#bonds)

constraints[¶](#mdp-constraints)

Controls which bonds in the topology will be converted to rigid holonomic constraints. Note that typical rigid water models do not have bonds, but rather a specialized `[settles]` directive, so are not affected by this keyword.

none[¶](#mdp-value-constraints-none)

No bonds converted to constraints.

h-bonds[¶](#mdp-value-constraints-h-bonds)

Convert the bonds with H-atoms to constraints.

all-bonds[¶](#mdp-value-constraints-all-bonds)

Convert all bonds to constraints. Note that many force fields have been parameterized with flexible bonds between heavy atoms and that constraining these bonds can increase energy barriers of dihedrals.

h-angles[¶](#mdp-value-constraints-h-angles)

Convert all bonds to constraints and convert the angles that involve H-atoms to bond-constraints. This option is deprecated.

all-angles[¶](#mdp-value-constraints-all-angles)

Convert all bonds to constraints and all angles to bond-constraints. This option is deprecated.

constraint-algorithm[¶](#mdp-constraint-algorithm)

Chooses which solver satisfies any non-SETTLE holonomic constraints.

LINCS[¶](#mdp-value-constraint-algorithm-LINCS)

LINear Constraint Solver. With domain decomposition the parallel version P-LINCS is used. The accuracy in set with [`lincs-order`](#mdp-lincs-order), which sets the number of matrices in the expansion for the matrix inversion. After the matrix inversion correction the algorithm does an iterative correction to compensate for lengthening due to rotation. The number of such iterations can be controlled with [`lincs-iter`](#mdp-lincs-iter). The root mean square relative constraint deviation is printed to the log file every [`nstlog`](#mdp-nstlog) steps. If a bond rotates more than [`lincs-warnangle`](#mdp-lincs-warnangle) in one step, a warning will be printed both to the log file and to `stderr`. LINCS should not be used with coupled angle constraints.

SHAKE[¶](#mdp-value-constraint-algorithm-SHAKE)

SHAKE is slightly slower and less stable than LINCS, but does work with angle constraints. The relative tolerance is set with [`shake-tol`](#mdp-shake-tol), 0.0001 is a good value for “normal” MD. SHAKE does not support constraints between atoms on different decomposition domains, so it can only be used with domain decomposition when so-called update-groups are used, which is usually the case when only bonds involving hydrogens are constrained. SHAKE can not be used with energy minimization.

continuation[¶](#mdp-continuation)

This option was formerly known as `unconstrained-start`.

no[¶](#mdp-value-continuation-no)

apply constraints to the start configuration and reset shells

yes[¶](#mdp-value-continuation-yes)

do not apply constraints to the start configuration and do not reset shells, useful for exact continuation and reruns

shake-tol[¶](#mdp-shake-tol)

(0.0001) relative tolerance for SHAKE

lincs-order[¶](#mdp-lincs-order)

(4) Highest order in the expansion of the constraint coupling matrix. When constraints form triangles, an additional expansion of the same order is applied on top of the normal expansion only for the couplings within such triangles. For “normal” MD simulations an order of 4 usually suffices, 6 is needed for large time-steps with virtual sites or BD. For accurate energy minimization in double precision an order of 8 or more might be required. Note that in single precision an order higher than 6 will often lead to worse accuracy due to amplification of rounding errors. With domain decomposition, the cell size is limited by the distance spanned by [`lincs-order`](#mdp-lincs-order) +1 constraints. When one wants to scale further than this limit, one can decrease [`lincs-order`](#mdp-lincs-order) and increase [`lincs-iter`](#mdp-lincs-iter), since the accuracy does not deteriorate when (1+ [`lincs-iter`](#mdp-lincs-iter) )* [`lincs-order`](#mdp-lincs-order) remains constant.

lincs-iter[¶](#mdp-lincs-iter)

(1) Number of iterations to correct for rotational lengthening in LINCS. For normal runs a single step is sufficient, but for NVE runs where you want to conserve energy accurately or for accurate energy minimization in double precision you might want to increase it to 2. Note that in single precision using more than 1 iteration will often lead to worse accuracy due to amplification of rounding errors.

lincs-warnangle[¶](#mdp-lincs-warnangle)

(30) [deg] maximum angle that a bond can rotate before LINCS will complain

morse[¶](#mdp-morse)no[¶](#mdp-value-morse-no)

bonds are represented by a harmonic potential

yes[¶](#mdp-value-morse-yes)

bonds are represented by a Morse potential

### Energy group exclusions[¶](#energy-group-exclusions)

energygrp-excl[¶](#mdp-energygrp-excl)

Exclusion between pairs of energy groups are currently not supported.

### Walls[¶](#walls)

nwall[¶](#mdp-nwall)

(0) When set to 1 there is a wall at `z=0`, when set to 2 there is also a wall at `z=z-box`. Walls can only be used with [`pbc`](#mdp-pbc)`=xy`. When set to 2, pressure coupling and Ewald summation can be used (it is usually best to use semiisotropic pressure coupling with the `x/y` compressibility set to 0, as otherwise the surface area will change). Walls interact wit the rest of the system through an optional [`wall-atomtype`](#mdp-wall-atomtype). Energy groups `wall0` and `wall1` (for [`nwall`](#mdp-nwall) =2) are added automatically to monitor the interaction of energy groups with each wall. The center of mass motion removal will be turned off in the `z`-direction.

wall-atomtype[¶](#mdp-wall-atomtype)

the atom type name in the force field for each wall. By (for example) defining a special wall atom type in the topology with its own combination rules, this allows for independent tuning of the interaction of each atomtype with the walls.

wall-type[¶](#mdp-wall-type)9-3[¶](#mdp-value-wall-type-9-3)

LJ integrated over the volume behind the wall: 9-3 potential

10-4[¶](#mdp-value-wall-type-10-4)

LJ integrated over the wall surface: 10-4 potential

12-6[¶](#mdp-value-wall-type-12-6)

direct LJ potential with the `z` distance from the wall

table[¶](#mdp-value-wall-type-table)

user-defined potentials indexed with the `z` distance from the wall, the tables are read analogously to the [`energygrp-table`](#mdp-energygrp-table) option, where the first name is for a “normal” energy group and the second name is `wall0` or `wall1`, only the dispersion and repulsion columns are used

wall-r-linpot[¶](#mdp-wall-r-linpot)

(-1) [nm] Below this distance from the wall the potential is continued linearly and thus the force is constant. Setting this option to a postive value is especially useful for equilibration when some atoms are beyond a wall. When the value is &lt;=0 (&lt;0 for [`wall-type`](#mdp-wall-type) =table), a fatal error is generated when atoms are beyond a wall.

wall-density[¶](#mdp-wall-density)

[nm<sup>-3</sup>] / [nm<sup>-2</sup>] the number density of the atoms for each wall for wall types 9-3 and 10-4

wall-ewald-zfac[¶](#mdp-wall-ewald-zfac)

(3) The scaling factor for the third box vector for Ewald summation only, the minimum is 2. Ewald summation can only be used with [`nwall`](#mdp-nwall) =2, where one should use [`ewald-geometry`](#mdp-ewald-geometry)`=3dc`. The empty layer in the box serves to decrease the unphysical Coulomb interaction between periodic images.

### COM pulling[¶](#com-pulling)

Sets whether pulling on collective variables is active. Note that where pulling coordinates are applicable, there can be more than one (set with [`pull-ncoords`](#mdp-pull-ncoords)) and multiple related [mdp](../reference-manual/file-formats.html#mdp) variables will exist accordingly. Documentation references to things like [`pull-coord1-vec`](#mdp-pull-coord1-vec) should be understood to apply to to the applicable pulling coordinate, eg. the second pull coordinate is described by pull-coord2-vec, pull-coord2-k, and so on.

pull[¶](#mdp-pull)no[¶](#mdp-value-pull-no)

No center of mass pulling. All the following pull options will be ignored (and if present in the [mdp](../reference-manual/file-formats.html#mdp) file, they unfortunately generate warnings)

yes[¶](#mdp-value-pull-yes)

Center of mass pulling will be applied on 1 or more groups using 1 or more pull coordinates.

pull-cylinder-r[¶](#mdp-pull-cylinder-r)

(1.5) [nm] the radius of the cylinder for [`pull-coord1-geometry=cylinder`](#mdp-value-pull-coord1-geometry-cylinder)

pull-constr-tol[¶](#mdp-pull-constr-tol)

(10<sup>-6</sup>) the relative constraint tolerance for constraint pulling

pull-print-com[¶](#mdp-pull-print-com)no[¶](#mdp-value-pull-print-com-no)

do not print the COM for any group

yes[¶](#mdp-value-pull-print-com-yes)

print the COM of all groups for all pull coordinates to the `pullx.xvg` file.

pull-print-ref-value[¶](#mdp-pull-print-ref-value)no[¶](#mdp-value-pull-print-ref-value-no)

do not print the reference value for each pull coordinate

yes[¶](#mdp-value-pull-print-ref-value-yes)

print the reference value for each pull coordinate to the `pullx.xvg` file.

pull-print-components[¶](#mdp-pull-print-components)no[¶](#mdp-value-pull-print-components-no)

only print the distance for each pull coordinate

yes[¶](#mdp-value-pull-print-components-yes)

print the distance and Cartesian components selected in [`pull-coord1-dim`](#mdp-pull-coord1-dim) to the `pullx.xvg` file.

pull-nstxout[¶](#mdp-pull-nstxout)

(50) interval for writing out the COMs of all the pull groups (0 is never) to the `pullx.xvg` file.

pull-nstfout[¶](#mdp-pull-nstfout)

(50) interval for writing out the force of all the pulled groups (0 is never) to the `pullf.xvg` file.

pull-pbc-ref-prev-step-com[¶](#mdp-pull-pbc-ref-prev-step-com)no[¶](#mdp-value-pull-pbc-ref-prev-step-com-no)

Use the reference atom ([`pull-group1-pbcatom`](#mdp-pull-group1-pbcatom)) for the treatment of periodic boundary conditions.

yes[¶](#mdp-value-pull-pbc-ref-prev-step-com-yes)

Use the COM of the previous step as reference for the treatment of periodic boundary conditions. The reference is initialized using the reference atom ([`pull-group1-pbcatom`](#mdp-pull-group1-pbcatom)), which should be located centrally in the group. Using the COM from the previous step can be useful if one or more pull groups are large or very flexible.

pull-xout-average[¶](#mdp-pull-xout-average)no[¶](#mdp-value-pull-xout-average-no)

Write the instantaneous coordinates for all the pulled groups.

yes[¶](#mdp-value-pull-xout-average-yes)

Write the average coordinates (since last output) for all the pulled groups. N.b., some analysis tools might expect instantaneous pull output.

pull-fout-average[¶](#mdp-pull-fout-average)no[¶](#mdp-value-pull-fout-average-no)

Write the instantaneous force for all the pulled groups.

yes[¶](#mdp-value-pull-fout-average-yes)

Write the average force (since last output) for all the pulled groups. N.b., some analysis tools might expect instantaneous pull output.

pull-ngroups[¶](#mdp-pull-ngroups)

(1) The number of pull groups, not including the absolute reference group, when used. Pull groups can be reused in multiple pull coordinates. Below only the pull options for group 1 are given, further groups simply increase the group index number.

pull-ncoords[¶](#mdp-pull-ncoords)

(1) The number of pull coordinates. Below only the pull options for coordinate 1 are given, further coordinates simply increase the coordinate index number.

pull-group1-name[¶](#mdp-pull-group1-name)

The name of the pull group, is looked up in the index file or in the default groups to obtain the atoms involved.

pull-group1-weights[¶](#mdp-pull-group1-weights)

Optional relative weights which are multiplied with the masses of the atoms to give the total weight for the COM. The number of weights should be 0, meaning all 1, or the number of atoms in the pull group.

pull-group1-pbcatom[¶](#mdp-pull-group1-pbcatom)

(0) The reference atom for the treatment of periodic boundary conditions inside the group (this has no effect on the treatment of the pbc between groups). This option is only important when the diameter of the pull group is larger than half the shortest box vector. For determining the COM, all atoms in the group are put at their periodic image which is closest to [`pull-group1-pbcatom`](#mdp-pull-group1-pbcatom). A value of 0 means that the middle atom (number wise) is used, which is only safe for small groups. [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) checks that the maximum distance from the reference atom (specifically chosen, or not) to the other atoms in the group is not too large. This parameter is not used with [`pull-coord1-geometry`](#mdp-pull-coord1-geometry) cylinder. A value of -1 turns on cosine weighting, which is useful for a group of molecules in a periodic system, *e.g.* a water slab (see Engin et al. J. Chem. Phys. B 2010).

pull-coord1-type[¶](#mdp-pull-coord1-type)umbrella[¶](#mdp-value-pull-coord1-type-umbrella)

Center of mass pulling using an umbrella potential between the reference group and one or more groups.

constraint[¶](#mdp-value-pull-coord1-type-constraint)

Center of mass pulling using a constraint between the reference group and one or more groups. The setup is identical to the option umbrella, except for the fact that a rigid constraint is applied instead of a harmonic potential. Note that this type is not supported in combination with multiple time stepping.

constant-force[¶](#mdp-value-pull-coord1-type-constant-force)

Center of mass pulling using a linear potential and therefore a constant force. For this option there is no reference position and therefore the parameters [`pull-coord1-init`](#mdp-pull-coord1-init) and [`pull-coord1-rate`](#mdp-pull-coord1-rate) are not used.

flat-bottom[¶](#mdp-value-pull-coord1-type-flat-bottom)

At distances above [`pull-coord1-init`](#mdp-pull-coord1-init) a harmonic potential is applied, otherwise no potential is applied.

flat-bottom-high[¶](#mdp-value-pull-coord1-type-flat-bottom-high)

At distances below [`pull-coord1-init`](#mdp-pull-coord1-init) a harmonic potential is applied, otherwise no potential is applied.

external-potential[¶](#mdp-value-pull-coord1-type-external-potential)

An external potential that needs to be provided by another module.

pull-coord1-potential-provider[¶](#mdp-pull-coord1-potential-provider)

The name of the external module that provides the potential for the case where [`pull-coord1-type=external-potential`](#mdp-value-pull-coord1-type-external-potential).

pull-coord1-geometry[¶](#mdp-pull-coord1-geometry)distance[¶](#mdp-value-pull-coord1-geometry-distance)

Pull along the vector connecting the two groups. Components can be selected with [`pull-coord1-dim`](#mdp-pull-coord1-dim).

direction[¶](#mdp-value-pull-coord1-geometry-direction)

Pull in the direction of [`pull-coord1-vec`](#mdp-pull-coord1-vec).

direction-periodic[¶](#mdp-value-pull-coord1-geometry-direction-periodic)

As [`pull-coord1-geometry=direction`](#mdp-value-pull-coord1-geometry-direction), but does not apply periodic box vector corrections to keep the distance within half the box length. This is (only) useful for pushing groups apart by more than half the box length by continuously changing the reference location using a pull rate. With this geometry the box should not be dynamic (*e.g.* no pressure scaling) in the pull dimensions and the pull force is not added to the virial.

direction-relative[¶](#mdp-value-pull-coord1-geometry-direction-relative)

As [`pull-coord1-geometry=direction`](#mdp-value-pull-coord1-geometry-direction), but the pull vector is the vector that points from the COM of a third to the COM of a fourth pull group. This means that 4 groups need to be supplied in [`pull-coord1-groups`](#mdp-pull-coord1-groups). Note that the pull force will give rise to a torque on the pull vector, which is turn leads to forces perpendicular to the pull vector on the two groups defining the vector. If you want a pull group to move between the two groups defining the vector, simply use the union of these two groups as the reference group.

cylinder[¶](#mdp-value-pull-coord1-geometry-cylinder)

Designed for pulling with respect to a layer where the reference COM is given by a local cylindrical part of the reference group. The pulling is in the direction of [`pull-coord1-vec`](#mdp-pull-coord1-vec). From the first of the two groups in [`pull-coord1-groups`](#mdp-pull-coord1-groups) a cylinder is selected around the axis going through the COM of the second group with direction [`pull-coord1-vec`](#mdp-pull-coord1-vec) with radius [`pull-cylinder-r`](#mdp-pull-cylinder-r). Weights of the atoms decrease continuously to zero as the radial distance goes from 0 to [`pull-cylinder-r`](#mdp-pull-cylinder-r) (mass weighting is also used). The radial dependence gives rise to radial forces on both pull groups. Note that the radius should be smaller than half the box size. For tilted cylinders they should be even smaller than half the box size since the distance of an atom in the reference group from the COM of the pull group has both a radial and an axial component. This geometry is not supported with constraint pulling.

angle[¶](#mdp-value-pull-coord1-geometry-angle)

Pull along an angle defined by four groups. The angle is defined as the angle between two vectors: the vector connecting the COM of the first group to the COM of the second group and the vector connecting the COM of the third group to the COM of the fourth group.

angle-axis[¶](#mdp-value-pull-coord1-geometry-angle-axis)

As [`pull-coord1-geometry=angle`](#mdp-value-pull-coord1-geometry-angle) but the second vector is given by [`pull-coord1-vec`](#mdp-pull-coord1-vec). Thus, only the two groups that define the first vector need to be given.

dihedral[¶](#mdp-value-pull-coord1-geometry-dihedral)

Pull along a dihedral angle defined by six groups. These pairwise define three vectors: the vector connecting the COM of group 1 to the COM of group 2, the COM of group 3 to the COM of group 4, and the COM of group 5 to the COM group 6. The dihedral angle is then defined as the angle between two planes: the plane spanned by the the two first vectors and the plane spanned the two last vectors.

transformation[¶](#mdp-value-pull-coord1-geometry-transformation)

Transforms other pull coordinates using a mathematical expression defined by [`pull-coord1-expression`](#mdp-pull-coord1-expression). Pull coordinates of lower indices, and time, can be used as variables to this pull coordinate. Thus, pull transformation coordinates should have a higher pull coordinate index than all pull coordinates they transform.

pull-coord1-expression[¶](#mdp-pull-coord1-expression)

Mathematical expression to transform pull coordinates of lower indices to a new one. The pull coordinates are referred to as variables in the equation so that pull-coord1’s value becomes ‘x1’, pull-coord2 value becomes ‘x2’ etc. Time can also be used a variable, becoming ‘t’. Note that angular coordinates use units of radians in the expression. The mathematical expression are evaluated using muParser. Only relevant if [`pull-coord1-geometry=transformation`](#mdp-value-pull-coord1-geometry-transformation).

pull-coord1-dx[¶](#mdp-pull-coord1-dx)

(1e-9) Size of finite difference to use in numerical derivation of the pull coordinate with respect to other pull coordinates. The current implementation uses a simple first order finite difference method to perform derivation so that f’(x) = (f(x+dx)-f(x))/dx Only relevant if [`pull-coord1-geometry=transformation`](#mdp-value-pull-coord1-geometry-transformation).

pull-coord1-groups[¶](#mdp-pull-coord1-groups)

The group indices on which this pull coordinate will operate. The number of group indices required is geometry dependent. The first index is the reference group and can be 0, in which case an absolute reference of [`pull-coord1-origin`](#mdp-pull-coord1-origin) is used. With an absolute reference the system is no longer translation invariant and one should think about what to do with the center of mass motion.

pull-coord1-dim[¶](#mdp-pull-coord1-dim)

(Y Y Y) Selects the dimensions that this pull coordinate acts on and that are printed to the output files when [`pull-print-components`](#mdp-pull-print-components) = [`pull-coord1-start=yes`](#mdp-value-pull-coord1-start-yes). With [`pull-coord1-geometry`](#mdp-pull-coord1-geometry) = [`pull-coord1-geometry=distance`](#mdp-value-pull-coord1-geometry-distance), only Cartesian components set to Y contribute to the distance. Thus setting this to Y Y N results in a distance in the x/y plane. With other geometries all dimensions with non-zero entries in [`pull-coord1-vec`](#mdp-pull-coord1-vec) should be set to Y, the values for other dimensions only affect the output.

pull-coord1-origin[¶](#mdp-pull-coord1-origin)

(0.0 0.0 0.0) The pull reference position for use with an absolute reference.

pull-coord1-vec[¶](#mdp-pull-coord1-vec)

(0.0 0.0 0.0) The pull direction. [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) normalizes the vector.

pull-coord1-start[¶](#mdp-pull-coord1-start)no[¶](#mdp-value-pull-coord1-start-no)

do not modify [`pull-coord1-init`](#mdp-pull-coord1-init)

yes[¶](#mdp-value-pull-coord1-start-yes)

add the COM distance of the starting conformation to [`pull-coord1-init`](#mdp-pull-coord1-init)

pull-coord1-init[¶](#mdp-pull-coord1-init)

(0.0) [nm] or [deg] The reference distance or reference angle at t=0.

pull-coord1-rate[¶](#mdp-pull-coord1-rate)

(0) [nm/ps] or [deg/ps] The rate of change of the reference position or reference angle.

pull-coord1-k[¶](#mdp-pull-coord1-k)

(0) [kJ mol<sup>-1</sup> nm<sup>-2</sup>] or [kJ mol<sup>-1</sup> nm<sup>-1</sup>] or [kJ mol<sup>-1</sup> rad<sup>-2</sup>] or [kJ mol<sup>-1</sup> rad<sup>-1</sup>] The force constant. For umbrella pulling this is the harmonic force constant in kJ mol<sup>-1</sup> nm<sup>-2</sup> (or kJ mol<sup>-1</sup> rad<sup>-2</sup> for angles). For constant force pulling this is the force constant of the linear potential, and thus the negative (!) of the constant force in kJ mol<sup>-1</sup> nm<sup>-1</sup> (or kJ mol<sup>-1</sup> rad<sup>-1</sup> for angles). Note that for angles the force constant is expressed in terms of radians (while [`pull-coord1-init`](#mdp-pull-coord1-init) and [`pull-coord1-rate`](#mdp-pull-coord1-rate) are expressed in degrees).

pull-coord1-kB[¶](#mdp-pull-coord1-kB)

(pull-k1) [kJ mol<sup>-1</sup> nm<sup>-2</sup>] or [kJ mol<sup>-1</sup> nm<sup>-1</sup>] or [kJ mol<sup>-1</sup> rad<sup>-2</sup>] or [kJ mol<sup>-1</sup> rad<sup>-1</sup>] As [`pull-coord1-k`](#mdp-pull-coord1-k), but for state B. This is only used when [`free-energy`](#mdp-free-energy) is turned on. The force constant is then (1 - lambda) * [`pull-coord1-k`](#mdp-pull-coord1-k) + lambda * [`pull-coord1-kB`](#mdp-pull-coord1-kB).

### AWH adaptive biasing[¶](#awh-adaptive-biasing)

awh[¶](#mdp-awh)no[¶](#mdp-value-awh-no)

No biasing.

yes[¶](#mdp-value-awh-yes)

Adaptively bias a reaction coordinate using the AWH method and estimate the corresponding PMF. This requires a constant ensemble temperature to be available. The PMF and other AWH data are written to the energy file ([edr](../reference-manual/file-formats.html#edr)) at an interval set by [`awh-nstout`](#mdp-awh-nstout) and can be extracted with the `gmxawh` tool. The AWH coordinate can be multidimensional and is defined by mapping each dimension to a pull coordinate index (and/or up to one alchemical free lambda state dimension [`free-energy`](#mdp-free-energy)). This is only allowed if [`pull-coord1-type=external-potential`](#mdp-value-pull-coord1-type-external-potential) and [`pull-coord1-potential-provider`](#mdp-pull-coord1-potential-provider) = `awh` for the concerned pull coordinate indices. Pull geometry ‘direction-periodic’ and transformation coordinates that depend on time are not supported by AWH.

awh-potential[¶](#mdp-awh-potential)convolved[¶](#mdp-value-awh-potential-convolved)

The applied biasing potential is the convolution of the bias function and a set of harmonic umbrella potentials (see [`awh-potential=umbrella`](#mdp-value-awh-potential-umbrella) below). This results in a smooth potential function and force. The resolution of the potential is set by the force constant of each umbrella, see [`awh1-dim1-force-constant`](#mdp-awh1-dim1-force-constant). This option is not compatible with using the free energy lambda state as an AWH reaction coordinate dimension.

umbrella[¶](#mdp-value-awh-potential-umbrella)

The potential bias is applied by controlling the position of a harmonic potential using Monte-Carlo sampling. The force constant is set with [`awh1-dim1-force-constant`](#mdp-awh1-dim1-force-constant). The umbrella location is sampled using Monte-Carlo every [`awh-nstsample`](#mdp-awh-nstsample) steps. This is option is required when using the free energy lambda state as an AWH reaction coordinate dimension. Apart from that, this option is mainly for comparison and testing purposes as there are no advantages to using an umbrella.

awh-share-multisim[¶](#mdp-awh-share-multisim)no[¶](#mdp-value-awh-share-multisim-no)

AWH will not share biases across simulations started with [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) option `-multidir`. The biases will be independent.

yes[¶](#mdp-value-awh-share-multisim-yes)

With [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) and option `-multidir` the bias and PMF estimates for biases with [`awh1-share-group`](#mdp-awh1-share-group) &gt;0 will be shared across simulations with the biases with the same [`awh1-share-group`](#mdp-awh1-share-group) value. The simulations should have the same AWH settings for sharing to make sense. [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) will check whether the simulations are technically compatible for sharing, but the user should check that bias sharing physically makes sense.

awh-seed[¶](#mdp-awh-seed)

(-1) Random seed for Monte-Carlo sampling the umbrella position, where -1 indicates to generate a seed. Only used with [`awh-potential=umbrella`](#mdp-value-awh-potential-umbrella).

awh-nstout[¶](#mdp-awh-nstout)

(100000) Number of steps between printing AWH data to the energy file, should be a multiple of [`nstenergy`](#mdp-nstenergy).

awh-nstsample[¶](#mdp-awh-nstsample)

(10) Number of steps between sampling of the coordinate value. This sampling is the basis for updating the bias and estimating the PMF and other AWH observables.

awh-nsamples-update[¶](#mdp-awh-nsamples-update)

(100) The number of coordinate samples used for each AWH update. The update interval in steps is [`awh-nstsample`](#mdp-awh-nstsample) times this value.

awh-nbias[¶](#mdp-awh-nbias)

(1) The number of biases, each acting on its own coordinate. The following options should be specified for each bias although below only the options for bias number 1 is shown. Options for other bias indices are obtained by replacing ‘1’ by the bias index.

awh1-error-init[¶](#mdp-awh1-error-init)

(10.0) [kJ mol<sup>-1</sup>] Estimated initial average error of the PMF for this bias. This value together with an estimate of the crossing time, based on the length of the sampling interval and the given diffusion constant(s) [`awh1-dim1-diffusion`](#mdp-awh1-dim1-diffusion), determine the initial biasing rate. With multiple dimensions, the longest crossing time is used. The error is obviously not known *a priori*. Only a rough estimate of [`awh1-error-init`](#mdp-awh1-error-init) is needed however. As a general guideline, leave [`awh1-error-init`](#mdp-awh1-error-init) to its default value when starting a new simulation. On the other hand, when there is *a priori* knowledge of the PMF (e.g. when an initial PMF estimate is provided, see the [`awh1-user-data`](#mdp-awh1-user-data) option) then [`awh1-error-init`](#mdp-awh1-error-init) should reflect that knowledge.

awh1-growth[¶](#mdp-awh1-growth)

Each bias keeps a reference weight histogram for the coordinate samples. Its size sets the magnitude of the bias function and free energy estimate updates (few samples corresponds to large updates and vice versa). Thus, its growth rate sets the maximum convergence rate.

exp-linear[¶](#mdp-value-awh1-growth-exp-linear)

By default, there is an initial stage in which the histogram grows close to exponentially (but slower than the sampling rate). In the final stage that follows, the growth rate is linear and equal to the sampling rate (set by [`awh-nstsample`](#mdp-awh-nstsample)). The initial stage is typically necessary for efficient convergence when starting a new simulation where high free energy barriers have not yet been flattened by the bias.

linear[¶](#mdp-value-awh1-growth-linear)

As [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear) but skip the initial stage. This may be useful if there is *a priori* knowledge (see [`awh1-error-init`](#mdp-awh1-error-init)) which eliminates the need for an initial stage. This is also the setting compatible with [`awh1-target=local-boltzmann`](#mdp-value-awh1-target-local-boltzmann).

awh1-growth-factor[¶](#mdp-awh1-growth-factor)

(2) [] The growth factor $\gamma$ during the exponential phase with [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear). Should be larger than 1.

awh1-equilibrate-histogram[¶](#mdp-awh1-equilibrate-histogram)yes[¶](#mdp-value-awh1-equilibrate-histogram-yes)

Before entering the initial stage (see [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear)), make sure the histogram of sampled weights is following the target distribution closely enough (specifically, at least 80% of the target region needs to have a local relative error of less than `awh1-histogram-tolerance`). This option is particularly important when [`awh1-share-group`](#mdp-awh1-share-group) &gt; 0 and the initial configurations poorly represent the target distribution.

no[¶](#mdp-value-awh1-equilibrate-histogram-no)

Do not equilibrate the histogram.

awh1-histogram-tolerance[¶](#mdp-awh1-histogram-tolerance)

(0.3) [] The relative tolerance for the histogram of sampled weigths, used with [`awh1-equilibrate-histogram=yes`](#mdp-value-awh1-equilibrate-histogram-yes). The value of 0.3 is sufficiently large to not slow down the convergence, even when a single walker is used.

awh1-target[¶](#mdp-awh1-target)constant[¶](#mdp-value-awh1-target-constant)

The bias is tuned towards a constant (uniform) coordinate distribution in the defined sampling interval (defined by [[`awh1-dim1-start`](#mdp-awh1-dim1-start), [`awh1-dim1-end`](#mdp-awh1-dim1-end)]).

cutoff[¶](#mdp-value-awh1-target-cutoff)

Similar to [`awh1-target=constant`](#mdp-value-awh1-target-constant), but the target distribution is proportional to 1/(1 + exp(F - [`awh1-target=cutoff`](#mdp-value-awh1-target-cutoff))), where F is the free energy relative to the estimated global minimum. This provides a smooth switch of a flat target distribution in regions with free energy lower than the cut-off to a Boltzmann distribution in regions with free energy higher than the cut-off.

boltzmann[¶](#mdp-value-awh1-target-boltzmann)

The target distribution is a Boltzmann distribtution with a scaled beta (inverse temperature) factor given by [`awh1-target-beta-scaling`](#mdp-awh1-target-beta-scaling). *E.g.*, a value of 0.1 would give the same coordinate distribution as sampling with a simulation temperature scaled by 10.

local-boltzmann[¶](#mdp-value-awh1-target-local-boltzmann)

Same target distribution and use of [`awh1-target-beta-scaling`](#mdp-awh1-target-beta-scaling) but the convergence towards the target distribution is inherently local *i.e.*, the rate of change of the bias only depends on the local sampling. This local convergence property is only compatible with [`awh1-growth=linear`](#mdp-value-awh1-growth-linear), since for [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear) histograms are globally rescaled in the initial stage.

awh1-target-beta-scaling[¶](#mdp-awh1-target-beta-scaling)

(0) For [`awh1-target=boltzmann`](#mdp-value-awh1-target-boltzmann) and [`awh1-target=local-boltzmann`](#mdp-value-awh1-target-local-boltzmann) it is the unitless beta scaling factor taking values in (0,1).

awh1-target-cutoff[¶](#mdp-awh1-target-cutoff)

(0) [kJ mol<sup>-1</sup>] For [`awh1-target=cutoff`](#mdp-value-awh1-target-cutoff) this is the cutoff, should be &gt; 0.

awh1-user-data[¶](#mdp-awh1-user-data)no[¶](#mdp-value-awh1-user-data-no)

Initialize the PMF and target distribution with default values.

yes[¶](#mdp-value-awh1-user-data-yes)

Initialize the PMF and target distribution with user provided data. For [`awh-nbias`](#mdp-awh-nbias) = 1, [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) will expect a file `awhinit.xvg` to be present in the run directory. For multiple biases, [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) expects files `awhinit1.xvg`, `awhinit2.xvg`, etc. The file name can be changed with the `-awh` option. The first [`awh1-ndim`](#mdp-awh1-ndim) columns of each input file should contain the coordinate values, such that each row defines a point in coordinate space. Column [`awh1-ndim`](#mdp-awh1-ndim) + 1 should contain the PMF value (in kT) for each point. The target distribution column can either follow the PMF (column [`awh1-ndim`](#mdp-awh1-ndim) + 2) or be in the same column as written by [gmx awh](../onlinehelp/gmx-awh.html#gmx-awh).

awh1-share-group[¶](#mdp-awh1-share-group)0[¶](#mdp-value-awh1-share-group-0)

Do not share the bias.

positive[¶](#mdp-value-awh1-share-group-positive)

Share the bias and PMF estimates between simulations. This currently only works between biases with the same index. Note that currently sharing within a single simulation is not supported. The bias will be shared across simulations that specify the same value for [`awh1-share-group`](#mdp-awh1-share-group). To enable this, use [`awh-share-multisim=yes`](#mdp-value-awh-share-multisim-yes) and the [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) option `-multidir`. Sharing may increase convergence initially, although the starting configurations can be critical, especially when sharing between many biases. N.b., multiple walkers sharing a degenerate reaction coordinate may have problems overlapping their sampling, possibly making it difficult to cover the sampling interval.

awh1-target-metric-scaling[¶](#mdp-awh1-target-metric-scaling)no[¶](#mdp-value-awh1-target-metric-scaling-no)

Do not scale the target distribution based on the AWH friction metric.

yes[¶](#mdp-value-awh1-target-metric-scaling-yes)

Scale the target distribution based on the AWH friction metric. Regions with high friction (long autocorrelation times) will be sampled more. The diffusion metric is the inverse of the friction metric. This scaling can be used with any [`awh1-target`](#mdp-awh1-target) type and is applied after user-provided target distribution modifications ([`awh1-user-data`](#mdp-awh1-user-data)), if any. If [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear), the target distribution scaling starts after leaving the initial phase.

awh1-target-metric-scaling-limit[¶](#mdp-awh1-target-metric-scaling-limit)

(10) The upper limit of scaling, relative to the average, when `awh1-target-metric-scaling` is enabled. The lower limit will be the inverse of this value. This upper limit should be &gt; 1.

awh1-ndim[¶](#mdp-awh1-ndim)

(1) [integer] Number of dimensions of the coordinate, each dimension maps to 1 pull coordinate. The following options should be specified for each such dimension. Below only the options for dimension number 1 is shown. Options for other dimension indices are obtained by replacing ‘1’ by the dimension index.

awh1-dim1-coord-provider[¶](#mdp-awh1-dim1-coord-provider)pull[¶](#mdp-value-awh1-dim1-coord-provider-pull)

The pull module is providing the reaction coordinate for this dimension. With multiple time-stepping, AWH and pull should be in the same MTS level.

fep-lambda[¶](#mdp-value-awh1-dim1-coord-provider-fep-lambda)

The free energy [`free-energy`](#mdp-free-energy) lambda state is the reaction coordinate for this dimension. The lambda states to use are specified by [`fep-lambdas`](#mdp-fep-lambdas), [`vdw-lambdas`](#mdp-vdw-lambdas), [`coul-lambdas`](#mdp-coul-lambdas) etc. This is not compatible with delta-lambda. It also requires `calc-lambda-neighbors=-1`. With multiple time-stepping, AWH should be in the slow level. This option requires [`awh-potential=umbrella`](#mdp-value-awh-potential-umbrella).

awh1-dim1-coord-index[¶](#mdp-awh1-dim1-coord-index)

(1) Index of the pull coordinate defining this coordinate dimension.

awh1-dim1-force-constant[¶](#mdp-awh1-dim1-force-constant)

(0) [kJ mol<sup>-1</sup> nm<sup>-2</sup>] or [kJ mol<sup>-1</sup> rad<sup>-2</sup>] Force constant for the (convolved) umbrella potential(s) along this coordinate dimension.

awh1-dim1-start[¶](#mdp-awh1-dim1-start)

(0.0) [nm] or [deg] Start value of the sampling interval along this dimension. The range of allowed values depends on the relevant pull geometry (see [`pull-coord1-geometry`](#mdp-pull-coord1-geometry)). For dihedral geometries [`awh1-dim1-start`](#mdp-awh1-dim1-start) greater than [`awh1-dim1-end`](#mdp-awh1-dim1-end) is allowed. The interval will then wrap around from +period/2 to -period/2. For the direction geometry, the dimension is made periodic when the direction is along a box vector and covers more than 95% of the box length. Note that one should not apply pressure coupling along a periodic dimension.

awh1-dim1-end[¶](#mdp-awh1-dim1-end)

(0.0) [nm] or [deg] End value defining the sampling interval together with [`awh1-dim1-start`](#mdp-awh1-dim1-start).

awh1-dim1-diffusion[¶](#mdp-awh1-dim1-diffusion)

(10<sup>-5</sup>) [nm<sup>2</sup>/ps], [rad<sup>2</sup>/ps] or [ps<sup>-1</sup>] Estimated diffusion constant for this coordinate dimension determining the initial biasing rate. This needs only be a rough estimate and should not critically affect the results unless it is set to something very low, leading to slow convergence, or very high, forcing the system far from equilibrium. Not setting this value explicitly generates a warning.

awh1-dim1-cover-diameter[¶](#mdp-awh1-dim1-cover-diameter)

(0.0) [nm] or [deg] Diameter that needs to be sampled by a single simulation around a coordinate value before the point is considered covered in the initial stage (see [`awh1-growth=exp-linear`](#mdp-value-awh1-growth-exp-linear)). A value &gt; 0 ensures that for each covering there is a continuous transition of this diameter across each coordinate value. This is trivially true for independent simulations but not for for multiple bias-sharing simulations ([`awh1-share-group`](#mdp-awh1-share-group)&gt;0). For a diameter = 0, covering occurs as soon as the simulations have sampled the whole interval, which for many sharing simulations does not guarantee transitions across free energy barriers. On the other hand, when the diameter &gt;= the sampling interval length, covering occurs when a single simulation has independently sampled the whole interval.

### Enforced rotation[¶](#enforced-rotation)

These [mdp](../reference-manual/file-formats.html#mdp) parameters can be used enforce the rotation of a group of atoms, e.g. a protein subunit. The [reference manual](../manual-2026.4.pdf) describes in detail 13 different potentials that can be used to achieve such a rotation.

rotation[¶](#mdp-rotation)no[¶](#mdp-value-rotation-no)

No enforced rotation will be applied. All enforced rotation options will be ignored (and if present in the [mdp](../reference-manual/file-formats.html#mdp) file, they unfortunately generate warnings).

yes[¶](#mdp-value-rotation-yes)

Apply the rotation potential specified by [`rot-type0`](#mdp-rot-type0) to the group of atoms given under the [`rot-group0`](#mdp-rot-group0) option.

rot-ngroups[¶](#mdp-rot-ngroups)

(1) Number of rotation groups.

rot-group0[¶](#mdp-rot-group0)

Name of rotation group 0 in the index file.

rot-type0[¶](#mdp-rot-type0)

(iso) Type of rotation potential that is applied to rotation group 0. Can be of of the following: `iso`, `iso-pf`, `pm`, `pm-pf`, `rm`, `rm-pf`, `rm2`, `rm2-pf`, `flex`, `flex-t`, `flex2`, or `flex2-t`.

rot-massw0[¶](#mdp-rot-massw0)

(no) Use mass weighted rotation group positions.

rot-vec0[¶](#mdp-rot-vec0)

(1.0 0.0 0.0) Rotation vector, will get normalized.

rot-pivot0[¶](#mdp-rot-pivot0)

(0.0 0.0 0.0) [nm] Pivot point for the potentials `iso`, `pm`, `rm`, and `rm2`.

rot-rate0[¶](#mdp-rot-rate0)

(0) [degree ps<sup>-1</sup>] Reference rotation rate of group 0.

rot-k0[¶](#mdp-rot-k0)

(0) [kJ mol<sup>-1</sup> nm<sup>-2</sup>] Force constant for group 0.

rot-slab-dist0[¶](#mdp-rot-slab-dist0)

(1.5) [nm] Slab distance, if a flexible axis rotation type was chosen.

rot-min-gauss0[¶](#mdp-rot-min-gauss0)

(0.001) Minimum value (cutoff) of Gaussian function for the force to be evaluated (for the flexible axis potentials).

rot-eps0[¶](#mdp-rot-eps0)

(0.0001) [nm<sup>2</sup>] Value of additive constant epsilon for `rm2*` and `flex2*` potentials.

rot-fit-method0[¶](#mdp-rot-fit-method0)

(rmsd) Fitting method when determining the actual angle of a rotation group (can be one of `rmsd`, `norm`, or `potential`).

rot-potfit-nsteps0[¶](#mdp-rot-potfit-nsteps0)

(21) For fit type `potential`, the number of angular positions around the reference angle for which the rotation potential is evaluated.

rot-potfit-step0[¶](#mdp-rot-potfit-step0)

(0.25) For fit type `potential`, the distance in degrees between two angular positions.

rot-nstrout[¶](#mdp-rot-nstrout)

(100) Output interval (in steps) for the angle of the rotation group, as well as for the torque and the rotation potential energy.

rot-nstsout[¶](#mdp-rot-nstsout)

(1000) Output interval (in steps) for per-slab data of the flexible axis potentials, i.e. angles, torques and slab centers.

### NMR refinement[¶](#nmr-refinement)

disre[¶](#mdp-disre)no[¶](#mdp-value-disre-no)

ignore distance restraint information in topology file

simple[¶](#mdp-value-disre-simple)

simple (per-molecule) distance restraints.

ensemble[¶](#mdp-value-disre-ensemble)

distance restraints over an ensemble of molecules in one simulation box. Normally, one would perform ensemble averaging over multiple simulations, using `mdrun-multidir`. The environment variable `GMX_DISRE_ENSEMBLE_SIZE` sets the number of systems within each ensemble (usually equal to the number of directories supplied to `mdrun-multidir`).

disre-weighting[¶](#mdp-disre-weighting)equal[¶](#mdp-value-disre-weighting-equal)

divide the restraint force equally over all atom pairs in the restraint

conservative[¶](#mdp-value-disre-weighting-conservative)

the forces are the derivative of the restraint potential, this results in an weighting of the atom pairs to the reciprocal seventh power of the displacement. The forces are conservative when [`disre-tau`](#mdp-disre-tau) is zero.

disre-mixed[¶](#mdp-disre-mixed)no[¶](#mdp-value-disre-mixed-no)

the violation used in the calculation of the restraint force is the time-averaged violation

yes[¶](#mdp-value-disre-mixed-yes)

the violation used in the calculation of the restraint force is the square root of the product of the time-averaged violation and the instantaneous violation

disre-fc[¶](#mdp-disre-fc)

(1000) [kJ mol<sup>-1</sup> nm<sup>-2</sup>] force constant for distance restraints, which is multiplied by a (possibly) different factor for each restraint given in the `fac` column of the interaction in the topology file.

disre-tau[¶](#mdp-disre-tau)

(0) [ps] time constant for distance restraints running average. A value of zero turns off time averaging.

nstdisreout[¶](#mdp-nstdisreout)

(100) [steps] period between steps when the running time-averaged and instantaneous distances of all atom pairs involved in restraints are written to the energy file (can make the energy file very large)

orire[¶](#mdp-orire)no[¶](#mdp-value-orire-no)

ignore orientation restraint information in topology file

yes[¶](#mdp-value-orire-yes)

use orientation restraints, ensemble averaging can be performed with `mdrun-multidir`

orire-fc[¶](#mdp-orire-fc)

(0) [kJ mol<sup>-1</sup>] force constant for orientation restraints, which is multiplied by a (possibly) different weight factor for each restraint, can be set to zero to obtain the orientations from a free simulation

orire-tau[¶](#mdp-orire-tau)

(0) [ps] time constant for orientation restraints running average. A value of zero turns off time averaging.

orire-fitgrp[¶](#mdp-orire-fitgrp)

fit group for orientation restraining. This group of atoms is used to determine the rotation **R** of the system with respect to the reference orientation. The reference orientation is the starting conformation of the first subsystem. For a protein, backbone is a reasonable choice

nstorireout[¶](#mdp-nstorireout)

(100) [steps] period between steps when the running time-averaged and instantaneous orientations for all restraints, and the molecular order tensor are written to the energy file (can make the energy file very large)

### Free energy calculations[¶](#free-energy-calculations)

free-energy[¶](#mdp-free-energy)no[¶](#mdp-value-free-energy-no)

Only use topology A.

yes[¶](#mdp-value-free-energy-yes)

Interpolate between topology A (lambda=0) to topology B (lambda=1) and write the derivative of the Hamiltonian with respect to lambda (as specified with [`dhdl-derivatives`](#mdp-dhdl-derivatives)), or the Hamiltonian differences with respect to other “foreign” lambda values (as specified with [`calc-lambda-neighbors`](#mdp-calc-lambda-neighbors)) to the energy file and/or to `dhdl.xvg`, where they can be processed by, for example [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar). The potentials, bond-lengths and angles are interpolated linearly as described in the manual. When [`sc-alpha`](#mdp-sc-alpha) is larger than zero, soft-core potentials are used for the LJ and Coulomb interactions.

expanded[¶](#mdp-value-free-energy-expanded)

Turns on expanded ensemble simulation, where the alchemical state becomes a dynamic variable, allowing jumping between different Hamiltonians. See the expanded ensemble options for controlling how expanded ensemble simulations are performed. The different Hamiltonians used in expanded ensemble simulations are defined by the other free energy options.

init-lambda[¶](#mdp-init-lambda)

(-1) starting value for lambda (float). Generally, this should only be used with slow growth (*i.e.* nonzero [`delta-lambda`](#mdp-delta-lambda)). In other cases, [`init-lambda-state`](#mdp-init-lambda-state) should be specified instead. If a lambda vector is given, [`init-lambda`](#mdp-init-lambda) is used to interpolate the vector instead of setting lambda directly. Must be greater than or equal to 0.

delta-lambda[¶](#mdp-delta-lambda)

(0) increment per time step for lambda

init-lambda-state[¶](#mdp-init-lambda-state)

(-1) starting value for the lambda state (integer). Specifies which column of the lambda vector ([`coul-lambdas`](#mdp-coul-lambdas), [`vdw-lambdas`](#mdp-vdw-lambdas), [`bonded-lambdas`](#mdp-bonded-lambdas), [`restraint-lambdas`](#mdp-restraint-lambdas), [`mass-lambdas`](#mdp-mass-lambdas), [`temperature-lambdas`](#mdp-temperature-lambdas), [`fep-lambdas`](#mdp-fep-lambdas)) should be used. This is a zero-based index: `init-lambda-state=0` means the first column, and so on.

fep-lambdas[¶](#mdp-fep-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. Free energy differences between different lambda values can then be determined with [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar). [`fep-lambdas`](#mdp-fep-lambdas) is different from the other -lambdas keywords because all components of the lambda vector that are not specified will use [`fep-lambdas`](#mdp-fep-lambdas).

coul-lambdas[¶](#mdp-coul-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. If soft-core potentials are used, values must be between 0 and 1. Only the electrostatic interactions are controlled with this component of the lambda vector (and only if the lambda=0 and lambda=1 states have differing electrostatic interactions).

vdw-lambdas[¶](#mdp-vdw-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. If soft-core potentials are used, values must be between 0 and 1. Only the van der Waals interactions are controlled with this component of the lambda vector.

bonded-lambdas[¶](#mdp-bonded-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. Only the bonded interactions are controlled with this component of the lambda vector.

restraint-lambdas[¶](#mdp-restraint-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. Only the restraint interactions: dihedral restraints, and the pull code restraints are controlled with this component of the lambda vector.

mass-lambdas[¶](#mdp-mass-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. Only the particle masses are controlled with this component of the lambda vector.

temperature-lambdas[¶](#mdp-temperature-lambdas)

[array] Zero, one or more lambda values for which Delta H values will be determined and written to dhdl.xvg every [`nstdhdl`](#mdp-nstdhdl) steps. Values must be greater than or equal to 0; values greater than 1 are allowed but should be used carefully. Only the temperatures are controlled with this component of the lambda vector. Note that these lambdas should not be used for replica exchange, only for simulated tempering.

calc-lambda-neighbors[¶](#mdp-calc-lambda-neighbors)

(1) Controls the number of lambda values for which Delta H values will be calculated and written out, if [`init-lambda-state`](#mdp-init-lambda-state) has been set. These lambda values are referred to as “foreign” lambdas. A positive value will limit the number of lambda points calculated to only the nth neighbors of [`init-lambda-state`](#mdp-init-lambda-state): for example, if [`init-lambda-state`](#mdp-init-lambda-state) is 5 and this parameter has a value of 2, energies for lambda points 3-7 will be calculated and writen out. A value of -1 means all lambda points will be written out. For normal BAR such as with [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar), a value of 1 is sufficient, while for MBAR -1 should be used.

sc-function[¶](#mdp-sc-function)

(beutler)

beutler[¶](#mdp-value-sc-function-beutler)

Beutler *et al.* soft-core function

gapsys[¶](#mdp-value-sc-function-gapsys)

Gapsys *et al.* soft-core function

sc-alpha[¶](#mdp-sc-alpha)

(0) for [`sc-function=beutler`](#mdp-value-sc-function-beutler) the soft-core alpha parameter, a value of 0 results in linear interpolation of the LJ and Coulomb interactions. Used only with [`sc-function=beutler`](#mdp-value-sc-function-beutler)

sc-r-power[¶](#mdp-sc-r-power)

(6) power 6 for the radial term in the soft-core equation. Used only with [`sc-function=beutler`](#mdp-value-sc-function-beutler)

sc-coul[¶](#mdp-sc-coul)

(no) Whether to apply the soft-core free energy interaction transformation to the Coulombic interaction of a molecule. Default is no, as it is generally more efficient to turn off the Coulombic interactions linearly before turning off the van der Waals interactions. Note that it is only taken into account when there are multiple lambda components, and you can still turn off soft-core interactions by setting [`sc-alpha`](#mdp-sc-alpha) to 0. Used only with [`sc-function=beutler`](#mdp-value-sc-function-beutler)

sc-power[¶](#mdp-sc-power)

(1) the power for lambda in the soft-core function, only the values 1 and 2 are supported. Used only with [`sc-function=beutler`](#mdp-value-sc-function-beutler)

sc-sigma[¶](#mdp-sc-sigma)

(0.3) [nm] for [`sc-function=beutler`](#mdp-value-sc-function-beutler) the soft-core sigma for particles which have a C6 or C12 parameter equal to zero or a sigma smaller than [`sc-sigma`](#mdp-sc-sigma). Used only with [`sc-function=beutler`](#mdp-value-sc-function-beutler)

sc-gapsys-scale-linpoint-lj[¶](#mdp-sc-gapsys-scale-linpoint-lj)

(0.85) for [`sc-function=gapsys`](#mdp-value-sc-function-gapsys) it is the unitless alphaLJ parameter. It controls the softness of the van der Waals interactions by scaling the point for linearizing the vdw force. Setting it to 0 will result in the standard hard-core van der Waals interactions. Used only with [`sc-function=gapsys`](#mdp-value-sc-function-gapsys)

sc-gapsys-scale-linpoint-q[¶](#mdp-sc-gapsys-scale-linpoint-q)

(0.3) [nm/e^2] For [`sc-function=gapsys`](#mdp-value-sc-function-gapsys) the alphaQ parameter with a default value of 0.3. It controls the softness of the Coulombic interactions. Setting it to 0 will result in the standard hard-core Coulombic interactions. Used only with [`sc-function=gapsys`](#mdp-value-sc-function-gapsys)

sc-gapsys-sigma-lj[¶](#mdp-sc-gapsys-sigma-lj)

(0.3) [nm] for [`sc-function=gapsys`](#mdp-value-sc-function-gapsys) the soft-core sigma for particles which have a C6 or C12 parameter equal to zero. Used only with [`sc-function=gapsys`](#mdp-value-sc-function-gapsys)

couple-moltype[¶](#mdp-couple-moltype)

Here one can supply a molecule type (as defined in the topology) for calculating solvation or coupling free energies. There is a special option `system` that couples all molecule types in the system. This can be useful for equilibrating a system starting from (nearly) random coordinates. [`free-energy`](#mdp-free-energy) has to be turned on. The Van der Waals interactions and/or charges in this molecule type can be turned on or off between lambda=0 and lambda=1, depending on the settings of [`couple-lambda0`](#mdp-couple-lambda0) and [`couple-lambda1`](#mdp-couple-lambda1). If you want to decouple one of several copies of a molecule, you need to copy and rename the molecule definition in the topology.

couple-lambda0[¶](#mdp-couple-lambda0)vdw-q[¶](#mdp-value-couple-lambda0-vdw-q)

all interactions are on at lambda=0

vdw[¶](#mdp-value-couple-lambda0-vdw)

the charges are zero (no Coulomb interactions) at lambda=0

q[¶](#mdp-value-couple-lambda0-q)

the Van der Waals interactions are turned off at lambda=0; soft-core interactions will be required to avoid singularities

none[¶](#mdp-value-couple-lambda0-none)

the Van der Waals interactions are turned off and the charges are zero at lambda=0; soft-core interactions will be required to avoid singularities.

couple-lambda1[¶](#mdp-couple-lambda1)

analogous to [`couple-lambda0`](#mdp-couple-lambda0), but for lambda=1

couple-intramol[¶](#mdp-couple-intramol)no[¶](#mdp-value-couple-intramol-no)

All intra-molecular non-bonded interactions for moleculetype [`couple-moltype`](#mdp-couple-moltype) are replaced by exclusions and explicit pair interactions. In this manner the decoupled state of the molecule corresponds to the proper vacuum state without periodicity effects.

yes[¶](#mdp-value-couple-intramol-yes)

The intra-molecular Van der Waals and Coulomb interactions are also turned on/off. This can be useful for partitioning free-energies of relatively large molecules, where the intra-molecular non-bonded interactions might lead to kinetically trapped vacuum conformations. The 1-4 pair interactions are not turned off.

nstdhdl[¶](#mdp-nstdhdl)

(100) the interval for writing dH/dlambda and possibly Delta H to dhdl.xvg, 0 means no ouput, should be a multiple of [`nstcalcenergy`](#mdp-nstcalcenergy).

dhdl-derivatives[¶](#mdp-dhdl-derivatives)

(yes)

If yes (the default), the derivatives of the Hamiltonian with respect to lambda at each [`nstdhdl`](#mdp-nstdhdl) step are written out. These values are needed for interpolation of linear energy differences with [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar) (although the same can also be achieved with the right [`calc-lambda-neighbors`](#mdp-calc-lambda-neighbors) setting, that may not be as flexible), or with thermodynamic integration

dhdl-print-energy[¶](#mdp-dhdl-print-energy)

(no)

Include either the total or the potential energy in the dhdl file. Options are ‘no’, ‘potential’, or ‘total’. This information is needed for later free energy analysis if the states of interest are at different temperatures. If all states are at the same temperature, this information is not needed. ‘potential’ is useful in case one is using `mdrun-rerun` to generate the `dhdl.xvg` file. When rerunning from an existing trajectory, the kinetic energy will often not be correct, and thus one must compute the residual free energy from the potential alone, with the kinetic energy component computed analytically.

separate-dhdl-file[¶](#mdp-separate-dhdl-file)yes[¶](#mdp-value-separate-dhdl-file-yes)

The free energy values that are calculated (as specified with [`calc-lambda-neighbors`](#mdp-calc-lambda-neighbors) and [`dhdl-derivatives`](#mdp-dhdl-derivatives) settings) are written out to a separate file, with the default name `dhdl.xvg`. This file can be used directly with [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar).

no[¶](#mdp-value-separate-dhdl-file-no)

The free energy values are written out to the energy output file (`ener.edr`, in accumulated blocks at every [`nstenergy`](#mdp-nstenergy) steps), where they can be extracted with [gmx energy](../onlinehelp/gmx-energy.html#gmx-energy) or used directly with [gmx bar](../onlinehelp/gmx-bar.html#gmx-bar).

dh-hist-size[¶](#mdp-dh-hist-size)

(0) If nonzero, specifies the size of the histogram into which the Delta H values (specified with [`calc-lambda-neighbors`](#mdp-calc-lambda-neighbors)) and the derivative dH/dl values are binned, and written to ener.edr. This can be used to save disk space while calculating free energy differences. One histogram gets written for each foreign lambda and two for the dH/dl, at every [`nstenergy`](#mdp-nstenergy) step. Be aware that incorrect histogram settings (too small size or too wide bins) can introduce errors. Do not use histograms unless you are certain you need it.

dh-hist-spacing[¶](#mdp-dh-hist-spacing)

(0.1) Specifies the bin width of the histograms, in energy units. Used in conjunction with [`dh-hist-size`](#mdp-dh-hist-size). This size limits the accuracy with which free energies can be calculated. Do not use histograms unless you are certain you need it.

### Expanded Ensemble calculations[¶](#expanded-ensemble-calculations)

nstexpanded[¶](#mdp-nstexpanded)

The number of integration steps beween attempted moves changing the system Hamiltonian in expanded ensemble simulations. Must be a multiple of [`nstcalcenergy`](#mdp-nstcalcenergy), but can be greater or less than [`nstdhdl`](#mdp-nstdhdl).

lmc-stats[¶](#mdp-lmc-stats)no[¶](#mdp-value-lmc-stats-no)

No Monte Carlo in state space is performed.

metropolis-transition[¶](#mdp-value-lmc-stats-metropolis-transition)

Uses the Metropolis weights to update the expanded ensemble weight of each state. Min{1,exp(-(beta_new u_new - beta_old u_old)}

barker-transition[¶](#mdp-value-lmc-stats-barker-transition)

Uses the Barker transition critera to update the expanded ensemble weight of each state i, defined by exp(-beta_new u_new)/(exp(-beta_new u_new)+exp(-beta_old u_old))

wang-landau[¶](#mdp-value-lmc-stats-wang-landau)

Uses the Wang-Landau algorithm (in state space, not energy space) to update the expanded ensemble weights.

min-variance[¶](#mdp-value-lmc-stats-min-variance)

Uses the minimum variance updating method of Escobedo et al. to update the expanded ensemble weights. Weights will not be the free energies, but will rather emphasize states that need more sampling to give even uncertainty.

lmc-mc-move[¶](#mdp-lmc-mc-move)no[¶](#mdp-value-lmc-mc-move-no)

No Monte Carlo in state space is performed.

metropolis-transition[¶](#mdp-value-lmc-mc-move-metropolis-transition)

Randomly chooses a new state up or down, then uses the Metropolis criteria to decide whether to accept or reject: Min{1,exp(-(beta_new u_new - beta_old u_old)}

barker-transition[¶](#mdp-value-lmc-mc-move-barker-transition)

Randomly chooses a new state up or down, then uses the Barker transition criteria to decide whether to accept or reject: exp(-beta_new u_new)/(exp(-beta_new u_new)+exp(-beta_old u_old))

gibbs[¶](#mdp-value-lmc-mc-move-gibbs)

Uses the conditional weights of the state given the coordinate (exp(-beta_i u_i) / sum_k exp(beta_i u_i) to decide which state to move to.

metropolized-gibbs[¶](#mdp-value-lmc-mc-move-metropolized-gibbs)

Uses the conditional weights of the state given the coordinate (exp(-beta_i u_i) / sum_k exp(beta_i u_i) to decide which state to move to, EXCLUDING the current state, then uses a rejection step to ensure detailed balance. Always more efficient that Gibbs, though only marginally so in many situations, such as when only the nearest neighbors have decent phase space overlap.

lmc-seed[¶](#mdp-lmc-seed)

(-1) random seed to use for Monte Carlo moves in state space. When [`lmc-seed`](#mdp-lmc-seed) is set to -1, a pseudo random seed is us

mc-temperature[¶](#mdp-mc-temperature)

Temperature used for acceptance/rejection for Monte Carlo moves. If not specified, the temperature of the simulation specified in the first group of [`ref-t`](#mdp-ref-t) is used.

wl-ratio[¶](#mdp-wl-ratio)

(0.8) The cutoff for the histogram of state occupancies to be reset, and the free energy incrementor to be changed from delta to delta * [`wl-scale`](#mdp-wl-scale). If we define the Nratio = (number of samples at each histogram) / (average number of samples at each histogram). [`wl-ratio`](#mdp-wl-ratio) of 0.8 means that means that the histogram is only considered flat if all Nratio &gt; 0.8 AND simultaneously all 1/Nratio &gt; 0.8.

wl-scale[¶](#mdp-wl-scale)

(0.8) Each time the histogram is considered flat, then the current value of the Wang-Landau incrementor for the free energies is multiplied by [`wl-scale`](#mdp-wl-scale). Value must be between 0 and 1.

init-wl-delta[¶](#mdp-init-wl-delta)

(1.0) The initial value of the Wang-Landau incrementor in kT. Some value near 1 kT is usually most efficient, though sometimes a value of 2-3 in units of kT works better if the free energy differences are large.

wl-oneovert[¶](#mdp-wl-oneovert)

(no) Set Wang-Landau incrementor to scale with 1/(simulation time) in the large sample limit. There is significant evidence that the standard Wang-Landau algorithms in state space presented here result in free energies getting ‘burned in’ to incorrect values that depend on the initial state. when [`wl-oneovert`](#mdp-wl-oneovert) is true, then when the incrementor becomes less than 1/N, where N is the number of samples collected (and thus proportional to the data collection time, hence ‘1 over t’), then the Wang-Lambda incrementor is set to 1/N, decreasing every step. Once this occurs, [`wl-ratio`](#mdp-wl-ratio) is ignored, but the weights will still stop updating when the equilibration criteria set in [`lmc-weights-equil`](#mdp-lmc-weights-equil) is achieved.

lmc-repeats[¶](#mdp-lmc-repeats)

(1) Controls the number of times that each Monte Carlo swap type is performed each iteration. In the limit of large numbers of Monte Carlo repeats, then all methods converge to Gibbs sampling. The value will generally not need to be different from 1.

lmc-gibbsdelta[¶](#mdp-lmc-gibbsdelta)

(-1) Limit Gibbs sampling to selected numbers of neighboring states. For Gibbs sampling, it is sometimes inefficient to perform Gibbs sampling over all of the states that are defined. A positive value of [`lmc-gibbsdelta`](#mdp-lmc-gibbsdelta) means that only states plus or minus [`lmc-gibbsdelta`](#mdp-lmc-gibbsdelta) are considered in exchanges up and down. A value of -1 means that all states are considered. For less than 100 states, it is probably not that expensive to include all states.

lmc-forced-nstart[¶](#mdp-lmc-forced-nstart)

(0) Force initial state space sampling to generate weights. In order to come up with reasonable initial weights, this setting allows the simulation to drive from the initial to the final lambda state, with [`lmc-forced-nstart`](#mdp-lmc-forced-nstart) steps at each state before moving on to the next lambda state. If [`lmc-forced-nstart`](#mdp-lmc-forced-nstart) is sufficiently long (thousands of steps, perhaps), then the weights will be close to correct. However, in most cases, it is probably better to simply run the standard weight equilibration algorithms.

nst-transition-matrix[¶](#mdp-nst-transition-matrix)

(-1) Interval of outputting the expanded ensemble transition matrix. A negative number means it will only be printed at the end of the simulation.

symmetrized-transition-matrix[¶](#mdp-symmetrized-transition-matrix)

(no) Whether to symmetrize the empirical transition matrix. In the infinite limit the matrix will be symmetric, but will diverge with statistical noise for short timescales. Forced symmetrization, by using the matrix T_sym = 1/2 (T + transpose(T)), removes problems like the existence of (small magnitude) negative eigenvalues.

mininum-var-min[¶](#mdp-mininum-var-min)

(100) The min-variance strategy (option of [`lmc-stats`](#mdp-lmc-stats) is only valid for larger number of samples, and can get stuck if too few samples are used at each state. [`mininum-var-min`](#mdp-mininum-var-min) is the minimum number of samples that each state that are allowed before the min-variance strategy is activated if selected.

init-lambda-weights[¶](#mdp-init-lambda-weights)

The initial weights (free energies) used for the expanded ensemble states. Default is a vector of zero weights. format is similar to the lambda vector settings in [`fep-lambdas`](#mdp-fep-lambdas), except the weights can be any floating point number. Units are kT. Its length must match the lambda vector lengths.

init-wl-histogram-counts[¶](#mdp-init-wl-histogram-counts)

The initial counts used for the Wang-Landau histogram of visiting expanded ensemble states. The flatness of this histogram is used to decide whether to decrement the histogram-building incrementor. This option is only generally useful if continuing a shorter simulation from a previous one, as the smaller the incrementor gets, the longer it takes for the histogram to become flat, often longer than a short simulation takes, requiring the histogram population to be carried over from the previous simulation. The default is a vector of zeros. The format is similar to the lambda vector settings in [`fep-lambdas`](#mdp-fep-lambdas). The value can be a floating point number or an integer, as some methods increment multiple histogram bins at the same time with fractional weights. Its length must match the lambda vector lengths.

init-lambda-counts[¶](#mdp-init-lambda-counts)

The initial counts used for the number of times each expanded ensemble state is visited states. Several algorithms set by [`lmc-weights-equil`](#mdp-lmc-weights-equil) use various functions of the number of visits to each state states to decide whether to switch to different phases of weight determination. These include `number-all-lambda` which requires the mumber of times each lambda state is visited to be equal to or greater than this number, `number-samples`, which requires the total number of visits to all lambda states to be greater than or equal to this, and `count-ratio`, which requires the number of states visited at each state to be within a given ratio of equal visitation. This option is only generally useful if continuing a shorter simulation from a previous one, as most methods will reach the triggering conditions with relatively low number of samples collected. The default is a vector of zeros. The format is similar to the lambda vector settings in [`fep-lambdas`](#mdp-fep-lambdas). Unlike `init-wl-histogram`, the value can only be an integer. Its length must match the lambda vector lengths.

lmc-weights-equil[¶](#mdp-lmc-weights-equil)no[¶](#mdp-value-lmc-weights-equil-no)

Expanded ensemble weights continue to be updated throughout the simulation.

yes[¶](#mdp-value-lmc-weights-equil-yes)

The input expanded ensemble weights are treated as equilibrated, and are not updated throughout the simulation.

wl-delta[¶](#mdp-value-lmc-weights-equil-wl-delta)

Expanded ensemble weight updating is stopped when the Wang-Landau incrementor falls below this value.

number-all-lambda[¶](#mdp-value-lmc-weights-equil-number-all-lambda)

Expanded ensemble weight updating is stopped when the number of samples at all of the lambda states is greater than this value.

number-steps[¶](#mdp-value-lmc-weights-equil-number-steps)

Expanded ensemble weight updating is stopped when the number of steps is greater than the level specified by this value.

number-samples[¶](#mdp-value-lmc-weights-equil-number-samples)

Expanded ensemble weight updating is stopped when the number of total samples across all lambda states is greater than the level specified by this value.

count-ratio[¶](#mdp-value-lmc-weights-equil-count-ratio)

Expanded ensemble weight updating is stopped when the ratio of samples at the least sampled lambda state and most sampled lambda state greater than this value.

simulated-tempering[¶](#mdp-simulated-tempering)

(no) Turn simulated tempering on or off. Simulated tempering is implemented as expanded ensemble sampling with different temperatures instead of different Hamiltonians.

sim-temp-low[¶](#mdp-sim-temp-low)

(300) [K] Low temperature for simulated tempering.

sim-temp-high[¶](#mdp-sim-temp-high)

(300) [K] High temperature for simulated tempering.

simulated-tempering-scaling[¶](#mdp-simulated-tempering-scaling)

Controls the way that the temperatures at intermediate lambdas are calculated from the [`temperature-lambdas`](#mdp-temperature-lambdas) part of the lambda vector.

linear[¶](#mdp-value-simulated-tempering-scaling-linear)

Linearly interpolates the temperatures using the values of [`temperature-lambdas`](#mdp-temperature-lambdas), *i.e.* if [`sim-temp-low`](#mdp-sim-temp-low) =300, [`sim-temp-high`](#mdp-sim-temp-high) =400, then lambda=0.5 correspond to a temperature of 350. A nonlinear set of temperatures can always be implemented with uneven spacing in lambda.

geometric[¶](#mdp-value-simulated-tempering-scaling-geometric)

Interpolates temperatures geometrically between [`sim-temp-low`](#mdp-sim-temp-low) and [`sim-temp-high`](#mdp-sim-temp-high). The i:th state has temperature [`sim-temp-low`](#mdp-sim-temp-low) * ([`sim-temp-high`](#mdp-sim-temp-high) / [`sim-temp-low`](#mdp-sim-temp-low)) raised to the power of (i/(ntemps-1)). This should give roughly equal exchange for constant heat capacity, though of course things simulations that involve protein folding have very high heat capacity peaks.

exponential[¶](#mdp-value-simulated-tempering-scaling-exponential)

Interpolates temperatures exponentially between [`sim-temp-low`](#mdp-sim-temp-low) and [`sim-temp-high`](#mdp-sim-temp-high). The i:th state has temperature [`sim-temp-low`](#mdp-sim-temp-low) + ([`sim-temp-high`](#mdp-sim-temp-high) - [`sim-temp-low`](#mdp-sim-temp-low))*((exp([`temperature-lambdas`](#mdp-temperature-lambdas) (i))-1)/(exp(1.0)-i)).

### Non-equilibrium MD[¶](#non-equilibrium-md)

acc-grps[¶](#mdp-acc-grps)

groups for constant acceleration (*e.g.*`ProteinSol`) all atoms in groups Protein and Sol will experience constant acceleration as specified in the [`accelerate`](#mdp-accelerate) line. Note that the kinetic energy of the center of mass of accelerated groups contributes to the kinetic energy and temperature of the system. If this is not desired, make each accelerate group also a separate temperature coupling group.

accelerate[¶](#mdp-accelerate)

(0) [nm ps<sup>-2</sup>] acceleration for [`acc-grps`](#mdp-acc-grps); x, y and z for each group (*e.g.*`0.10.00.0-0.10.00.0` means that first group has constant acceleration of 0.1 nm ps<sup>-2</sup> in X direction, second group the opposite).

freezegrps[¶](#mdp-freezegrps)

Groups that are to be frozen (*i.e.* their X, Y, and/or Z position will not be updated; *e.g.*`LipidSOL`). [`freezedim`](#mdp-freezedim) specifies for which dimension(s) the freezing applies. Note that the virial and pressure are usually not meaningful when frozen atoms are present. Note that coordinates of frozen atoms are not scaled by pressure-coupling algorithms.

freezedim[¶](#mdp-freezedim)

dimensions for which groups in [`freezegrps`](#mdp-freezegrps) should be frozen, specify `Y` or `N` for X, Y and Z and for each group (*e.g.*`YYNNNN` means that particles in the first group can move only in Z direction. The particles in the second group can move in any direction).

cos-acceleration[¶](#mdp-cos-acceleration)

(0) [nm ps<sup>-2</sup>] the amplitude of the acceleration profile for calculating the viscosity. The acceleration is in the X-direction and the magnitude is [`cos-acceleration`](#mdp-cos-acceleration) cos(2 pi z/boxheight). Two terms are added to the energy file: the amplitude of the velocity profile and 1/viscosity.

deform[¶](#mdp-deform)

(0 0 0 0 0 0) [nm ps<sup>-1</sup>] The velocities of deformation for the box elements: a(x) b(y) c(z) b(x) c(x) c(y). Each step the box elements for which [`deform`](#mdp-deform) is non-zero are calculated as: box(ts)+(t-ts)*deform, off-diagonal elements are corrected for periodicity. The time ts is set to t at the first step and at steps at which x and v are written to trajectory to ensure exact restarts. Deformation can be used together with semiisotropic or anisotropic pressure coupling when the appropriate compressibilities are set to zero. The diagonal elements can be used to strain a solid. The off-diagonal elements can be used to shear a solid or a liquid. Note that the atom positions are not affected directly by this option. Instead, the deform option only modifies the velocities of particles that are shifted by a periodic box vector such that their new velocities match the virtual velocity flow field corresponding to the box deformation. As the deform option never accelerates the remaining particles in the system, the matching velocity flow field should be set up at the beginning of the simulation to make the particles follow the deformation. This can be done with the [`deform-init-flow`](#mdp-deform-init-flow) option. The flow field is removed from the kinetic energy by [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) so the actual temperature and pressure of the system are reported.

deform-init-flow[¶](#mdp-deform-init-flow)no[¶](#mdp-value-deform-init-flow-no)

Do not modify the velocities. Only use this option when the velocities of the atoms in the initial configuration already obey the flow field.

yes[¶](#mdp-value-deform-init-flow-yes)

When the [`deform`](#mdp-deform) option is active, add a velocity profile corresponding to the box deformation to the initial velocities. This is done after computing observables from the initial state such as the initial temperature.

### Electric fields[¶](#electric-fields)

electric-field-x[¶](#mdp-electric-field-x)electric-field-y[¶](#mdp-electric-field-y)electric-field-z[¶](#mdp-electric-field-z)

Here you can specify an electric field that optionally can be alternating and pulsed. The general expression for the field has the form of a gaussian laser pulse:

 $$E(t) = E_0 \exp\left[-\frac{(t-t_0)^2}{2\sigma^2}\right]\cos\left[\omega (t-t_0)\right]$$

For example, the four parameters for direction x are set in the fields of [`electric-field-x`](#mdp-electric-field-x) (and similar for `electric-field-y` and `electric-field-z`) like

`electric-field-x=E0omegat0sigma`

with units (respectively) V nm<sup>-1</sup>, ps<sup>-1</sup>, ps, ps.

In the special case that `sigma=0`, the exponential term is omitted and only the cosine term is used. In this case, `t0` must be set to 0. If also `omega=0` a static electric field is applied.

Read more at [Electric fields](../reference-manual/special/electric-fields.html#electric-fields) and in ref. [146](../reference-manual/references.html#refcaleman2008a).

### Mixed quantum/classical molecular dynamics[¶](#mixed-quantum-classical-molecular-dynamics)

QMMM-grps[¶](#mdp-QMMM-grps)

groups to be described at the QM level for MiMiC QM/MM

QMMM[¶](#mdp-QMMM)no[¶](#mdp-value-QMMM-no)

QM/MM is no longer supported via these .mdp options. For MiMic, use no here.

### Computational Electrophysiology[¶](#computational-electrophysiology)

Use these options to switch on and control ion/water position exchanges in “Computational Electrophysiology” simulation setups. (See the [reference manual](../manual-2026.4.pdf) for details).

swapcoords[¶](#mdp-swapcoords)no[¶](#mdp-value-swapcoords-no)

Do not enable ion/water position exchanges.

X;Y;Z[¶](#mdp-value-swapcoords-X-Y-Z)

Allow for ion/water position exchanges along the chosen direction. In a typical setup with the membranes parallel to the x-y plane, ion/water pairs need to be exchanged in Z direction to sustain the requested ion concentrations in the compartments.

swap-frequency[¶](#mdp-swap-frequency)

(1) The swap attempt frequency, i.e. every how many time steps the ion counts per compartment are determined and exchanges made if necessary. Normally, it is not necessary to check at every time step. For typical Computational Electrophysiology setups, a value of about 100 is sufficient and yields a negligible performance impact.

split-group0[¶](#mdp-split-group0)

Name of the index group of the membrane-embedded part of channel #0. The center of mass of these atoms defines one of the compartment boundaries and should be chosen such that it is near the center of the membrane.

split-group1[¶](#mdp-split-group1)

Defines the position of the other compartment boundary.

massw-split0[¶](#mdp-massw-split0)

(no) Defines whether or not mass-weighting is used to calculate the split group center.

no[¶](#mdp-value-massw-split0-no)

Use the geometrical center.

yes[¶](#mdp-value-massw-split0-yes)

Use the center of mass.

massw-split1[¶](#mdp-massw-split1)

(no) As above, but for [`split-group1`](#mdp-split-group1).

solvent-group[¶](#mdp-solvent-group)

Name of the index group of solvent molecules.

coupl-steps[¶](#mdp-coupl-steps)

(10) Average the number of ions per compartment over these many swap attempt steps. This can be used to prevent that ions near a compartment boundary (diffusing through a channel, e.g.) lead to unwanted back and forth swaps.

iontypes[¶](#mdp-iontypes)

(1) The number of different ion types to be controlled. These are during the simulation exchanged with solvent molecules to reach the desired reference numbers.

iontype0-name[¶](#mdp-iontype0-name)

Name of the first ion type.

iontype0-in-A[¶](#mdp-iontype0-in-A)

(-1) Requested (=reference) number of ions of type 0 in compartment A. The default value of -1 means: use the number of ions as found in time step 0 as reference value.

iontype0-in-B[¶](#mdp-iontype0-in-B)

(-1) Reference number of ions of type 0 for compartment B.

bulk-offsetA[¶](#mdp-bulk-offsetA)

(0.0) Offset of the first swap layer from the compartment A midplane. By default (i.e. bulk offset = 0.0), ion/water exchanges happen between layers at maximum distance (= bulk concentration) to the split group layers. However, an offset b (-1.0 &lt; b &lt; +1.0) can be specified to offset the bulk layer from the middle at 0.0 towards one of the compartment-partitioning layers (at +/- 1.0).

bulk-offsetB[¶](#mdp-bulk-offsetB)

(0.0) Offset of the other swap layer from the compartment B midplane.

threshold[¶](#mdp-threshold)

(1) Only swap ions if threshold difference to requested count is reached.

cyl0-r[¶](#mdp-cyl0-r)

(2.0) [nm] Radius of the split cylinder #0. Two split cylinders (mimicking the channel pores) can optionally be defined relative to the center of the split group. With the help of these cylinders it can be counted which ions have passed which channel. The split cylinder definition has no impact on whether or not ion/water swaps are done.

cyl0-up[¶](#mdp-cyl0-up)

(1.0) [nm] Upper extension of the split cylinder #0.

cyl0-down[¶](#mdp-cyl0-down)

(1.0) [nm] Lower extension of the split cylinder #0.

cyl1-r[¶](#mdp-cyl1-r)

(2.0) [nm] Radius of the split cylinder #1.

cyl1-up[¶](#mdp-cyl1-up)

(1.0) [nm] Upper extension of the split cylinder #1.

cyl1-down[¶](#mdp-cyl1-down)

(1.0) [nm] Lower extension of the split cylinder #1.

### Density-guided simulations[¶](#density-guided-simulations)

These options enable and control the calculation and application of additional forces that are derived from three-dimensional densities, e.g., from cryo electron-microscopy experiments. (See the [reference manual](../manual-2026.4.pdf) for details)

density-guided-simulation-active[¶](#mdp-density-guided-simulation-active)

(no) Activate density-guided simulations.

density-guided-simulation-group[¶](#mdp-density-guided-simulation-group)

(protein) The atoms that are subject to the forces from the density-guided simulation and contribute to the simulated density.

density-guided-simulation-similarity-measure[¶](#mdp-density-guided-simulation-similarity-measure)

(inner-product) Similarity measure between the density that is calculated from the atom positions and the reference density.

inner-product[¶](#mdp-value-density-guided-simulation-similarity-measure-inner-product)

Takes the sum of the product of reference density and simulated density voxel values.

relative-entropy[¶](#mdp-value-density-guided-simulation-similarity-measure-relative-entropy)

Uses the negative relative entropy (or Kullback-Leibler divergence) between reference density and simulated density as similarity measure. Negative density values are ignored.

cross-correlation[¶](#mdp-value-density-guided-simulation-similarity-measure-cross-correlation)

Uses the Pearson correlation coefficient between reference density and simulated density as similarity measure.

density-guided-simulation-atom-spreading-weight[¶](#mdp-density-guided-simulation-atom-spreading-weight)

(unity) Determines the multiplication factor for the Gaussian kernel when spreading atoms on the grid.

unity[¶](#mdp-value-density-guided-simulation-atom-spreading-weight-unity)

Every atom in the density fitting group is assigned the same unit factor.

mass[¶](#mdp-value-density-guided-simulation-atom-spreading-weight-mass)

Atoms contribute to the simulated density proportional to their mass.

charge[¶](#mdp-value-density-guided-simulation-atom-spreading-weight-charge)

Atoms contribute to the simulated density proportional to their charge.

density-guided-simulation-force-constant[¶](#mdp-density-guided-simulation-force-constant)

(1e+09) [kJ mol<sup>-1</sup>] The scaling factor for density-guided simulation forces. May also be negative.

density-guided-simulation-gaussian-transform-spreading-width[¶](#mdp-density-guided-simulation-gaussian-transform-spreading-width)

(0.2) [nm] The Gaussian RMS width for the spread kernel for the simulated density.

density-guided-simulation-gaussian-transform-spreading-range-in-multiples-of-width[¶](#mdp-density-guided-simulation-gaussian-transform-spreading-range-in-multiples-of-width)

(4) The range after which the gaussian is cut off in multiples of the Gaussian RMS width described above.

density-guided-simulation-reference-density-filename[¶](#mdp-density-guided-simulation-reference-density-filename)

(reference.mrc) Reference density file name using an absolute path or a path relative to the to the folder from which [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) is called.

density-guided-simulation-nst[¶](#mdp-density-guided-simulation-nst)

(1) Interval in steps at which the density fitting forces are evaluated and applied. The forces are scaled by this number when applied (See the [reference manual](../manual-2026.4.pdf) for details).

density-guided-simulation-normalize-densities[¶](#mdp-density-guided-simulation-normalize-densities)

(true) Normalize the sum of density voxel values to one for the reference density as well as the simulated density.

density-guided-simulation-adaptive-force-scaling[¶](#mdp-density-guided-simulation-adaptive-force-scaling)

(false) Adapt the force constant to ensure a steady increase in similarity between simulated and reference density.

true[¶](#mdp-value-density-guided-simulation-adaptive-force-scaling-true)

Use adaptive force scaling.

density-guided-simulation-adaptive-force-scaling-time-constant[¶](#mdp-density-guided-simulation-adaptive-force-scaling-time-constant)

(4) [ps] Couple force constant to increase in similarity with reference density with this time constant. Larger times result in looser coupling.

density-guided-simulation-shift-vector[¶](#mdp-density-guided-simulation-shift-vector)

(0,0,0) [nm] Add this vector to all atoms in the density-guided-simulation-group before calculating forces and energies for density-guided simulations. Affects only the density-guided simulation forces and energies. Corresponds to a shift of the input density in the opposite direction by (-1) * density-guided-simulation-shift-vector.

density-guided-simulation-transformation-matrix[¶](#mdp-density-guided-simulation-transformation-matrix)

(1,0,0,0,1,0,0,0,1) Multiply all atoms with this matrix in the density-guided-simulation-group before calculating forces and energies for density-guided simulations. Affects only the density-guided simulation forces and energies. Corresponds to a transformation of the input density by the inverse of this matrix. The matrix is given in row-major order. This option allows, e.g., rotation of the density-guided atom group around the z-axis by $\theta$ degrees by using the following input: $(\cos \theta , -\sin \theta , 0 , \sin \theta , \cos \theta , 0 , 0 , 0 , 1)$ .

### QM/MM simulations with CP2K Interface[¶](#qm-mm-simulations-with-cp2k-interface)

These options enable and control the calculation and application of additional QM/MM forces that are computed by the CP2K package if it is linked into GROMACS. For further details about QM/MM interface implementation follow [Hybrid Quantum-Classical simulations (QM/MM) with CP2K interface](../reference-manual/special/qmmm.html#qmmm).

qmmm-cp2k-active[¶](#mdp-qmmm-cp2k-active)

(false) Activate QM/MM simulations. Requires CP2K to be linked with GROMACS

qmmm-cp2k-qmgroup[¶](#mdp-qmmm-cp2k-qmgroup)

(System) Index group with atoms that are treated with QM.

qmmm-cp2k-qmmethod[¶](#mdp-qmmm-cp2k-qmmethod)

(PBE) Method used to describe the QM part of the system.

PBE[¶](#mdp-value-qmmm-cp2k-qmmethod-PBE)

DFT using PBE functional and DZVP-MOLOPT basis set.

PBE-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-PBE-D3)

DFT using PBE functional, DZVP-MOLOPT basis set and D3 dispersion correction.

BLYP[¶](#mdp-value-qmmm-cp2k-qmmethod-BLYP)

DFT using BLYP functional and DZVP-MOLOPT basis set.

BLYP-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-BLYP-D3)

DFT using BLYP functional, DZVP-MOLOPT basis set and D3 dispersion correction.

B3LYP[¶](#mdp-value-qmmm-cp2k-qmmethod-B3LYP)

DFT using B3LYP hybrid functional and 6-31G* basis set.

B3LYP-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-B3LYP-D3)

DFT using B3LYP hybrid functional, 6-31G* basis set and D3 dispersion correction.

PBE0[¶](#mdp-value-qmmm-cp2k-qmmethod-PBE0)

DFT using PBE0 hybrid functional and 6-31G* basis set.

PBE0-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-PBE0-D3)

DFT using PBE0 hybrid functional, 6-31G* basis set and D3 dispersion correction.

CAM-B3LYP[¶](#mdp-value-qmmm-cp2k-qmmethod-CAM-B3LYP)

DFT using CAM-B3LYP range-separated functional and 6-31G* basis set.

CAM-B3LYP-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-CAM-B3LYP-D3)

DFT using CAM-B3LYP range-separated functional, 6-31G* basis set and D3 dispersion correction.

WB97X[¶](#mdp-value-qmmm-cp2k-qmmethod-WB97X)

DFT using wB97X range-separated functional and 6-31G* basis set.

WB97X-D3[¶](#mdp-value-qmmm-cp2k-qmmethod-WB97X-D3)

DFT using wB97X-D3 range-separated functional with built-in D3 dispersion correction and 6-31G* basis set.

INPUT[¶](#mdp-value-qmmm-cp2k-qmmethod-INPUT)

Provide an external input file for CP2K when running [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) with the `-qmi` command-line option. External input files are subject to the limitations that are described in [Hybrid Quantum-Classical simulations (QM/MM) with CP2K interface](../reference-manual/special/qmmm.html#qmmm).

qmmm-cp2k-qmcharge[¶](#mdp-qmmm-cp2k-qmcharge)

1. Total charge of the QM part.

qmmm-cp2k-qmmultiplicity[¶](#mdp-qmmm-cp2k-qmmultiplicity)

1. Multiplicity or spin-state of QM part. Default value 1 means singlet state.

qmmm-cp2k-qmfilenames[¶](#mdp-qmmm-cp2k-qmfilenames)

() Names of the CP2K files that will be generated during the simulation. When using the default, empty, value the name of the simulation input file will be used with an additional `_cp2k` suffix.

### Collective variables (Colvars) module[¶](#collective-variables-colvars-module)

These options enable and control the features provided by the collective variables ([Colvars](https://colvars.github.io/)) module, a software library for enhanced sampling methods in molecular simulations. The Colvars module is described in ref. [195](../reference-manual/references.html#reffiorin13) as well as other references that are reported in the log file when the corresponding features are used. For further details about Colvars interface implementation follow [Collective Variable simulations with the Colvars module](../reference-manual/special/colvars.html#colvars).

colvars-active[¶](#mdp-colvars-active)

(false) Activate Colvars computation in the current run. Requires that the Colvars library was compiled with GROMACS, which is the default in a typical installation.

colvars-configfile[¶](#mdp-colvars-configfile)

Name of the Colvars configuration file, using options specific to Colvars that are documented at: [https://colvars.github.io/gromacs-2026/colvars-refman-gromacs.html](https://colvars.github.io/gromacs-2026/colvars-refman-gromacs.html). The file name can be either an absolute path, or a path relative to the working directory when [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) is called.

colvars-seed[¶](#mdp-colvars-seed)

(-1) [integer] Seed used to initialize the random generator associated with certain stochastic methods implemented within Colvars. The default value of -1 generates a random seed.

The current implementation of the Colvars-GROMACS interface gathers the relevant atomic coordinates on one MPI rank, where all collective variables and their forces are computed. Take this fact into account when choosing how many atoms to include in selections.

### NNP/MM simulations with neural network potentials in the NNPot interface[¶](#nnp-mm-simulations-with-neural-network-potentials-in-the-nnpot-interface)

These options enable and control the calculation and application of additional forces derived from neural network potentials via the nnpot interface, if GROMACS is built with LibTorch support. For further details about NNP/MM interface implementation follow [Neural Network Potentials](../reference-manual/special/nnpot.html#nnpot).

nnpot-active[¶](#mdp-nnpot-active)

(false) Activate NNP/MM simulations via the NNPot interface. Requires GROMACS to be built with LibTorch support.

nnpot-modelfile[¶](#mdp-nnpot-modelfile)

(model.pt) Path to a TorchScript-compiled model, either absolute or relative to the simulation directory.

nnpot-input-group[¶](#mdp-nnpot-input-group)

(System) Index group defining the input atoms for the NNP subsystem. Defaults to `System`, which performs a pure NNP simulation.

nnpot-embedding[¶](#mdp-nnpot-embedding)

(mechanical) Type of embedding scheme to use for NNP/MM simulations.

mechanical[¶](#mdp-value-nnpot-embedding-mechanical)

Mechanical embedding scheme, NNP-MM interactions are treated classically.

electrostatic-model[¶](#mdp-value-nnpot-embedding-electrostatic-model)

Electrostatic embedding scheme, NNP-MM interactions are computed by the NNP model. In this case, the NNP model is expected to return the total energy, as well as forces on NNP and MM atoms.

nnpot-model-input[1-9][¶](#mdp-nnpot-model-input-1-9)

Names of input fields to be filled in by GROMACS at each step and passed to the NNP model. Up to 9 inputs can be specified:

atom-positions[¶](#mdp-value-nnpot-model-input-1-9-atom-positions)

Positions of the NNP atoms specified by [`nnpot-input-group`](#mdp-nnpot-input-group).

atom-numbers[¶](#mdp-value-nnpot-model-input-1-9-atom-numbers)

Atomic numbers of the NNP atoms specified by [`nnpot-input-group`](#mdp-nnpot-input-group).

atom-pairs[¶](#mdp-value-nnpot-model-input-1-9-atom-pairs)

Pairs of NNP atoms specified by [`nnpot-input-group`](#mdp-nnpot-input-group), filter by the [`pair-cutoff`](#mdp-pair-cutoff), as a vector of shape (N_pairs, 2).

pair-shifts[¶](#mdp-value-nnpot-model-input-1-9-pair-shifts)

Periodic box shift vectors for the NNP atom pairs, as a vector of shape (N_pairs, 3).

atom-positions-mm[¶](#mdp-value-nnpot-model-input-1-9-atom-positions-mm)

Positions of the MM atoms surrounding the NNP region, needed for `electrostatic-model` embedding.

atom-charges-mm[¶](#mdp-value-nnpot-model-input-1-9-atom-charges-mm)

Charges of the MM atoms surrounding the NNP region, needed for `electrostatic-model` embedding.

nnp-charge[¶](#mdp-value-nnpot-model-input-1-9-nnp-charge)

Total charge of the NNP atoms.

box[¶](#mdp-value-nnpot-model-input-1-9-box)

Simulation box vectors.

pbc[¶](#mdp-value-nnpot-model-input-1-9-pbc)

Periodic boundary conditions.

pair-cutoff[¶](#mdp-pair-cutoff)

(0.0) [nm] Cutoff distance for pairs of NNP atoms. Positive cutoff value must be specified when requesting `atom-pairs` input.

nnpot-link-type[¶](#mdp-nnpot-link-type)

(H) Type of link atoms to be used in the NNP/MM simulation, specified by element symbol. Defaults to hydrogen (H).

nnpot-link-distance[¶](#mdp-nnpot-link-distance)

(0.1) [nm] Distance between link atom and the bonded MM atom.

### Fast Multipole Method (FMM) Interface[¶](#fast-multipole-method-fmm-interface)

These options enable an FMM backend and control its settings. For further details about the FMM interface implementation follow [Fast Multipole Method (FMM)](../reference-manual/special/fmm.html#fmm).

fmm-backend[¶](#mdp-fmm-backend)

(inactive) Activate an FMM library for electrostatics.

inactive[¶](#mdp-value-fmm-backend-inactive)

No FMM library is used.

exafmm[¶](#mdp-value-fmm-backend-exafmm)

Use ExaFMM as FMM library.

fmsolvr[¶](#mdp-value-fmm-backend-fmsolvr)

Use FMSolvr as FMM library.

#### Options controlling ExaFmm[¶](#options-controlling-exafmm)

fmm-exafmm-direct-provider[¶](#mdp-fmm-exafmm-direct-provider)

(GROMACS) Selects direct interaction provider.

GROMACS[¶](#mdp-value-fmm-exafmm-direct-provider-GROMACS)

Use GROMACS to compute direct interactions.

FMM[¶](#mdp-value-fmm-exafmm-direct-provider-FMM)

Use ExaFMM to compute direct interactions.

fmm-exafmm-direct-range[¶](#mdp-fmm-exafmm-direct-range)

(2) Specifies whether ExaFMM includes only immediate or also second-nearest neighboring cells in direct interactions. Accepts `1` or `2`. Must be `2` when using GROMACS as direct provider.

fmm-exafmm-order[¶](#mdp-fmm-exafmm-order)

1. Multipole expansion order. Must be greater than `0`.

fmm-exafmm-tree-type[¶](#mdp-fmm-exafmm-tree-type)

(uniform) Tree structure used by ExaFMM.

uniform[¶](#mdp-value-fmm-exafmm-tree-type-uniform)

Use uniform tree structure.

adaptive[¶](#mdp-value-fmm-exafmm-tree-type-adaptive)

Use adaptive tree structure.

fmm-exafmm-tree-depth[¶](#mdp-fmm-exafmm-tree-depth)

(0) Tree depth for uniform tree. Required when using `FMM` as direct provider. Must not be set for adaptive tree.

fmm-exafmm-max-particles-per-cell[¶](#mdp-fmm-exafmm-max-particles-per-cell)

(0) Maximum particles per cell for adaptive tree. Required and positive when `fmm-exafmm-tree-type=adaptive`. Must not be set for uniform tree.

#### Options controlling FMSolvr[¶](#options-controlling-fmsolvr)

fmm-fmsolvr-order[¶](#mdp-fmm-fmsolvr-order)

1. Multipole expansion order. Must be greater than `0`.

fmm-fmsolvr-tree-depth[¶](#mdp-fmm-fmsolvr-tree-depth)

1. Tree depth controlling spatial subdivision.

fmm-fmsolvr-direct-provider[¶](#mdp-fmm-fmsolvr-direct-provider)

(FMM) Selects direct interaction provider.

GROMACS[¶](#mdp-value-fmm-fmsolvr-direct-provider-GROMACS)

Use GROMACS to compute direct interactions.

FMM[¶](#mdp-value-fmm-fmsolvr-direct-provider-FMM)

Use FMSolvr to compute direct interactions.

fmm-fmsolvr-direct-range[¶](#mdp-fmm-fmsolvr-direct-range)

1. Direct interaction settings. Must be `1`, as FMSolvr currently supports direct interactions only with immediate neighboring cells.

fmm-fmsolvr-dipole-compensation[¶](#mdp-fmm-fmsolvr-dipole-compensation)

(yes) Enables dipole compensation.

fmm-fmsolvr-sparse[¶](#mdp-fmm-fmsolvr-sparse)

(no) Enable performance optimizations for sparse simulation systems with a lot of vacuum.

### User defined thingies[¶](#user-defined-thingies)

user1-grps[¶](#mdp-user1-grps)user2-grps[¶](#mdp-user2-grps)userint1(0)[¶](#mdp-userint1-0)userint2(0)[¶](#mdp-userint2-0)userint3(0)[¶](#mdp-userint3-0)userint4(0)[¶](#mdp-userint4-0)userreal1(0)[¶](#mdp-userreal1-0)userreal2(0)[¶](#mdp-userreal2-0)userreal3(0)[¶](#mdp-userreal3-0)userreal4(0)[¶](#mdp-userreal4-0)

These you can use if you modify code. You can pass integers and reals and groups to your subroutine. Check the inputrec definition in `src/gromacs/mdtypes/inputrec.h`

### Removed features[¶](#removed-features)

These features have been removed from GROMACS, but so that old [mdp](../reference-manual/file-formats.html#mdp) and [tpr](../reference-manual/file-formats.html#tpr) files cannot be mistakenly misused, we still parse these options. [gmx grompp](../onlinehelp/gmx-grompp.html#gmx-grompp) and [gmx mdrun](../onlinehelp/gmx-mdrun.html#gmx-mdrun) will issue a fatal error if they are set.

adress[¶](#mdp-adress)

(no)

implicit-solvent[¶](#mdp-implicit-solvent)

(no)
