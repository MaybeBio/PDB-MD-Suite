import re
import typer
from pathlib import Path
from typing import Optional

from Bio.PDB import MMCIFParser, PDBIO, PDBParser

from .utils import load_pdb, save_pdb
from .MultiChainSelector import MultiChainSelector
from .SingleChainSelector import SingleChainSelector
from .rename import MAX_RESNAME_LEN, rename_residues, save_pdb_keeping_columns
from .termini import strip_5_phosphate

app = typer.Typer(help="Pre- and post-processing toolkit for PDB/MMCIF structure files in molecular dynamics workflows.", no_args_is_help=True)

@app.command("select", no_args_is_help=True)
def select_cmd(
    input_file: Path = typer.Option(..., "--input", "-I", help="Input PDB or MMCIF file"),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-O",
        help="Output PDB file, defaults to <input stem>_selected.pdb in the current working directory",
    ),
    segments: list[str] = typer.Option(
        ...,
        "--segment",
        "-S",
        help="Segments to select, either 'chain' (whole chain, e.g. A) or 'chain:start-end' (e.g. A:1-10). Repeatable. The start-end range filters polymer residues only; HETATM residues on the same chain are gated solely by --keep-hetero.",
    ),
    keep_hetero: Optional[list[str]] = typer.Option(
        None,
        "--keep-hetero",
        "-H",
        help=(
            "Keep HETATM residues. Repeatable. Each entry is '[chain:]spec' where spec is 'none','all', or a comma-separated list of residue names (e.g. 'ZN' or 'ZN,HOH'). "
            "An entry without a colon/chain is the global default for every chain; an entry with a chain (e.g. 'A:all') overrides the global set for that chain. "
            "Entries in the same scope are combined by union (-H ZN -H HOH == -H ZN,HOH); a chain entry replaces, not merges with, the global set. "
            "A chain must also appear in --segment, otherwise it is dropped before -H is consulted."
        ),
    )
):
    """Select segments from a PDB or MMCIF structure file."""

    # Parse the structure
    structure = load_pdb(input_file)

    # Process the keep_hetero option.
    # Each entry is '[chain:]spec' where spec is 'none'(drop all HETATM), 'all'(keep every HETATM), or a comma-separated list of residue names.
    # An entry without a colon/chain is the global default for every chain; a chain entry replaces (does not merge with) the global set so that per-chain removal stays expressible.
    def _parse_hetero_spec(spec: str) -> frozenset[str]:
        spec = spec.strip().lower()
        if spec in ("", "none"):
            return frozenset()
        elif spec == "all":
            return frozenset({"all"})
        return frozenset(
            name.strip().upper() for name in spec.split(",") if name.strip()
        )

    # global default for every chain, and per-chain overrides
    global_keep = frozenset()
    chain_keep: dict[str, frozenset[str]] = {}

    # Equals to:
    # entries = keep_hetero if keep_hetero is not None else []
    # for entry in entries:
    for entry in keep_hetero or []:
        # per-chain entry
        if ":" in entry:
            chain_id, spec = entry.split(":", 1)
            chain_id = chain_id.strip()
            if not chain_id:
                raise ValueError(
                    f"Invalid heterogen entry: {entry!r}. Expected '[chain:]spec'."
                )
            # Union set if repeated chain entries, like -H A:ZN -H A:HOH
            chain_keep[chain_id] = (
                chain_keep.get(chain_id, frozenset()) | _parse_hetero_spec(spec)
            )
        # global entry, union set
        else:
            global_keep = global_keep | _parse_hetero_spec(entry)

    # Create SingleChainSelector objects; a segment without a colon selects a whole chain
    selectors = []
    for seg in segments:
        if ":" not in seg:
            chain_id = seg.strip()
            if not chain_id:
                raise ValueError(
                    f"Invalid segment: {seg!r}. Expected 'chain' or 'chain:start-end'."
                )
            selectors.append(SingleChainSelector(chain_id, None, keep_hetero=chain_keep.get(chain_id, global_keep)))
            continue
        chain_id, range_str = seg.split(":", 1)
        match = re.fullmatch(r"(\d+)-(\d+)", range_str)
        if not match:
            raise ValueError(f"Invalid range format: {range_str}. Expected format is start-end.")
        start, end = map(int, match.groups())
        selectors.append(SingleChainSelector(chain_id, [(start, end)], keep_hetero=chain_keep.get(chain_id, global_keep)))

    # A -H chain entry only filters HETATM; the chain still needs a --segment to be accepted in the first place
    # so flag chain names that no segment opens.
    selector_chains = {selector.chain_id for selector in selectors}
    for chain_id in chain_keep:
        if chain_id not in selector_chains:
            typer.echo(
                f"WARNING: -H chain {chain_id} is not covered by any --segment; its HETATM whitelist has no effect",
                err=True
            )

    # Warn about chain ids that are absent from the model that gets written (model 0),
    # so a typo does not silently produce an empty output file
    existing_chains = {
        chain.get_id()
        for model in structure.get_models()
        if model.get_id() == 0
        for chain in model
    }
    for selector in selectors:
        if selector.chain_id not in existing_chains:
            typer.echo(
                f"WARNING: chain {selector.chain_id} not found in {input_file}", err=True
            )

    # Create MultiChainSelector
    multi_selector = MultiChainSelector(selectors)

    # Write out selected portion to output file, defaulting to <input stem>_selected.pdb
    if not output_file:
        output_file = Path(input_file.stem + "_selected.pdb")
    io = PDBIO()
    io.set_structure(structure)
    # PDBIO.save only accepts a filename string or an open filehandle, not a Path
    io.save(str(output_file), multi_selector)
    typer.echo(f"Wrote {output_file}")


