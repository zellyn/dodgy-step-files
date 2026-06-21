"""Wr044 — Inch unit declared in `LENGTH_UNIT` context but coordinates emitted in millimetres (no conversion).

Catalog claim: the writer emits a LENGTH_UNIT complex record claiming inches but every
CARTESIAN_POINT carries the original millimetre values verbatim with no scale division.
A part authored as a 25.4 mm cube round-trips as a 25.4 inch (645 mm) cube — visibly
25.4× larger on re-import. Bug-reporter language: "exports geometry data as mm but
tags file as inch — model scales up", "inch unit selected but values are still mm".

Reproducer recipe: GEOMETRIC_REPRESENTATION_CONTEXT with LENGTH_UNIT complex record
(LENGTH_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('INCH', ..)); CARTESIAN_POINT
corner coordinates (25.4, 25.4, 25.4) — millimetre values, not divided by 25.4.

Byte assertions:
  contains(b'INCH')
  contains(b'CARTESIAN_POINT') and contains(b'25.4')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr044",
    defect=(
        "inch unit declared in LENGTH_UNIT context but coordinates emitted in millimetres (no conversion); "
        "input: user selected inches in the STEP-export unit dialog; writer emits LENGTH_UNIT complex "
        "record claiming INCH (via CONVERSION_BASED_UNIT) but every CARTESIAN_POINT carries the original "
        "millimetre values verbatim with no scale division by 25.4; "
        "a part authored as a 25.4 mm cube round-trips as a 25.4 inch (645 mm) cube — 25.4× too large; "
        "produced by FreeCAD with OCCT 7.8.x where the user picks inch in the STEP-export unit "
        "drop-down but the writer skips the value-side conversion; "
        "expected kernel behavior: heal and accept — writer divides every coordinate by 25.4 when "
        "declaring inch unit; or warn and accept by warning the user that values were not converted; "
        "receivers should heal the mismatch when validation properties contradict the declared unit; "
        "subset of Wr035 but with concrete inch-vs-mm symptom; see also: Wr035, U015; "
        "synonyms: STEP file marked inch but model is mm-sized, unit dropdown changes label only, "
        "inch unit but coords are mm, writer forgot to convert when changing unit"
    ),
)


def _render_wr044() -> str:
    """Render a Part-21 where inch unit is declared but coordinates are in mm (no conversion)."""
    return (
        "ISO-10303-21;\n"
        "/* Wr044: inch unit declared in LENGTH_UNIT but coordinates are in millimetres */\n"
        "/* FreeCAD #18078: user picks inch export unit; writer labels file as inch but */\n"
        "/* emits mm coordinates unchanged (skips the divide-by-25.4 conversion pass) */\n"
        "/* A 25.4 mm cube round-trips as a 25.4 inch (645 mm) cube — 25.4x too large */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr044: inch unit declared but coordinates are in mm'),'2;1');\n"
        "FILE_NAME('Wr044.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: LENGTH_UNIT declares INCH but all coordinates are millimetre values */\n"
        "/* Correct inch file would have corner at (1.0, 1.0, 1.0) — 25.4mm / 25.4 */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(25.4,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,25.4,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(25.4,25.4,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: unit declared as INCH; coordinates are mm values (25.4 should be 1.0) */\n"
        "#8=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#9);\n"
        "#9=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#8) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=GEOMETRIC_CURVE_SET('inch-unit-mm-coords-shape',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr044(path) -> None:
    Path(path).write_text(_render_wr044())


f.render = _render_wr044  # type: ignore[method-assign]
f.write = _write_wr044    # type: ignore[method-assign]
