"""Run configuration model, YAML loading, and validation for ``pdb-md md``.

The single ``RunConfig`` object produced here is consumed by every pipeline
stage. All relative paths are resolved against the directory holding
``run.yaml``; the resulting ``RunConfig.root`` is :meth:`Path.resolve`-d.

Validation never stops at the first problem: every error found across the
whole document is collected and raised in one :class:`ConfigError`.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pdb_md.md.errors import ConfigError
from pdb_md.md.mdp import check_mdp

try:  # PyYAML is an optional extra; config loading is the only user.
    import yaml
except ImportError:  # pragma: no cover - exercised only without the extra
    yaml = None


_PBC_STEPS: Tuple[str, ...] = ("whole", "cluster", "whole", "nojump", "center")

_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "run_name",
        "workdir",
        "tools",
        "input",
        "system",
        "forcefield",
        "zinc_sites",
        "coordination_check",
        "mdp",
        "grompp",
        "replicates",
        "mdrun",
        "pbc",
        "topology",
    }
)


@dataclass(frozen=True)
class ToolPaths:
    gmx: str = "gmx"
    tleap: str = "tleap"
    parmed_python: str = "python"
    timeout_minutes: float = 0.0


@dataclass(frozen=True)
class SolvateConfig:
    box: str = "TIP3PBOX"
    buffer_angstrom: float = 10.0


@dataclass(frozen=True)
class SaltConfig:
    concentration_M: float = 0.15
    cation: str = "NA"
    anion: str = "CL"
    water_count: Optional[int] = None
    net_charge: Optional[int] = None


@dataclass(frozen=True)
class SpeciesConfig:
    metal_resnames: Tuple[str, ...] = ("ZN", "ZN3", "ZN4")
    dna_resnames: Tuple[str, ...] = (
        "DA", "DC", "DG", "DT", "DA5", "DC5", "DG5", "DT5",
        "DA3", "DC3", "DG3", "DT3",
    )
    solvent_resnames: Tuple[str, ...] = ("WAT", "SOL", "HOH", "NA", "CL")


@dataclass(frozen=True)
class SystemConfig:
    solvate: SolvateConfig
    salt: SaltConfig
    species: SpeciesConfig


@dataclass(frozen=True)
class ForcefieldConfig:
    # The three required fields come first so dataclass ordering stays legal;
    # construction is keyword-based throughout.
    zaff_prep: str
    zaff_frcmod: str
    atom_types: str
    protein: str = "leaprc.protein.ff14SB"
    nucleic: str = "leaprc.DNA.bsc1"
    water: str = "leaprc.water.tip3p"
    ions_frcmod: str = "frcmod.ions1lm_126_tip3p"


@dataclass(frozen=True)
class ResidueRef:
    chain: str
    resid: int
    resname: str
    atom: str


@dataclass(frozen=True)
class ZincSite:
    center_id: Optional[int]
    coordination_number: int
    zn: ResidueRef
    ligands: Tuple[ResidueRef, ...]


@dataclass(frozen=True)
class CoordinationCheck:
    bond_min_angstrom: float = 1.8
    bond_max_angstrom: float = 2.6
    on_violation: str = "fail"
    report_extra_near_atoms: bool = True


@dataclass(frozen=True)
class MdpConfig:
    em: Tuple[str, ...]
    nvt: str
    npt: str
    prod: str


@dataclass(frozen=True)
class GromppConfig:
    default_maxwarn: int = 0
    # Immutable by design: dict defaults are forbidden on dataclasses.
    by_stage: Tuple[Tuple[str, int], ...] = ()


@dataclass(frozen=True)
class ReplicatesConfig:
    # ``seeds`` is required, so it precedes the defaulted ``count``.
    seeds: Tuple[int, ...]
    count: int = 3


@dataclass(frozen=True)
class MdrunConfig:
    args: Tuple[str, ...] = ()
    ntomp: Optional[int] = None


@dataclass(frozen=True)
class PbcStageGroups:
    cluster: str = "Complex"
    center: str = "Complex"
    output: str = "System"


@dataclass(frozen=True)
class PbcConfig:
    enabled: bool = True
    ndx: str = "auto"
    steps: Tuple[str, ...] = _PBC_STEPS
    groups: PbcStageGroups = field(default_factory=PbcStageGroups)
    bond_max_angstrom: float = 3.0


@dataclass(frozen=True)
class PreprocessConfig:
    enabled: bool = False
    steps: Tuple[Tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class InputConfig:
    structure: str
    preprocess: PreprocessConfig


@dataclass(frozen=True)
class TopologyConfig:
    posre_fc: float = 1000.0


@dataclass(frozen=True)
class RunConfig:
    schema_version: int
    run_name: str
    workdir: str
    tools: ToolPaths
    input: InputConfig
    system: SystemConfig
    forcefield: ForcefieldConfig
    zinc_sites: Tuple[ZincSite, ...]
    coordination_check: CoordinationCheck
    mdp: MdpConfig
    grompp: GromppConfig
    replicates: ReplicatesConfig
    mdrun: MdrunConfig
    pbc: PbcConfig
    topology: TopologyConfig
    source_path: Path
    root: Path

    def path(self, value: str) -> Path:
        """Join ``value`` onto :attr:`root` unless it is already absolute.

        No existence check is performed.
        """
        p = Path(value)
        return p if p.is_absolute() else self.root / p

    def stage_maxwarn(self, stage: str) -> int:
        """Return the ``-maxwarn`` value for ``stage`` (per-stage override wins)."""
        for name, value in self.grompp.by_stage:
            if name == stage:
                return value
        return self.grompp.default_maxwarn


# ---------------------------------------------------------------------------
# Small structural helpers
# ---------------------------------------------------------------------------


def _get(mapping: Any, key: str, default: Any = None) -> Any:
    """Return ``mapping[key]`` or ``default``; ``null`` also yields ``default``."""
    if not isinstance(mapping, dict):
        return default
    value = mapping.get(key, default)
    return default if value is None else value


def _require(mapping: Any, key: str, context: str) -> Any:
    """Return a required mapping key or raise :class:`ConfigError`."""
    if not isinstance(mapping, dict) or key not in mapping or mapping[key] is None:
        raise ConfigError("run.yaml: missing required key {}.{}".format(context, key))
    return mapping[key]


def _mapping(raw: Any, context: str) -> dict:
    """Coerce an optional YAML section to a dict, rejecting wrong types."""
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ConfigError("run.yaml: {} must be a mapping".format(context))
    return raw


def _resolve(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / p


def _coerce(fn: Any, raw: Any, what: str) -> Any:
    """Apply ``fn`` (``int``/``float``) to ``raw``, reporting bad values.

    A malformed YAML value (e.g. ``count: two``) must be collected into the
    aggregate :class:`ConfigError` rather than escaping as a raw
    ``ValueError``/``TypeError``.
    """
    try:
        return fn(raw)
    except (TypeError, ValueError):
        kind = "an integer" if fn is int else "a number"
        raise ConfigError(
            "run.yaml: {} must be {} (got {!r})".format(what, kind, raw)
        )


def _optional_int(value: Any, what: str = "value") -> Optional[int]:
    return None if value is None else _coerce(int, value, what)


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------


def _parse_tools(raw: Any) -> ToolPaths:
    m = _mapping(raw, "tools")
    return ToolPaths(
        gmx=str(_get(m, "gmx", "gmx")),
        tleap=str(_get(m, "tleap", "tleap")),
        parmed_python=str(_get(m, "parmed_python", "python")),
        timeout_minutes=_coerce(
            float, _get(m, "timeout_minutes", 0.0), "tools.timeout_minutes"
        ),
    )


def _parse_preprocess(raw: Any) -> PreprocessConfig:
    m = _mapping(raw, "input.preprocess")
    raw_steps = _get(m, "steps", ()) or ()
    steps = tuple(tuple(str(part) for part in step) for step in raw_steps)
    return PreprocessConfig(enabled=bool(_get(m, "enabled", False)), steps=steps)


def _parse_input(raw: Any) -> InputConfig:
    m = _mapping(raw, "input")
    return InputConfig(
        structure=str(_require(m, "structure", "input")),
        preprocess=_parse_preprocess(m.get("preprocess")),
    )


def _parse_species(raw: Any) -> SpeciesConfig:
    m = _mapping(raw, "system.species")
    defaults = SpeciesConfig()
    return SpeciesConfig(
        metal_resnames=tuple(
            str(v) for v in _get(m, "metal_resnames", defaults.metal_resnames)
        ),
        dna_resnames=tuple(
            str(v) for v in _get(m, "dna_resnames", defaults.dna_resnames)
        ),
        solvent_resnames=tuple(
            str(v) for v in _get(m, "solvent_resnames", defaults.solvent_resnames)
        ),
    )


def _parse_system(raw: Any) -> SystemConfig:
    m = _mapping(raw, "system")
    solvate = _mapping(m.get("solvate"), "system.solvate")
    salt = _mapping(m.get("salt"), "system.salt")
    return SystemConfig(
        solvate=SolvateConfig(
            box=str(_get(solvate, "box", "TIP3PBOX")),
            buffer_angstrom=_coerce(
                float, _get(solvate, "buffer_angstrom", 10.0),
                "system.solvate.buffer_angstrom",
            ),
        ),
        salt=SaltConfig(
            concentration_M=_coerce(
                float, _get(salt, "concentration_M", 0.15),
                "system.salt.concentration_M",
            ),
            cation=str(_get(salt, "cation", "NA")),
            anion=str(_get(salt, "anion", "CL")),
            water_count=_optional_int(
                _get(salt, "water_count", None), "system.salt.water_count"
            ),
            net_charge=_optional_int(
                _get(salt, "net_charge", None), "system.salt.net_charge"
            ),
        ),
        species=_parse_species(m.get("species")),
    )


def _parse_forcefield(raw: Any) -> ForcefieldConfig:
    m = _mapping(raw, "forcefield")
    return ForcefieldConfig(
        zaff_prep=str(_require(m, "zaff_prep", "forcefield")),
        zaff_frcmod=str(_require(m, "zaff_frcmod", "forcefield")),
        atom_types=str(_require(m, "atom_types", "forcefield")),
        protein=str(_get(m, "protein", "leaprc.protein.ff14SB")),
        nucleic=str(_get(m, "nucleic", "leaprc.DNA.bsc1")),
        water=str(_get(m, "water", "leaprc.water.tip3p")),
        ions_frcmod=str(_get(m, "ions_frcmod", "frcmod.ions1lm_126_tip3p")),
    )


def _parse_ref(raw: Any, context: str) -> ResidueRef:
    m = _mapping(raw, context)
    return ResidueRef(
        chain=str(_require(m, "chain", context)),
        resid=_coerce(int, _require(m, "resid", context), context + ".resid"),
        resname=str(_require(m, "resname", context)),
        atom=str(_require(m, "atom", context)),
    )


def _parse_zinc_sites(raw: Any) -> Tuple[ZincSite, ...]:
    if raw is None:
        raise ConfigError("run.yaml: missing required key zinc_sites")
    if not isinstance(raw, list):
        raise ConfigError("run.yaml: zinc_sites must be a list")
    sites: List[ZincSite] = []
    for index, item in enumerate(raw, 1):
        context = "zinc_sites[{}]".format(index)
        m = _mapping(item, context)
        raw_ligands = _require(m, "ligands", context)
        if not isinstance(raw_ligands, list):
            raise ConfigError("run.yaml: {}.ligands must be a list".format(context))
        ligands = tuple(
            _parse_ref(lig, "{}.ligands[{}]".format(context, i))
            for i, lig in enumerate(raw_ligands, 1)
        )
        sites.append(
            ZincSite(
                center_id=_optional_int(
                    _get(m, "center_id", None), context + ".center_id"
                ),
                coordination_number=_coerce(
                    int,
                    _require(m, "coordination_number", context),
                    context + ".coordination_number",
                ),
                zn=_parse_ref(_require(m, "zn", context), context + ".zn"),
                ligands=ligands,
            )
        )
    return tuple(sites)


def _parse_coordination(raw: Any) -> CoordinationCheck:
    m = _mapping(raw, "coordination_check")
    return CoordinationCheck(
        bond_min_angstrom=_coerce(
            float, _get(m, "bond_min_angstrom", 1.8),
            "coordination_check.bond_min_angstrom",
        ),
        bond_max_angstrom=_coerce(
            float, _get(m, "bond_max_angstrom", 2.6),
            "coordination_check.bond_max_angstrom",
        ),
        on_violation=str(_get(m, "on_violation", "fail")),
        report_extra_near_atoms=bool(_get(m, "report_extra_near_atoms", True)),
    )


def _parse_mdp(raw: Any) -> MdpConfig:
    m = _mapping(raw, "mdp")
    raw_em = _get(m, "em", ()) or ()
    if isinstance(raw_em, str):
        raw_em = (raw_em,)
    return MdpConfig(
        em=tuple(str(path) for path in raw_em),
        nvt=str(_require(m, "nvt", "mdp")),
        npt=str(_require(m, "npt", "mdp")),
        prod=str(_require(m, "prod", "mdp")),
    )


def _parse_grompp(raw: Any) -> GromppConfig:
    m = _mapping(raw, "grompp")
    by_stage = tuple(
        (str(name), _coerce(int, value, "grompp.{}".format(name)))
        for name, value in m.items()
        if name != "maxwarn"
    )
    return GromppConfig(
        default_maxwarn=_coerce(int, _get(m, "maxwarn", 0), "grompp.maxwarn"),
        by_stage=by_stage,
    )


def _parse_replicates(raw: Any) -> ReplicatesConfig:
    m = _mapping(raw, "replicates")
    raw_seeds = _get(m, "seeds", ()) or ()
    return ReplicatesConfig(
        seeds=tuple(
            _coerce(int, seed, "replicates.seeds[{}]".format(index))
            for index, seed in enumerate(raw_seeds, 1)
        ),
        count=_coerce(int, _get(m, "count", 3), "replicates.count"),
    )


def _parse_mdrun(raw: Any) -> MdrunConfig:
    m = _mapping(raw, "mdrun")
    raw_args = _get(m, "args", ()) or ()
    return MdrunConfig(
        args=tuple(str(arg) for arg in raw_args),
        ntomp=_optional_int(_get(m, "ntomp", None), "mdrun.ntomp"),
    )


def _parse_pbc_groups(raw: Any) -> PbcStageGroups:
    m = _mapping(raw, "pbc.groups")
    return PbcStageGroups(
        cluster=str(_get(m, "cluster", "Complex")),
        center=str(_get(m, "center", "Complex")),
        output=str(_get(m, "output", "System")),
    )


def _parse_pbc(raw: Any) -> PbcConfig:
    m = _mapping(raw, "pbc")
    raw_steps = _get(m, "steps", _PBC_STEPS) or ()
    return PbcConfig(
        enabled=bool(_get(m, "enabled", True)),
        ndx=str(_get(m, "ndx", "auto")),
        steps=tuple(str(step) for step in raw_steps),
        groups=_parse_pbc_groups(m.get("groups")),
        bond_max_angstrom=_coerce(
            float, _get(m, "bond_max_angstrom", 3.0), "pbc.bond_max_angstrom"
        ),
    )


def _parse_topology(raw: Any) -> TopologyConfig:
    m = _mapping(raw, "topology")
    return TopologyConfig(
        posre_fc=_coerce(float, _get(m, "posre_fc", 1000.0), "topology.posre_fc")
    )


_SECTION_PARSERS = {
    "tools": _parse_tools,
    "input": _parse_input,
    "system": _parse_system,
    "forcefield": _parse_forcefield,
    "coordination_check": _parse_coordination,
    "mdp": _parse_mdp,
    "grompp": _parse_grompp,
    "replicates": _parse_replicates,
    "mdrun": _parse_mdrun,
    "pbc": _parse_pbc,
    "topology": _parse_topology,
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _ref_key(ref: ResidueRef) -> Tuple[str, int, str, str]:
    return (ref.chain, ref.resid, ref.resname, ref.atom)


def _ref_text(ref: ResidueRef) -> str:
    return "{}:{} {}/{}".format(ref.chain, ref.resid, ref.resname, ref.atom)


def _check_mdp_file(
    root: Path, value: str, stage: str, errors: List[str], label: str
) -> None:
    path = _resolve(root, value)
    if not path.is_file():
        errors.append("{}: mdp file does not exist: {}".format(label, path))
        return
    try:
        check_mdp(path, stage)
    except ConfigError as exc:
        errors.append("{}: {}".format(label, exc.message))
    except OSError as exc:
        errors.append("{}: cannot read mdp file {}: {}".format(label, path, exc))


def _validate_zinc_sites(sites: Tuple[ZincSite, ...], errors: List[str]) -> None:
    if not sites:
        errors.append("zinc_sites must contain at least one site")
    for index, site in enumerate(sites, 1):
        label = "zinc_sites[{}]".format(index)
        if site.coordination_number != 4:
            errors.append(
                "{}: coordination_number must be four for ZAFF (got {})".format(
                    label, site.coordination_number
                )
            )
        if site.center_id in (11, 12):
            errors.append(
                "{}: center_id {} is not supported (ZAFF center 11/12 "
                "cannot be modelled)".format(label, site.center_id)
            )
        if len(site.ligands) != 4:
            errors.append(
                "{}: expected 4 ligand references, got {}".format(
                    label, len(site.ligands)
                )
            )
        seen = set()
        zn_key = _ref_key(site.zn)
        for ref in site.ligands:
            key = _ref_key(ref)
            if key in seen:
                errors.append(
                    "{}: duplicate ligand reference {}".format(label, _ref_text(ref))
                )
            seen.add(key)
            if key == zn_key:
                errors.append(
                    "{}: ligand reference {} duplicates the Zn atom".format(
                        label, _ref_text(ref)
                    )
                )


def _validate_replicates(replicates: ReplicatesConfig, errors: List[str]) -> None:
    if replicates.count < 1:
        errors.append(
            "replicates.count must be >= 1 (got {})".format(replicates.count)
        )
    if len(replicates.seeds) != replicates.count:
        errors.append(
            "replicates.seeds has {} entries but replicates.count is {}".format(
                len(replicates.seeds), replicates.count
            )
        )
    if len(set(replicates.seeds)) != len(replicates.seeds):
        errors.append(
            "replicates.seeds must be distinct (got {})".format(
                list(replicates.seeds)
            )
        )


def _validate_grompp(grompp: GromppConfig, errors: List[str]) -> None:
    if grompp.default_maxwarn < 0:
        errors.append(
            "grompp.maxwarn must be >= 0 (got {})".format(grompp.default_maxwarn)
        )
    for stage, value in grompp.by_stage:
        if value < 0:
            errors.append(
                "grompp.{} must be >= 0 (got {})".format(stage, value)
            )


def _validate_system(system: SystemConfig, errors: List[str]) -> None:
    salt = system.salt
    if salt.concentration_M < 0:
        errors.append(
            "salt.concentration_M must be >= 0 (got {})".format(
                salt.concentration_M
            )
        )
    if salt.cation == salt.anion:
        errors.append(
            "salt.cation and salt.anion must differ (both {!r})".format(salt.cation)
        )
    species = system.species
    for name in ("metal_resnames", "dna_resnames", "solvent_resnames"):
        if not getattr(species, name):
            errors.append("species.{} must not be empty".format(name))


def _validate_pbc(pbc: PbcConfig, root: Path, errors: List[str]) -> None:
    if pbc.steps != _PBC_STEPS:
        errors.append(
            "pbc.steps must be {} in schema 1 (got {})".format(
                list(_PBC_STEPS), list(pbc.steps)
            )
        )
    if pbc.ndx != "auto":
        ndx_path = _resolve(root, pbc.ndx)
        if not ndx_path.exists():
            errors.append("pbc.ndx file does not exist: {}".format(ndx_path))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def load_config(path: Path) -> RunConfig:
    """Load and validate ``run.yaml``, returning an immutable :class:`RunConfig`.

    All problems found are reported together in a single :class:`ConfigError`.
    """
    if yaml is None:
        raise ConfigError(
            "PyYAML is required to load run.yaml",
            hint='pip install "pdb-md[md]"',
        )

    source_path = Path(path)
    try:
        text = source_path.read_text()
    except OSError as exc:
        raise ConfigError("{}: cannot read configuration: {}".format(source_path, exc))

    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError("{}: invalid YAML: {}".format(source_path, exc))

    if not isinstance(raw, dict):
        raise ConfigError(
            "{}: top-level YAML document must be a mapping".format(source_path)
        )

    errors: List[str] = []

    for key in raw:
        if key not in _TOP_LEVEL_KEYS:
            errors.append("unknown top-level key {!r}".format(key))

    schema_version = raw.get("schema_version")
    if schema_version != 1:
        errors.append(
            "schema_version must be 1 (got {!r})".format(schema_version)
        )

    run_name = raw.get("run_name")
    if not isinstance(run_name, str) or not run_name.strip():
        errors.append("run_name must be a non-empty string")
    elif re.fullmatch(r"[A-Za-z0-9._-]+", run_name) is None:
        errors.append(
            "run_name may only contain letters, digits, '.' '_' and '-'"
        )

    workdir = raw.get("workdir", ".")
    if not isinstance(workdir, str) or not workdir:
        errors.append("workdir must be a non-empty string")
        workdir = "."
    root = (source_path.parent / workdir).resolve()
    if any(ch.isspace() for ch in str(root)):
        errors.append(
            "run directory path must not contain whitespace "
            "(LEaP cannot quote paths)"
        )

    parsed: Dict[str, Any] = {}
    for name, parser in _SECTION_PARSERS.items():
        try:
            parsed[name] = parser(raw.get(name))
        except ConfigError as exc:
            errors.append(exc.message)
    try:
        parsed["zinc_sites"] = _parse_zinc_sites(raw.get("zinc_sites"))
    except ConfigError as exc:
        errors.append(exc.message)

    # --- semantic checks (all collected) ---------------------------------
    if "input" in parsed:
        structure_path = _resolve(root, parsed["input"].structure)
        if not structure_path.exists():
            errors.append(
                "input.structure does not exist: {}".format(structure_path)
            )

    if "mdp" in parsed:
        mdp = parsed["mdp"]
        if not mdp.em:
            errors.append("mdp.em must list at least one .mdp file")
        for i, value in enumerate(mdp.em, 1):
            _check_mdp_file(root, value, "em", errors, "mdp.em[{}]".format(i))
        _check_mdp_file(root, mdp.nvt, "nvt", errors, "mdp.nvt")
        _check_mdp_file(root, mdp.npt, "npt", errors, "mdp.npt")
        _check_mdp_file(root, mdp.prod, "prod", errors, "mdp.prod")

    if "zinc_sites" in parsed:
        _validate_zinc_sites(parsed["zinc_sites"], errors)

    if (
        "forcefield" in parsed
        and "ZN" not in parsed["forcefield"].atom_types
    ):
        errors.append('forcefield.atom_types must contain "ZN"')

    if "replicates" in parsed:
        _validate_replicates(parsed["replicates"], errors)

    if "grompp" in parsed:
        _validate_grompp(parsed["grompp"], errors)

    if "system" in parsed:
        _validate_system(parsed["system"], errors)

    if "pbc" in parsed:
        _validate_pbc(parsed["pbc"], root, errors)

    if errors:
        raise ConfigError(
            "{}: invalid configuration:\n{}".format(
                source_path, "\n".join("  - " + error for error in errors)
            )
        )

    return RunConfig(
        schema_version=schema_version,
        run_name=run_name,
        workdir=workdir,
        tools=parsed["tools"],
        input=parsed["input"],
        system=parsed["system"],
        forcefield=parsed["forcefield"],
        zinc_sites=parsed["zinc_sites"],
        coordination_check=parsed["coordination_check"],
        mdp=parsed["mdp"],
        grompp=parsed["grompp"],
        replicates=parsed["replicates"],
        mdrun=parsed["mdrun"],
        pbc=parsed["pbc"],
        topology=parsed["topology"],
        source_path=source_path,
        root=root,
    )
