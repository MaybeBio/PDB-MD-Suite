"""Documentation guard and opt-in smoke test for ``pdb-md md``.

The guard test always runs and fails if the README stops documenting the
end-to-end pipeline.  The smoke test only runs when ``PDB_MD_REAL_SMOKE=1``
*and* real ``gmx``/``tleap`` binaries are on ``PATH``; otherwise it skips so
the default suite stays independent of external tools.
"""

import json
import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pdb_md.cli import app
from tests.md.fixtures import PDB_WITH_ZN

_REAL_TOOLS = (
    os.environ.get("PDB_MD_REAL_SMOKE") == "1"
    and shutil.which("tleap") is not None
    and shutil.which("gmx") is not None
)


def test_documented_command_reference_exists():
    # 无真实工具时的最小守护：README 必须包含这些命令
    text = Path(__file__).parents[2].joinpath("README.md").read_text()
    for needle in ("pdb-md md init", "pdb-md md doctor", "pdb-md md run", "_5center.xtc"):
        assert needle in text


@pytest.mark.skipif(
    not _REAL_TOOLS,
    reason="set PDB_MD_REAL_SMOKE=1 with gmx/tleap available",
)
def test_tleap_renders_and_runs(tmp_path, minimal_yaml):
    """Run the ``zaff`` stage end to end with the real ``tleap`` binary.

    The five-residue ZAFF fixture drives preprocess -> zaff through the CLI.
    Real ZAFF prep/frcmod files are user-supplied and never committed, so
    ``PDB_MD_ZAFF_PREP``/``PDB_MD_ZAFF_FRCMOD`` must point at a working ZAFF
    parameter set; without them there is nothing for ``tleap`` to load.
    """

    prep = os.environ.get("PDB_MD_ZAFF_PREP")
    frcmod = os.environ.get("PDB_MD_ZAFF_FRCMOD")
    if not prep or not frcmod:
        pytest.skip(
            "set PDB_MD_ZAFF_PREP and PDB_MD_ZAFF_FRCMOD to ZAFF parameter files"
        )

    run_yaml = minimal_yaml(
        tmp_path,
        tools={
            "gmx": shutil.which("gmx"),
            "tleap": shutil.which("tleap"),
        },
        extra_top_level={"mdrun": {"args": []}},
        replicates_count=1,
        seeds=[10001],
    )
    shutil.copyfile(prep, tmp_path / "params" / "ZAFF.prep")
    shutil.copyfile(frcmod, tmp_path / "params" / "ZAFF.frcmod")
    (tmp_path / "inputs" / "complex.pdb").write_text(PDB_WITH_ZN)

    result = CliRunner().invoke(
        app, ["md", "run", str(run_yaml), "--to", "zaff", "--yes"]
    )
    assert result.exit_code == 0, result.output

    stage_dir = tmp_path / "01_zaff"
    report = json.loads(
        (stage_dir / "zaff_report.json").read_text(encoding="utf-8")
    )
    assert report["n_sites"] == 1
    for name in ("testrun_dry.prmtop", "testrun_solv.prmtop", "testrun_solv.pdb"):
        assert (stage_dir / name).stat().st_size > 0, name
