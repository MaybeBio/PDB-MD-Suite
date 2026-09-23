import re
from pathlib import Path
from typing import Optional

import typer
from Bio.PDB import MMCIFParser, PDBIO, PDBParser

from .MultiChainSelector import MultiChainSelector
from .SingleChainSelector import SingleChainSelector

app = typer.Typer(help="Pre- and post-processing toolkit for PDB/MMCIF structure files in molecular dynamics workflows.", no_args_is_help=True)

# Rules for typer: When the app registers only one command and has no callback, this command will be directly promoted to the root command (single-command collapse), and the subcommand layer will no longer exist.
# Adding @app.callback() explicitly declares "this is a command group"
@app.callback()
def main():
    """Segment selector for PDB/MMCIF structure files."""


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
        help="Segments to select, either 'chain' (whole chain, e.g. A) or 'chain:start-end' (e.g. A:1-10). Repeatable.",
    ),
    keep_hetero: str = typer.Option(
        "",
        "--keep-hetero",
        "-H",
        help="Keep HETATM residues. '' (default) drops all; 'all' keeps every HETATM; otherwise a comma-separated list of residue names, e.g. 'ZN'.",
    )
):
    """Select segments from a PDB or MMCIF structure file."""
    if not input_file.exists():
        raise ValueError(f"Input file {input_file} does not exist.")

    # Determine the parser based on file extension
    suffix = input_file.suffix.lower()
    if suffix == ".pdb":
        parser = PDBParser()
    elif suffix == ".cif":
        parser = MMCIFParser()
    else:
        raise ValueError("Unsupported file format. Please provide a .pdb or .cif file.")

    # Parse the structure
    structure = parser.get_structure("structure", input_file)

    # Process the keep_hetero option
    # resolve the heterogen whitelist once:
    # "" -> drop all HETATM, "all" -> keep all HETATM, otherwise a comma-separated list of residue names
    if keep_hetero.strip().lower() in ("", "none"):
        keep_names = frozenset()
    elif keep_hetero.strip().lower() == "all":
        keep_names = frozenset({"all"})
    else:
        keep_names = frozenset( 
            name.strip().upper() for name in keep_hetero.split(",") if name.strip()
            )

    # Create SingleChainSelector objects; a segment without a colon selects a whole chain
    selectors = []
    for seg in segments:
        if ":" not in seg:
            chain_id = seg.strip()
            if not chain_id:
                raise ValueError(
                    f"Invalid segment: {seg!r}. Expected 'chain' or 'chain:start-end'."
                )
            selectors.append(SingleChainSelector(chain_id, None, keep_hetero=keep_names))
            continue
        chain_id, range_str = seg.split(":", 1)
        match = re.fullmatch(r"(\d+)-(\d+)", range_str)
        if not match:
            raise ValueError(f"Invalid range format: {range_str}. Expected format is start-end.")
        start, end = map(int, match.groups())
        selectors.append(SingleChainSelector(chain_id, [(start, end)], keep_hetero=keep_names))

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


if __name__ == "__main__":
    app()
