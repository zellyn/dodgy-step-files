"""Wr005 — Floating-point format inconsistency within one file.

Catalog claim: Floating-point values appear in three or more distinct formats
within a single DATA section: `1.0E-7`, `1e-07`, `0.0000001`, and `1.0e-007`
(extra exponent digit) all coexist.  The spec permits any valid REAL
formatting; each value parses correctly, but tools that hash REAL streams to
detect change disagree on equality, regex-based extractors fail, and human
reviewers find the file unreadable.

Reproducer recipe: one CARTESIAN_POINT with coordinates `(1.0E-7, 1e-07,
0.0000001)` and a second with `(1.0e-007, 1.0, 1.)`.

Byte assertions:
  contains(b'1.0E-7') and contains(b'1e-07') and (contains(b'0.0000001') or contains(b'1.0e-007'))
  count(b'1') + count(b'e') + count(b'E') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr005",
    defect=(
        "Floating-point format inconsistency within one file; "
        "floating-point values appear in three or more distinct formats "
        "within a single DATA section: 1.0E-7, 1e-07, 0.0000001, and 1.0e-007 "
        "(extra exponent digit) all coexist; "
        "multi-source writer pipelines that compose entities from different subsystems "
        "(older Pro/E, multi-pass NX export); "
        "ISO 10303-21 section 6 allows any of these forms; producer is sloppy but conforming; "
        "tools that hash REAL streams to detect change disagree on equality, "
        "regex-based extractors fail, and human reviewers find the file unreadable; "
        "expected kernel behavior: heal and accept; "
        "normalize / parse all valid REAL formats; "
        "coerce / canonicalise on re-emit if the kernel's policy is normalised output; "
        "synonyms: STEP file has weird number formatting, every coordinate looks different, "
        "scientific notation inconsistent, every number formatted differently"
    ),
)


def _render_fp_format_inconsistency() -> str:
    """Return a Part-21 string with mixed floating-point formatting styles."""
    return (
        "ISO-10303-21;\n"
        "/* Wr005: mixed floating-point formats in one DATA section */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr005 - floating-point format inconsistency'),'2;1');\n"
        "FILE_NAME('Wr005.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: coords use four different REAL formats in same file */\n"
        "/* Format 1: uppercase E with negative exponent: 1.0E-7 */\n"
        "/* Format 2: lowercase e with two-digit exponent: 1e-07 */\n"
        "/* Format 3: decimal expansion: 0.0000001 */\n"
        "#1=CARTESIAN_POINT('pt-a',(1.0E-7,1e-07,0.0000001));\n"
        "/* Format 4: extra exponent digit: 1.0e-007 */\n"
        "/* Format 5: plain decimal: 1.0 */\n"
        "/* Format 6: trailing-dot form: 1. */\n"
        "#2=CARTESIAN_POINT('pt-b',(1.0e-007,1.0,1.));\n"
        "#3=GEOMETRIC_CURVE_SET('fp-formats',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_fp_format_inconsistency(path) -> None:
    Path(path).write_bytes(_render_fp_format_inconsistency().encode("utf-8"))


f.render = _render_fp_format_inconsistency  # type: ignore[method-assign]
f.write = _write_fp_format_inconsistency  # type: ignore[method-assign]
