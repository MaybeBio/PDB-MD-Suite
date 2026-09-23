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


if __name__ == "__main__":
    app()
