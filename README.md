# 🔬 PDB/MMCIF segment selector

> PDB file segmentation tool, extract specific chains and residue ranges from PDB/MMCIF files.   

# Installation

```bash
pip install pdb-select
```

# Usage

```bash
pdb-select --help
                                                                        
 Usage: pdb-select [OPTIONS] COMMAND [ARGS]...                                                                                                                                          
                                                                                                                                                                                        
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


```bash
pdb-select select  --help
                                                                                                                                                                                        
 Usage: pdb-select select [OPTIONS]                                                                                                                                                     
                                                                                                                                                                                        
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
pdb-select select -I znf263_all_hs7_30_0.54_0.37_model_0.cif -O znf263_all_hs7_30_0.54_0.37_model_0_selected.pdb -s A:369-683 -s B -s C -s D -s E -s F -s G -s H -s I -s J -s K:1-47 -s L:29-75 
```