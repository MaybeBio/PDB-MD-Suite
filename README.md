# 🔬 PDB/MMCIF segment selector

> Formerly published on PyPI as `pdb-select`. That name is deprecated — use `pdb-md`.

> PDB file segmentation tool, extract specific chains and residue ranges from PDB/MMCIF files.   

# Installation

```bash
pip install pdb-md
```

# Usage

```bash
pdb-md --help
                                                                        
 Usage: pdb-md [OPTIONS] COMMAND [ARGS]...                                                                                                                                          
                                                                                                                                                                                        
 Segment selector for PDB/MMCIF Structure file                                                                                                                                          
                                                                                                                                                                                        
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                                              │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                       │
│ --help                        Show this message and exit.                                                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ select  Select segments from a PDB or MMCIF structure file.                                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯                                                                        
```

> ⚠️ Warning: Sequence index matching to Uniprot only be tested in AlphaFold PDB files. 
> 
> Check for SIFTS 

```bash
pdb-md select  --help
                                                                                                                                                                                        
 Usage: pdb-md select [OPTIONS]                                                                                                                                                     
                                                                                                                                                                                        
 Select segments from a PDB or MMCIF structure file.                                                                                                                                    
                                                                                                                                                                                        
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input    -I      <path>  Input PDB or MMCIF file [required]                                                                                                                     │
│    --output   -O      <path>  Output PDB file, defaults to <input stem>_selected.pdb in the current working directory                                                                │
│ *  --segment  -s      <str>   Segments to select, either 'chain' (whole chain, e.g. A) or 'chain:start-end' (e.g. A:1-10). Repeatable. [required]                                    │
│    --help                     Show this message and exit.                                                                                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

example:

```bash
pdb-md select -I znf263_all_hs7_30_0.54_0.37_model_0.cif -O znf263_all_hs7_30_0.54_0.37_model_0_selected.pdb -s A:369-683 -s B -s C -s D -s E -s F -s G -s H -s I -s J -s K:1-47 -s L:29-75 
```

change from 
![](./figs/image1.png) to
![](./figs/image.png)