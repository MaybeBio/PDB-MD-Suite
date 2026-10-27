from typer.testing import CliRunner
from pdb_md.cli import app

def test_md_subcommand_is_registered():
    result = CliRunner().invoke(app, ["md", "--help"])
    assert result.exit_code == 0
    assert "MD" in result.output.upper()
