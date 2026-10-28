"""The ``preprocess`` stage: guarantee ``00_input/structure.pdb``.

The ``zaff`` stage always consumes ``00_input/structure.pdb``, so this stage
always produces it, whether or not preprocessing is configured.  The user's
structure is first copied verbatim to ``00_input/source.pdb``; with
preprocessing disabled that copy is duplicated to ``structure.pdb``.  With
preprocessing enabled, each configured step runs in order, consuming the
previous step's output and writing the next one.  The first ``{in}`` is
``source.pdb``, the last ``{out}`` is ``structure.pdb``, and intermediate
outputs land in ``00_input/_prep/step{i}.pdb``.

Placeholders are replaced in *every* element of a step tuple, and every path
handed to ``{in}``/``{out}`` is absolute, so steps behave the same regardless
of the tool's working directory.  Commands run with the run root as their cwd.
A failed step raises through :class:`Runner`, and the final check rejects a
missing or empty ``structure.pdb``.
"""

import shutil
from pathlib import Path
from typing import List, Optional, Sequence

from ..config import RunConfig
from ..errors import StageError
from ..plan import RunContext
from ..state import sha256_file, sha256_parts

INPUT_DIR = "00_input"
SOURCE_NAME = "source.pdb"
STRUCTURE_NAME = "structure.pdb"
PREP_DIR = "_prep"


class PreprocessStage:
    """Produce ``00_input/structure.pdb`` from the configured input structure."""

    key = "preprocess"
    deps = ()

    def __init__(self, cfg: RunConfig):
        # ``run`` reads configuration from this binding, not ``ctx.cfg`` (see
        # the ``zaff`` stage for the rationale).
        self.cfg = cfg

    # -- protocol ---------------------------------------------------------

    def input_hash(self, cfg: RunConfig, root: Path) -> str:
        # The user's structure is guaranteed present by config validation, so
        # ``sha256_file`` (not ``hash_or_missing``) is correct here: this stage
        # has no upstream stage artifacts to tolerate being absent.
        return sha256_parts(
            [
                sha256_file(cfg.path(cfg.input.structure)),
                [list(step) for step in cfg.input.preprocess.steps],
            ]
        )

    def artifacts(self, cfg: RunConfig, root: Path) -> List[Path]:
        root = Path(root)
        input_dir = root / INPUT_DIR
        return [
            input_dir / SOURCE_NAME,
            input_dir / STRUCTURE_NAME,
        ]

    def run(self, ctx: RunContext) -> None:
        cfg = self.cfg
        root = Path(ctx.root)
        input_dir = root / INPUT_DIR
        source = input_dir / SOURCE_NAME
        structure = input_dir / STRUCTURE_NAME
        prep_dir = input_dir / PREP_DIR

        input_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cfg.path(cfg.input.structure), source)

        if not cfg.input.preprocess.enabled:
            shutil.copyfile(source, structure)
        else:
            prep_dir.mkdir(parents=True, exist_ok=True)
            steps = cfg.input.preprocess.steps
            previous_out = source
            for i, step in enumerate(steps, 1):
                in_path = source if i == 1 else previous_out
                if i == len(steps):
                    out_path = structure
                else:
                    out_path = prep_dir / "step{}.pdb".format(i)
                argv = [
                    arg.replace("{in}", str(in_path)).replace(
                        "{out}", str(out_path)
                    )
                    for arg in step
                ]
                ctx.runner.run(argv, log_name="preprocess", cwd=root)
                previous_out = out_path

        if not structure.is_file() or structure.stat().st_size == 0:
            raise _stage_error(
                "preprocess output is missing or empty: {}".format(structure),
                cwd=root,
            )

    def verify(self, cfg: RunConfig, root: Path) -> None:
        root = Path(root)
        for path in self.artifacts(cfg, root):
            if not path.is_file() or path.stat().st_size == 0:
                raise _stage_error(
                    "preprocess artifact is missing or empty: {}".format(path),
                    cwd=root,
                )


def _stage_error(
    message: str,
    cwd: Optional[Path] = None,
    hint: Optional[str] = None,
    tail: Optional[Sequence[str]] = None,
) -> StageError:
    """Build a :class:`StageError` for failures that are not a subprocess exit."""
    return StageError(
        message,
        argv=[],
        cwd=cwd,
        returncode=0,
        tail=list(tail or []),
        hint=hint,
    )
