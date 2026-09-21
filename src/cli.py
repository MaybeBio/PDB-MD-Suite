import typer
from .SingleChainSelector import SingleChainSelector
from .MultiChainSelector import MultiChainSelector
from Bio.PDB import PDBParser, MMCIFParser, PDBIO
from pathlib import Path
import re

app = typer.Typer(help="Segment selector for PDB/MMCIF Structure file", no_args_is_help=True)

@app.command(
    "select",
    no_args_is_help=True
)

# note Argument is different from Option, Argument is required and positional, Option is optional and can be specified with --option or -o
def select_cmd(
    input_file: Path = typer.Option(..., "--input", "-I" , help="Input PDB or MMCIF file"),
    output_file: Path = typer.Option(..., "--output", "-O", help="Output PDB file, if not provided, will use input file name with _selected.pdb suffix in current working directory"),
    segments: list[str] = typer.Option(..., "--segment", "-s", help="Segments to select in the format chain:start-end (e.g., A:1-10). Repeatable."),
):
    """Select segments from a PDB or MMCIF structure file."""
    # check the file
    if not input_file.exists():
        raise ValueError(f"Input file {input_file} does not exist.")

    # Determine the parser based on file extension
    if input_file.endswith(".pdb"):
        parser = PDBParser()
    elif input_file.endswith(".cif"):
        parser = MMCIFParser()
    else:
        raise ValueError("Unsupported file format. Please provide a .pdb or .cif file.")

    # Parse the structure
    structure = parser.get_structure("structure", input_file)

    # Create SingleChainSelector objects for each chain and region
    selectors = []
    for seg in segments:
        chain_id, range_str = seg.split(":", 1)
        match = re.match(r"(\d+)-(\d+)", range_str)
        if not match:
            raise ValueError(f"Invalid range format: {range_str}. Expected format is start-end.")
        start, end = map(int, match.groups())
        selectors.append(SingleChainSelector(chain_id, [(start, end)]))

    # Create MultiChainSelector
    multi_selector = MultiChainSelector(selectors)

    # Write out selected portion to output file
    io = PDBIO()
    io.set_structure(structure)
    # check if output_file is provided, if not, use the input_file name with _selected.pdb suffix
    if not output_file:
        # choose to output the file in the same directory as input_file, with _selected.pdb suffix:
        # output_file = input_file.with_name(input_file.stem + "_selected.pdb")
        # or directly output in current working directory with _selected.pdb suffix
        output_file = Path(input_file.stem + "_selected.pdb")
    io.save(output_file, multi_selector)

if __name__ == "__main__":
    app()