@app.command("termini-rm5p", no_args_is_help=True)
def termini_rm5p_cmd(
    input_file: Path = typer.Option(..., "--input", "-I", help="Input PDB or MMCIF file"),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-O",
        help="Output PDB file, defaults to <input stem>_rm5p.pdb in the current working directory",
    ),
    chains: Optional[list[str]] = typer.Option(
        None,
        "--chain",
        "-C",
        help="Chains to process. Repeatable. If not provided, all chains will be processed.",
    ),
):
    """
    Remove terminal phosphate groups from nucleic acids, e.g. 5' phosphate group from DNA/RNA.
    """

    # parse the structure
    structure = load_pdb(input_file)

    # warn about requested chains that are absent, so a typo does not pass silently
    for chain_id in chains or []:
        if chain_id not in structure[0]:
            typer.echo(f"WARNING: chain {chain_id} not found in {input_file}", err=True)

    # strip the 5'-terminal phosphates, collecting what was removed per chain
    removed = strip_5_phosphate(structure, chains)

    if not output_file:
        output_file = Path(input_file.stem + "_rm5p.pdb")
    save_pdb(structure, output_file)

    # report which file was written and what changed
    typer.echo(f"Wrote {output_file}")
    if removed:
        for chain_id, atom_names in removed.items():
            typer.echo(f"  chain {chain_id}: removed {', '.join(atom_names)}")
    else:
        typer.echo("  no 5'-terminal phosphate found; structure left unchanged")



@app.command("res-rename", no_args_is_help=True)
def res_rename_cmd(
    input_file: Path = typer.Option(..., "--input", "-I", help="Input PDB or MMCIF file"),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-O",
        help="Output PDB file, defaults to <input stem>_renamed.pdb in the current working directory",
    ),
    renames: list[str] = typer.Option(
        ...,
        "--rename",
        "-R",
        help="Residue to rename as 'chain:resnum:newresname' (e.g. A:20:HIE). Repeatable. resnum is the residue number carried by that chain's own records (columns 23-26); it is not the atom serial, and it does not necessarily restart at 1 per chain. The new name may be at most 4 characters.",
    ),
):
    """
    Rename residues of specified chains and residue numbers, e.g. to the residue names a
    force field expects for a given protonation state (HIS -> HIE/HID/HIP, CYS -> CYM).
    """

    # Parse the -R entries into (chain_id, resseq, new_resname) triples,
    # validating here so a malformed entry fails before any file is read.
    rename_list = []
    for entry in renames:
        parts = entry.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid --rename entry: {entry!r}. Expected 'chain:resnum:newresname'."
            )
        chain_id, resnum_str, new_resname = (part.strip() for part in parts)
        if not chain_id or not resnum_str or not new_resname:
            raise ValueError(
                f"Invalid --rename entry: {entry!r}. Expected 'chain:resnum:newresname'."
            )
        if not resnum_str.isdigit():
            raise ValueError(
                f"Invalid residue number in {entry!r}: {resnum_str!r}. Expected an integer."
            )
        if len(new_resname) > MAX_RESNAME_LEN:
            raise ValueError(
                f"Residue name {new_resname!r} is {len(new_resname)} characters; "
                f"a PDB residue name holds at most {MAX_RESNAME_LEN}."
            )
        rename_list.append((chain_id, int(resnum_str), new_resname))

    # parse the structure
    structure = load_pdb(input_file)

    # warn about requested chains that are absent, so a typo does not pass silently
    for chain_id in {chain_id for chain_id, _, _ in rename_list}:
        if chain_id not in structure[0]:
            typer.echo(f"WARNING: chain {chain_id} not found in {input_file}", err=True)

    # rename the residues, collecting what was applied
    # the structure is modified in place, so we don't need to assign the return value
    applied = rename_residues(structure, rename_list)

    if not output_file:
        output_file = Path(input_file.stem + "_renamed.pdb")
    save_pdb_keeping_columns(structure, output_file)

    # report which file was written and what changed. Reported from `applied` rather
    # than from the requested list, so that listing one residue twice reports the final
    # state once instead of pairing the first request's target with the last one's name.
    typer.echo(f"Wrote {output_file}")
    for (chain_id, resseq), (old_resname, new_resname) in applied.items():
        typer.echo(f"  chain {chain_id}: {resseq} {old_resname} -> {new_resname}")
    for chain_id, resseq, _ in rename_list:
        if (chain_id, resseq) not in applied and chain_id in structure[0]:
            typer.echo(
                f"WARNING: residue {resseq} not found in chain {chain_id}", err=True
            )


if __name__ == "__main__":
    app()
