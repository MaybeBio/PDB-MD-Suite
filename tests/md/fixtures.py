"""Shared structural fixtures for the MD stage tests.

``PDB_WITH_ZN`` matches the default zinc site built by ``make_config``: Zn at
``A:10`` (ZN4/ZN) coordinated by ligands at ``A:1``/``A:2`` (CY4/SG) and
``A:3``/``A:4`` (HD2/NE2), each 2.1 A from the metal and fenced by TER records.
"""

PDB_WITH_ZN = """\
ATOM      1  SG  CY4 A   1       2.100   0.000   0.000  1.00  0.00           S
ATOM      2  SG  CY4 A   2      -2.100   0.000   0.000  1.00  0.00           S
ATOM      3  NE2 HD2 A   3       0.000   2.100   0.000  1.00  0.00           N
ATOM      4  NE2 HD2 A   4       0.000  -2.100   0.000  1.00  0.00           N
TER
HETATM    5   ZN ZN4 A  10       0.000   0.000   0.000  1.00  0.00          Zn
TER
END
"""


# ---------------------------------------------------------------------------
# Canonical solvated system used by the fake-binary end-to-end test.
#
# Every fake tool agrees on one seven-atom system (resid -> resname -> name):
#
#   1 CY4 SG   2 CY4 SG   3 HD2 NE2   4 HD2 NE2   5 ZN4 ZN
#   6 WAT O    7 WAT O
#
# The dry topology is the first five atoms, so solv (7) > dry (5).  The Zn is
# at LEaP residue position 5 and its four ligands occupy positions 1-4, which
# matches the default zinc site in ``minimal_yaml`` and the atoms in
# ``PDB_WITH_ZN`` above.
# ---------------------------------------------------------------------------

GRO_ATOMS = (
    ("CY4", "SG"),
    ("CY4", "SG"),
    ("HD2", "NE2"),
    ("HD2", "NE2"),
    ("ZN4", "ZN"),
    ("WAT", "O"),
    ("WAT", "O"),
)

#: The canonical seven-atom ``.gro`` body shared by the fake ``mdrun`` and the
#: fake ParmEd conversion.  Format: ``%5d%-5s%5s%5d`` then three coordinates.
CANONICAL_GRO = (
    "testrun system\n"
    + str(len(GRO_ATOMS))
    + "\n"
    + "".join(
        "%5d%-5s%5s%5d%8.3f%8.3f%8.3f\n"
        % (index, resname, name, index, 0.0, 0.0, 0.0)
        for index, (resname, name) in enumerate(GRO_ATOMS, 1)
    )
    + "   1.00000   1.00000   1.00000\n"
)


_FAKE_GMX_TEMPLATE = r'''#!/usr/bin/env python3
"""Fake ``gmx``: emits the artifacts the pipeline expects, no real MD."""

import os
import sys
from pathlib import Path

GRO = @@GRO@@


def _value(argv, flag):
    return argv[argv.index(flag) + 1]


def _log(line):
    path = os.environ.get("E2E_CALLS")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def main():
    argv = sys.argv[1:]
    if not argv:
        return 0
    command = argv[0]

    if command == "--version":
        print("gmx fake 1.0")
        return 0

    if command == "grompp":
        output = _value(argv, "-o")
        Path(output).write_text("tpr\n", encoding="utf-8")
        _log("grompp " + output)
        return 0

    if command == "mdrun":
        prefix = _value(argv, "-deffnm")
        _log("mdrun " + prefix)
        # Fail only the production run so em/nvt/npt still complete.
        if os.environ.get("E2E_FAIL_STAGE", "") == "mdrun" and "06_prod" in prefix:
            print("Fatal error:")
            print("production mdrun failed for " + prefix)
            print("GROMACS execution failed")
            return 1
        for extension in ("edr", "log", "cpt", "xtc"):
            Path(prefix + "." + extension).write_text(
                "fake output\n", encoding="utf-8"
            )
        Path(prefix + ".gro").write_text(GRO, encoding="utf-8")
        return 0

    if command == "trjconv":
        sys.stdin.read()
        output = _value(argv, "-o")
        Path(output).write_text("xtc\n", encoding="utf-8")
        _log("trjconv " + output)
        return 0

    if command == "check":
        print("# Atoms  7", file=sys.stderr)
        _log("check")
        return 0

    if command == "distance":
        output = _value(argv, "-oav")
        n_pairs = sum(1 for arg in argv if arg == "-select")
        row = "0.0 " + " ".join(["2.1"] * n_pairs)
        Path(output).write_text(
            '# fake distance output\n@ title "Zn-ligand distances"\n'
            + row
            + "\n",
            encoding="utf-8",
        )
        _log("distance " + output)
        return 0

    print("fake gmx: unknown command " + command)
    return 2


if __name__ == "__main__":
    sys.exit(main())
'''


