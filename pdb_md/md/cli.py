import typer

md_app = typer.Typer(
    no_args_is_help=True,
    help="End-to-end GROMACS MD pipeline for DNA + zinc-finger complexes.",
)
