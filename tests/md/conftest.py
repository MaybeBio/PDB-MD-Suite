import copy
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from pdb_md.cli import app
from pdb_md.md.config import (
    CoordinationCheck,
    ForcefieldConfig,
    GromppConfig,
    InputConfig,
    MdpConfig,
    MdrunConfig,
    PbcConfig,
    PreprocessConfig,
    ReplicatesConfig,
    ResidueRef,
    RunConfig,
    SaltConfig,
    SolvateConfig,
    SpeciesConfig,
    SystemConfig,
    ToolPaths,
    TopologyConfig,
    ZincSite,
)

from tests.md.fixtures import FAKE_GMX, FAKE_PARMED, FAKE_TLEAP, PDB_WITH_ZN


@pytest.fixture
def write_script():
    """Return a helper that writes an executable script and returns its path."""

    def _write_script(path: Path, body: str) -> Path:
        path = Path(path)
        path.write_text(body)
        path.chmod(0o755)
        return path

    return _write_script


# Required keys, kept in sync with pdb_md.md.mdp._REQUIRED_KEYS.
_MDP_BODIES = {
    "em1.mdp": (
        "integrator = steep\n"
        "nsteps = 5000\n"
        "emtol = 1000.0\n"
        "emstep = 0.01\n"
    ),
    "em2.mdp": (
        "integrator = steep\n"
        "nsteps = 5000\n"
        "emtol = 1000.0\n"
        "emstep = 0.01\n"
    ),
    "nvt.mdp": (
        "integrator = md\n"
        "nsteps = 50000\n"
        "dt = 0.002\n"
        "gen_vel = yes\n"
        "gen_seed = 10001\n"
        "define = -DPOSRES\n"
    ),
    "npt.mdp": (
        "integrator = md\n"
        "nsteps = 50000\n"
        "dt = 0.002\n"
        "continuation = yes\n"
        "define = -DPOSRES\n"
    ),
    "md.mdp": (
        "integrator = md\n"
        "nsteps = 500000\n"
        "dt = 0.002\n"
    ),
}

# The structure contains exactly the atoms referenced by the default zinc site
# (Zn at A:10 ZN4/ZN; ligands A:1 CY4/SG, A:2 CY4/SG, A:3 HD2/NE2,
# A:4 HD2/NE2), so stage tests can resolve every reference against the file.
_STRUCTURE = (
    "ATOM      1   SG CY4 A   1       1.800   1.200   1.000  1.00  0.00           S\n"
    "ATOM      2   SG CY4 A   2      -1.800   1.200  -1.000  1.00  0.00           S\n"
    "ATOM      3  NE2 HD2 A   3       1.200  -1.800  -1.000  1.00  0.00           N\n"
    "ATOM      4  NE2 HD2 A   4      -1.200  -1.800   1.000  1.00  0.00           N\n"
    "TER\n"
    "HETATM    5   ZN ZN4 A  10       0.000   0.000   0.000  1.00  0.00          ZN\n"
    "END\n"
)


def _write_mdp_files(root: Path) -> None:
    mdp_dir = root / "mdp"
    mdp_dir.mkdir(parents=True, exist_ok=True)
    for name, body in _MDP_BODIES.items():
        (mdp_dir / name).write_text(body)


def _write_inputs(root: Path) -> None:
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    (inputs / "complex.pdb").write_text(_STRUCTURE)

    params = root / "params"
    params.mkdir(parents=True, exist_ok=True)
    (params / "ZAFF.prep").write_text("")
    (params / "ZAFF.frcmod").write_text("")


_ATOM_TYPES = 'addAtomTypes { { "ZN" "Zn" "sp3" } { "S4" "S" "sp3" } { "N3" "N" "sp3" } }'