_FAKE_TLEAP_TEMPLATE = r'''#!/usr/bin/env python3
"""Fake ``tleap``: writes leap.log and minimal AMBER prmtop files."""

import os
import re
import sys
from pathlib import Path

# Parsed by pdb_md.md.tleap.parse_leap_log: water_count=1000, net_charge=-4.
LEAP_LOG = "Added 1000 residues\nTotal unperturbed charge: -4.000000\n"

PRMTOP_TEMPLATE = """\
%VERSION VERSION_STAMP = V0001.000  DATE = 01/01/01  00:00:00
%FLAG TITLE
%FORMAT(20a4)
testrun
%FLAG POINTERS
%FORMAT(10I8)
{natom:8d}
%FLAG ATOM_NAME
%FORMAT(20a4)
{names}
%FLAG RESIDUE_POINTER
%FORMAT(10I8)
{pointers}
"""

DRY_NAMES = ["SG", "SG", "NE2", "NE2", "ZN"]
SOLV_NAMES = ["SG", "SG", "NE2", "NE2", "ZN", "O", "O"]


def _write_prmtop(path, names):
    names_line = "".join("{:<4}".format(name) for name in names)
    pointers = "".join(
        "{:8d}".format(index) for index in range(1, len(names) + 1)
    )
    Path(path).write_text(
        PRMTOP_TEMPLATE.format(
            natom=len(names), names=names_line, pointers=pointers
        ),
        encoding="utf-8",
    )


def _log():
    path = os.environ.get("E2E_CALLS")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("tleap\n")


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--version":
        print("tleap fake 1.0")
        return 0
    if "-f" not in argv:
        print("fake tleap: expected -f <script>")
        return 2

    script = Path(argv[argv.index("-f") + 1]).read_text(encoding="utf-8")
    match = re.search(r"(\S+)_(?:dry|solv)\.prmtop", script)
    prefix = match.group(1) if match else "testrun"

    Path("leap.log").write_text(LEAP_LOG, encoding="utf-8")
    _write_prmtop(prefix + "_dry.prmtop", DRY_NAMES)
    _write_prmtop(prefix + "_solv.prmtop", SOLV_NAMES)
    for suffix in ("dry", "solv"):
        for extension in ("inpcrd", "pdb"):
            Path("{}_{}.{}".format(prefix, suffix, extension)).write_text(
                "fake\n", encoding="utf-8"
            )

    _log()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


_FAKE_PARMED_TEMPLATE = r'''#!/usr/bin/env python3
"""Fake ParmEd conversion script: writes conf.gro and a GROMACS topology."""

import sys
from pathlib import Path

GRO = @@GRO@@

# Two moleculetypes whose [ molecules ] expansion is exactly the 7 gro atoms:
# complex (5 atoms, the sole solute) + WAT x2.  The complex carries the ZN4
# metal residue and the ligand names the zinc site maps to.
TOPOLOGY = """\
[ defaults ]
1 2 yes 0.5 0.8333

[ atomtypes ]
ZN ZN 65.38 0.0 A 0.0 0.0
S4 S 32.06 0.0 A 0.0 0.0
N3 N 14.01 0.0 A 0.0 0.0
OW O 16.00 0.0 A 0.0 0.0

[ moleculetype ]
complex 3

[ atoms ]
1 SG 1 CY4 SG 1 0.0 32.06
2 SG 2 CY4 SG 2 0.0 32.06
3 NE2 3 HD2 NE2 3 0.0 14.01
4 NE2 4 HD2 NE2 4 0.0 14.01
5 ZN 5 ZN4 ZN 5 0.0 65.38

[ moleculetype ]
WAT 2

[ atoms ]
1 O 6 WAT O 6 0.0 16.00

[ system ]
testrun

[ molecules ]
complex 1
WAT 2
"""


def _value(argv, flag):
    return argv[argv.index(flag) + 1]


def main():
    argv = sys.argv[1:]
    if not argv:
        return 0
    # Tool-version probe: ``parmed_python -c "import parmed; ..."``.
    if argv[0] in ("-c", "--version"):
        print("fake parmed 1.0")
        return 0

    top = _value(argv, "--top")
    gro = _value(argv, "--gro")
    Path(top).write_text(TOPOLOGY, encoding="utf-8")
    Path(gro).write_text(GRO, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


#: Executable script bodies written by the ``e2e_run`` fixture.  The two that
#: need the canonical coordinates get them embedded as a Python literal.
FAKE_GMX = _FAKE_GMX_TEMPLATE.replace("@@GRO@@", repr(CANONICAL_GRO))
FAKE_TLEAP = _FAKE_TLEAP_TEMPLATE
FAKE_PARMED = _FAKE_PARMED_TEMPLATE.replace("@@GRO@@", repr(CANONICAL_GRO))
