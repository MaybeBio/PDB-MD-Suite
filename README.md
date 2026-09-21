# 🔬 PDB/MMCIF segment selector

> PDB file segmentation tool, extract specific chains and residue ranges from PDB/MMCIF files.   

# Installation

```bash
pip install pdb-select
```

# Usage

```bash
pdb-select --help
                                                                                                                                               
 Usage: pdb-select [OPTIONS]                                                                                                                   
                                                                                                                                               
 Select segments from a PDB or MMCIF structure file.                                                                                           
                                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input               -I      <path>  Input PDB or MMCIF file [required]                                                                 │
│ *  --output              -O      <path>  Output PDB file, if not provided, will use input file name with _selected.pdb suffix in current    │
│                                          working directory                                                                                  │
│                                          [required]                                                                                         │
│ *  --segment             -s      <str>   Segments to select in the format chain:start-end (e.g., A:1-10). Repeatable. [required]            │
│    --install-completion                  Install completion for the current shell.                                                          │
│    --show-completion                     Show completion for the current shell, to copy it or customize the installation.                   │
│    --help                                Show this message and exit.                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

example:

```bash
pdb-select -I znf263_all_hs7_30_0.54_0.37_model_0.cif -O znf263_all_hs7_30_0.54_0.37_model_0_selected.pdb -s A:1-10 -s B:20-30
```