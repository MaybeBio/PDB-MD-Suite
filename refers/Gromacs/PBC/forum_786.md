# Seemingly unresolvable PBC problem on protein complex

> GROMACS version: 2019.4  GROMACS modification: No  Dear All,  I have a protein complex on which I ran some REMD and I want to solve PBC issues before analysis.  However, no matter what I tried, one of the proteins still jumps out of the box.  Firstly I make the system whole with:  $gmx trjconv -f md.xtc -s nvt_298.15.tpr -pbc whole -o whole -n index.ndx  This makes the molecules whole, although both proteins in the complex “jump around”.  I have then centered the system on an interfacial residue...

![](https://europe1.discourse-cdn.com/flex017/uploads/bioexcel1/optimized/2X/2/2d170b6b641e7313ecb17f5e5d92dcf2d4d5811a_2_690x345.png)

### [GitHub - BartBruininks/mdvwhole: Density based object completion over PBC.](https://github.com/BartBruininks/mdvwhole)

Density based object completion over PBC. Contribute to BartBruininks/mdvwhole development by creating an account on GitHub.
