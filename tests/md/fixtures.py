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
