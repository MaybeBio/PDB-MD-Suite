# Applying distance constraints to ligand and Mg ion

> GROMACS version: 2020.2  GROMACS modification: No  Hello,  I am simulating a protein dimer with a ligand and an Mg ion in its active site. I want to apply a distance constraint on the Mg ion and an oxygen of the ligand in order to keep them 0.2 nm from each other. I was wondering, what is the best method to do this?  So far, I have made an index group containing the ligand oxygen and the Mg ion (with other atoms in between). I then used this index group in ‘gmx genrestr’ with the added option “-...

[User discussions](https://gromacs.bioexcel.eu/c/gromacs-user-forum/5)[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 20, 2020, 1:57pm 1

GROMACS version: 2020.2

 GROMACS modification: No

Hello,

I am simulating a protein dimer with a ligand and an Mg ion in its active site. I want to apply a distance constraint on the Mg ion and an oxygen of the ligand in order to keep them 0.2 nm from each other. I was wondering, what is the best method to do this?

So far, I have made an index group containing the ligand oxygen and the Mg ion (with other atoms in between). I then used this index group in ‘gmx genrestr’ with the added option “-disre_dist 0.2”. I then copied the line from the produced .itp file containing the ligand oxygen and Mg ion from the produced itp file into the very end of my original topol.top file underneath [intermolecular-interactions]. The end of my topol.top looks like this:

[ intermolecular-interactions ]

 [ distance_restraints ]

 ; i j ? label funct lo up1 up2 weight

 10900 10908 1 0 1 0.107085 0.507085 1.50708 1

Unfortunately, after running a 10-ns simulation, the ligand oxygen and Mg ion appeared to still be farther than 0.2 nm apart and the distance restraint was not in place.

I realized that I did not add any distance restraint options to my .mdp file, so I tried the simulation again with the following added to the md.mdp file:

disre = simple

 disre-weighting = equal

 disre-mixed = no

 disre-fc = 1000

 disre-tau = 0

However, this did not seem to affect anything and the Mg-ligand oxygen distance was still farther than 0.2 nm. I am not sure what to try next, or perhaps I should be using a different method.

Any help or advice would be greatly appreciated!

Josh

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 20, 2020, 3:12pm 2

Use a harmonic biasing potential via the pull code. With a zero pull rate, it will achieve what you want very simply.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 20, 2020, 4:27pm 3

Thank you, Dr. Lemkul!

Should I keep the distance restraints and added mdp options from my initial post while using the pull code? Or would they be unnecessary?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 20, 2020, 5:10pm 4

Use one or the other. Your distance restraints allow for a wide range of variation and will not necessarily keep the distance at 0.2 nm. You could amend it, but I think the use of a simple biasing potential via the pull code is much cleaner and straightforward.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 20, 2020, 6:40pm 5

I see, thank you.

Do you think that these pull code options in my md.mdp would suffice? The Mg ion is a_10900 and the ligand oxygen is a_10908.

; Pull code

 pull = yes

 pull-ngroups = 2

 pull-ncoords = 1

 pull-group1-name = a_10908

 pull-group2-name = a_10900

 pull-coord1-type = umbrella

 pull-coord1-geometry = distance ; simple distance increase

 pull-coord1-groups = 1 2

 pull-coord1-dim = Y Y Y

 pull-coord1-rate = 0.0 ; not pull, just distance restraint at a reference

 distance bw 2 groups

 pull-coord1-k = 1000 ; kJ mol^-1 nm^-2

 pull-coord1-start = yes ; define initial COM distance &gt; 0

 pull-nstxout = 5000

 pull-nstfout = 5000

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 21, 2020, 1:32am 6![](https://avatars.discourse-cdn.com/v4/letter/j/aeb1de/48.png) joshhayden:> pull-coord1-start = yes ; define initial COM distance &gt; 0

If the initial distance between the two atoms is 0.2 nm, this is fine.

![](https://avatars.discourse-cdn.com/v4/letter/j/aeb1de/48.png) joshhayden:> pull-nstxout = 5000
>  pull-nstfout = 5000

You only need this output for umbrella sampling, so you can set both to zero.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 21, 2020, 2:34am 7

I have noticed that from my past simulations, my npt.gro file shows the distance between the two atoms to be around 0.2 nm. However, the starting coordinates of my final md simulation always have the atoms much farther apart.

In that case, should I change the “pull-coord1-start” line?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 21, 2020, 9:38am 8

If the coordinates you provide to `grompp` have the desired atoms separated by 0.2 nm, you can use `pull-coord1-start = yes`, otherwise you should set `pull-coord1-init = 0.2`.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 22, 2020, 3:53am 9

I decided to use “pull-coord-init = 0.2” and ran a 10-ns simulation. After visualizing the simulation, I could see that the distance constraint was in place for the first half of the simulation. However, the atom distance exceeded 0.2 nm during the second half of the simulation.

Is there a way to ensure the pull code stays in place during the entire duration of the simulation?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 22, 2020, 12:07pm 10

Something else is going on; `mdrun` doesn’t suddenly forget that a restraint should be applied. Check the magnitude of the energy contribution from the pull restraint, make sure you’re properly accounting for PBC, etc.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 23, 2020, 3:13pm 11

Everything is fine with the periodic boundary condtions. And in the pull code, I have “pull-coord1-k = 1000 ; kJ mol^-1 nm^-2”. Is this the energy contribution you are referring to?

I analyzed the distance between the atoms against time using ‘gmx distance’ and found that they never get as close as 0.2 nm apart. For the first 4 ns they are about 0.3 nm apart, and for the last 6 ns they are closer to 0.38 nm apart. However, this is still much closer than any of my previous simulations, leading me to believe that the pull restraint is still in place to some extent.

Is there possibly a way to increase the strength of the pull restraint to ensure the distance stays closer to 0.2 nm?

Thank you for all of your help so far!

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 24, 2020, 10:14am 12![](https://avatars.discourse-cdn.com/v4/letter/j/aeb1de/48.png) joshhayden:> Everything is fine with the periodic boundary condtions. And in the pull code, I have “pull-coord1-k = 1000 ; kJ mol^-1 nm^-2”. Is this the energy contribution you are referring to?

My suggestion was to check the actual energy contribution coming from the restraint in the `.edr` file, as this will tell you about the behavior of the system. If the energy is very low (around zero), then the two atoms are hovering around the target distance; if the energy is large, then they are far away from the target. Sudden changes in this energy would help you pinpoint what’s happening during the dynamics (e.g. find the frame where things went wrong - however I see no evidence that anything has actually gone wrong).

![](https://avatars.discourse-cdn.com/v4/letter/j/aeb1de/48.png) joshhayden:> I analyzed the distance between the atoms against time using ‘gmx distance’ and found that they never get as close as 0.2 nm apart.

Did you perform energy minimization and equilibration in the presence of the restraint, or did you just pick up from a previously equilibrated system? If the coordinates start out far away from the restraint value, it may be hard to get things to fall in line without careful preparation.

![](https://avatars.discourse-cdn.com/v4/letter/j/aeb1de/48.png) joshhayden:> Is there possibly a way to increase the strength of the pull restraint to ensure the distance stays closer to 0.2 nm?

You can certainly increase the force constant, but I’d suggest looking into the above comment about perhaps a more rigorous method of preparation. If you’re trying to force a behavior that isn’t there to start, it may take a while or simply require a different approach.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 24, 2020, 1:48pm 13[![Screenshot 2020-07-24 10:38:20](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/1X/79ce70fed471a0bc6ef9c1f18a185aa6ab12317f.png)Screenshot 2020-07-24 10:38:20789×745 7.04 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/1X/79ce70fed471a0bc6ef9c1f18a185aa6ab12317f.png)

The above graph is the energy output of the pull restraint from the .edr file. The pattern is very similar to the distance-time graph of the ligand-oxygen and the magenesium ion, which I am attaching in my next post.

Would this indicate that something has gone wrong with the pull restraint?

I did not perform energy minimization and equilibration with the pull code in any of the .mdp files. However, the distance between the atoms was very close to 0.2 nm throughout these steps. Should the pull code be in both energy minimization and equilibration .mdp files?

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 24, 2020, 1:49pm 14[![distance](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/1X/052f812f7395bc1a136e1ccfc740f982595456b7.png)distance820×717 7.38 KB](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/original/1X/052f812f7395bc1a136e1ccfc740f982595456b7.png)[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 24, 2020, 6:04pm 15

You’re starting very far away from your target. You should be applying the restraint at all stages of preparing and carrying out the simulation, otherwise it may take a very long time for the ion to be properly coordinated (if ever, based on clashes that it may run into).

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 24, 2020, 6:19pm 16

Okay, I will perform energy minimization and equilibration steps with the pull code in all .mdp files.

Because I am now applying a pull restraint on an atom of the ligand in all steps, should I still have the position restraint in place during the equilibration steps?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 24, 2020, 6:45pm 17

Is the target distance 0.2 nm in the starting coordinates (prior to energy minimization)?

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 24, 2020, 7:24pm 18

Yes, the target distance is 0.2 nm prior to energy minimization.

I checked my .gro file before energy minimization, and the other oxygen of my ligand is already 0.184 nm away from the magnesium ion. However, the oxygen that I applied the restraint to is 0.307 nm away from the magnesium. Perhaps I should apply the pull restraint to the other oxygen and perform energy minimization and equilibration?

[jalemkul](https://gromacs.bioexcel.eu/u/jalemkul) July 24, 2020, 8:27pm 19

Restrain whatever distance makes sense. If the starting coordinates are compatible with the distance restraint, there should be no issue applying multiple restraints (position restraints + distance restraint) since they won’t work in opposition.

[joshhayden](https://gromacs.bioexcel.eu/u/joshhayden) July 24, 2020, 10:02pm 20

Do you think I will run into issues if I set pull-coord1-init = 0.2 and the distance is smaller than 0.2 nm in the starting coordinates before performing energy minimization?

**[next page →](https://gromacs.bioexcel.eu/t/applying-distance-constraints-to-ligand-and-mg-ion/540?page=2)**

###  Related topics 

| Topic |  | Replies | Views | Activity |
|-------|--|---------|-------|----------|
| 2019 Gromacs boresch restraints not workingUser discussionsfree-energy,restraints | 6 | 186 | September 24, 2025 |  |
| Distance restraints between more than one protein and ligandUser discussions | 1 | 435 | December 7, 2022 |  |
| Trouble to apply distance restraintsUser discussionsmdp-parameters,restraints,simulation-setup | 2 | 1517 | April 4, 2022 |  |
| Force fluctuation calculation using constraint simulation in pull code?User discussions | 3 | 303 | October 11, 2023 |  |
| How to put distance restraints into topology fileUser discussionsmdrun,restraints | 25 | 2280 | January 16, 2025 |  |
