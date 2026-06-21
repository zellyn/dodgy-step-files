"""Wr045 — Unit name in `LENGTH_UNIT` changed without rescaling coordinate values.

Catalog claim: a user authors a 10 mm cube and changes the export-unit setting to "m";
the writer flips the LENGTH_UNIT text in the GEOMETRIC_REPRESENTATION_CONTEXT to SI
metre but emits the same numeric values (10.0, 10.0, 10.0). Re-import produces a
10-metre cube. Bug-reporter language: "values are unchanged when I change the units",
"10mm cube exports as 10 metres tagged AP214", "unit field is just a label, numbers
stay the same".

Reproducer recipe: a 10 mm cube; declare LENGTH_UNIT as SI metre (SI_UNIT($,.METRE.) —
not MILLI) but emit corner coordinates (10.0, 10.0, 10.0).

Byte assertions:
  contains(b'.METRE.') and contains(b'10.0')
  contains(b'CARTESIAN_POINT')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr045",
    defect=(
        "unit name in LENGTH_UNIT changed without rescaling coordinate values; "
        "input: user authors a 10 mm cube and changes the export-unit setting to 'm' (metre); "
        "writer flips the LENGTH_UNIT text in GEOMETRIC_REPRESENTATION_CONTEXT to SI metre "
        "(SI_UNIT($,.METRE.) without MILLI prefix) but emits the same numeric values (10.0, 10.0, 10.0) "
        "unchanged — should have divided by 1000 to get (0.01, 0.01, 0.01); "
        "re-import produces a 10-metre cube instead of a 10-millimetre cube; "
        "distinct from Wr044 (inch case) because the trigger is 'user selected a different unit "
        "on the way out' rather than 'source kernel was already mm'; "
        "produced by FreeCAD STEP exporter (FreeCAD #20546) when unit drop-down is changed "
        "(mm → m) but writer treats the unit choice as metadata only (label change, no rescale); "
        "expected kernel behavior: writer multiplies/divides coordinates whenever the declared "
        "unit differs from the canonical kernel unit; or refuses the unit change with a diagnostic; "
        "cousin of Wr044 (inch case) and Wr035 (scale-applied-twice); "
        "synonyms: metre unit but mm values, unit field decorative, STEP exporter doesn't "
        "convert when user changes units, labels change but numbers don't"
    ),
)


def _render_wr045() -> str:
    """Render a Part-21 where LENGTH_UNIT says metre but coordinates are in millimetres."""
    return (
        "ISO-10303-21;\n"
        "/* Wr045: unit name in LENGTH_UNIT changed without rescaling coordinate values */\n"
        "/* FreeCAD #20546: user changes export unit mm → m; writer updates the unit label */\n"
        "/* but does NOT divide coordinates by 1000 — values stay as-is (mm numbers) */\n"
        "/* A 10 mm cube is emitted with coordinates (10.0,10.0,10.0) under SI METRE */\n"
        "/* Receivers that honour the metre unit load a 10-metre cube instead */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr045: LENGTH_UNIT says metre but coordinates are in mm'),'2;1');\n"
        "FILE_NAME('Wr045.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: SI_UNIT($,.METRE.) — no MILLI prefix — declares metre as the length unit */\n"
        "/* DEFECT: coordinates are 10.0 (millimetre values); correct metre values would be 0.01 */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(10.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,10.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,10.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(10.0,10.0,10.0));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: $=no prefix means base unit METRE; coordinates 10.0 are mm values not metres */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#9=GEOMETRIC_CURVE_SET('metre-unit-mm-values-shape',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr045(path) -> None:
    Path(path).write_text(_render_wr045())


f.render = _render_wr045  # type: ignore[method-assign]
f.write = _write_wr045    # type: ignore[method-assign]