_DEFAULT_YAML = {
    "schema_version": 1,
    "run_name": "testrun",
    "workdir": ".",
    "tools": {
        "gmx": "gmx",
        "tleap": "tleap",
        "parmed_python": "python",
        "timeout_minutes": 0,
    },
    "input": {
        "structure": "inputs/complex.pdb",
        "preprocess": {"enabled": False, "steps": []},
    },
    "system": {
        "solvate": {"box": "TIP3PBOX", "buffer_angstrom": 10.0},
        "salt": {
            "concentration_M": 0.15,
            "cation": "NA",
            "anion": "CL",
            "water_count": None,
            "net_charge": None,
        },
        "species": {
            "metal_resnames": ["ZN", "ZN3", "ZN4"],
            "dna_resnames": [
                "DA", "DC", "DG", "DT", "DA5", "DC5", "DG5", "DT5",
                "DA3", "DC3", "DG3", "DT3",
            ],
            "solvent_resnames": ["WAT", "SOL", "HOH", "NA", "CL"],
        },
    },
    "forcefield": {
        "protein": "leaprc.protein.ff14SB",
        "nucleic": "leaprc.DNA.bsc1",
        "water": "leaprc.water.tip3p",
        "ions_frcmod": "frcmod.ions1lm_126_tip3p",
        "zaff_prep": "params/ZAFF.prep",
        "zaff_frcmod": "params/ZAFF.frcmod",
        "atom_types": _ATOM_TYPES,
    },
    "zinc_sites": [
        {
            "center_id": 4,
            "coordination_number": 4,
            "zn": {"chain": "A", "resid": 10, "resname": "ZN4", "atom": "ZN"},
            "ligands": [
                {"chain": "A", "resid": 1, "resname": "CY4", "atom": "SG"},
                {"chain": "A", "resid": 2, "resname": "CY4", "atom": "SG"},
                {"chain": "A", "resid": 3, "resname": "HD2", "atom": "NE2"},
                {"chain": "A", "resid": 4, "resname": "HD2", "atom": "NE2"},
            ],
        }
    ],
    "coordination_check": {
        "bond_min_angstrom": 1.8,
        "bond_max_angstrom": 2.6,
        "on_violation": "fail",
        "report_extra_near_atoms": True,
    },
    "mdp": {
        "em": ["mdp/em1.mdp", "mdp/em2.mdp"],
        "nvt": "mdp/nvt.mdp",
        "npt": "mdp/npt.mdp",
        "prod": "mdp/md.mdp",
    },
    "grompp": {"maxwarn": 0},
    "replicates": {"count": 2, "seeds": [10001, 10002]},
    "mdrun": {"args": ["-nb", "gpu"], "ntomp": None},
    "pbc": {
        "enabled": True,
        "ndx": "auto",
        "steps": ["whole", "cluster", "whole", "nojump", "center"],
        "groups": {"cluster": "Complex", "center": "Complex", "output": "System"},
        "bond_max_angstrom": 3.0,
    },
    "topology": {"posre_fc": 1000.0},
}

_MINIMAL_YAML_OVERRIDES = {
    "seeds",
    "center_id",
    "coordination_number",
    "duplicate_ligand",
    "delete_mdp",
    "maxwarn",
    "tools",
    "pbc_ndx",
    "extra_top_level",
    "replicates_count",
}


@pytest.fixture
def minimal_yaml(tmp_path):
    """Write a complete, valid ``run.yaml`` tree and return its path.

    Supported keyword overrides: ``seeds``, ``center_id``,
    ``coordination_number``, ``duplicate_ligand``, ``delete_mdp``,
    ``maxwarn``, ``tools``, ``pbc_ndx``, ``extra_top_level``,
    ``replicates_count``.
    """

    def _minimal_yaml(base: Path = None, **overrides) -> Path:
        unknown = set(overrides) - _MINIMAL_YAML_OVERRIDES
        if unknown:
            raise TypeError(
                "unsupported minimal_yaml override(s): {}".format(
                    ", ".join(sorted(unknown))
                )
            )

        base = Path(base or tmp_path)
        _write_inputs(base)
        _write_mdp_files(base)
        data = copy.deepcopy(_DEFAULT_YAML)

        if "seeds" in overrides:
            data["replicates"]["seeds"] = list(overrides["seeds"])
        if "replicates_count" in overrides:
            data["replicates"]["count"] = overrides["replicates_count"]
        if "center_id" in overrides:
            data["zinc_sites"][0]["center_id"] = overrides["center_id"]
        if "coordination_number" in overrides:
            data["zinc_sites"][0]["coordination_number"] = overrides[
                "coordination_number"
            ]
        if overrides.get("duplicate_ligand"):
            data["zinc_sites"][0]["ligands"][1] = copy.deepcopy(
                data["zinc_sites"][0]["ligands"][0]
            )
        if "delete_mdp" in overrides:
            (base / "mdp" / overrides["delete_mdp"]).unlink()
        if "maxwarn" in overrides:
            maxwarn = overrides["maxwarn"]
            if isinstance(maxwarn, dict):
                data["grompp"].update(maxwarn)
            else:
                data["grompp"]["maxwarn"] = maxwarn
        if "tools" in overrides:
            data["tools"].update(overrides["tools"])
        if "pbc_ndx" in overrides:
            data["pbc"]["ndx"] = overrides["pbc_ndx"]
        if "extra_top_level" in overrides:
            data.update(overrides["extra_top_level"])

        path = base / "run.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False))
        return path

    return _minimal_yaml


def _default_zinc_site() -> ZincSite:
    return ZincSite(
        center_id=4,
        coordination_number=4,
        zn=ResidueRef(chain="A", resid=10, resname="ZN4", atom="ZN"),
        ligands=(
            ResidueRef(chain="A", resid=1, resname="CY4", atom="SG"),
            ResidueRef(chain="A", resid=2, resname="CY4", atom="SG"),
            ResidueRef(chain="A", resid=3, resname="HD2", atom="NE2"),
            ResidueRef(chain="A", resid=4, resname="HD2", atom="NE2"),
        ),
    )


@pytest.fixture
def make_config(tmp_path):
    """Build a fully-formed :class:`RunConfig` without going through YAML."""

    def _make(root: Path = None, **overrides) -> RunConfig:
        root = Path(root or tmp_path)
        _write_inputs(root)
        _write_mdp_files(root)

        base = RunConfig(
            schema_version=1,
            run_name="testrun",
            workdir=".",
            tools=ToolPaths(),
            input=InputConfig(
                structure="inputs/complex.pdb",
                preprocess=PreprocessConfig(),
            ),
            system=SystemConfig(
                solvate=SolvateConfig(),
                salt=SaltConfig(),
                species=SpeciesConfig(),
            ),
            forcefield=ForcefieldConfig(
                zaff_prep="params/ZAFF.prep",
                zaff_frcmod="params/ZAFF.frcmod",
                atom_types=_ATOM_TYPES,
            ),
            zinc_sites=(_default_zinc_site(),),
            coordination_check=CoordinationCheck(),
            mdp=MdpConfig(
                em=("mdp/em1.mdp", "mdp/em2.mdp"),
                nvt="mdp/nvt.mdp",
                npt="mdp/npt.mdp",
                prod="mdp/md.mdp",
            ),
            grompp=GromppConfig(),
            replicates=ReplicatesConfig(count=1, seeds=(10001,)),
            mdrun=MdrunConfig(),
            pbc=PbcConfig(),
            topology=TopologyConfig(),
            source_path=root / "run.yaml",
            root=root.resolve(),
        )

        if "preprocess" in overrides and "input" not in overrides:
            base = replace(
                base, input=replace(base.input, preprocess=overrides.pop("preprocess"))
            )
        return replace(base, **overrides)

    return _make


@pytest.fixture
def e2e_run(tmp_path, monkeypatch, write_script, minimal_yaml):
    """Factory building a run dir wired to fake ``gmx``/``tleap``/ParmEd tools.

    ``_e2e_run(n_replicas=1, fail_stage=None)`` returns ``(run_dir, invoke)``
    where ``invoke`` calls the root Typer app in-process.  Every fake tool
    appends a token line to ``$E2E_CALLS`` only for real stage actions, so a
    skip-only run adds no lines and ``--version`` probes stay invisible.
    """

    def _e2e_run(n_replicas=1, fail_stage=None):
        run_dir = tmp_path / "run"
        run_dir.mkdir(parents=True, exist_ok=True)

        fake_gmx = write_script(run_dir / "fake_gmx", FAKE_GMX)
        fake_tleap = write_script(run_dir / "fake_tleap", FAKE_TLEAP)
        fake_parmed = write_script(run_dir / "fake_parmed", FAKE_PARMED)

        calls = run_dir / "calls.log"
        calls.write_text("", encoding="utf-8")
        monkeypatch.setenv("E2E_CALLS", str(calls))
        monkeypatch.setenv("E2E_FAIL_STAGE", fail_stage or "")

        minimal_yaml(
            run_dir,
            tools={
                "gmx": str(fake_gmx),
                "tleap": str(fake_tleap),
                "parmed_python": str(fake_parmed),
            },
            replicates_count=n_replicas,
            seeds=[10000 * i + i for i in range(1, n_replicas + 1)],
            extra_top_level={"mdrun": {"args": []}},
        )
        # ``minimal_yaml``'s structure has no TER after the Zn, which
        # ``zinc.validate_sites`` rejects.  Use the complete fixture instead.
        (run_dir / "inputs" / "complex.pdb").write_text(
            PDB_WITH_ZN, encoding="utf-8"
        )

        def invoke(args, **kwargs):
            return CliRunner().invoke(app, args, **kwargs)

        return run_dir, invoke

    return _e2e_run
