"""U006 — PrePoMax double-applies inch->mm scaling on inch STEP (25.4x too large).

Catalog claim: PrePoMax recognizes the STEP file as inch and then multiplies coordinates
by 25.4, leaving the body 25.4x too large; the conversion is applied where coordinates
are already in mm.

Reproducer recipe: inch SolidWorks STEP with CONVERSION_BASED_UNIT('INCH',#lmwu) and
LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#mm) — coordinates in mm — receiver
multiplies by 25.4 again.

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('INCH'")
  contains(b'25.4') or matches(rb'LENGTH_MEASURE\\(25\\.4\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U006",
    defect=(
        "PrePoMax double-applies inch->mm scaling on inch STEP (25.4x too large); "
        "input: SolidWorks inch STEP with CONVERSION_BASED_UNIT('INCH',#lmwu) where "
        "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#mm) defines the inch-to-mm factor; "
        "coordinates are in mm values (e.g. 25.4, 50.8 for 1-inch and 2-inch extents); "
        "PrePoMax 1.x recognizes the file as inch and multiplies all coordinates by 25.4 again, "
        "leaving the body 25.4x too large — double conversion error; "
        "the conversion is applied once inside the CONVERSION_BASED_UNIT factor chain "
        "and a second time in the receiver's import pipeline; "
        "kernel must normalize/apply the CONVERSION_BASED_UNIT factor exactly once; "
        "never compose with target-unit conversion on the same coordinates; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: PrePoMax double-applies inch scaling, STEP body 25.4x too large in PrePoMax, "
        "inch STEP scaled twice by 25.4, double inch-to-mm conversion, PrePoMax inch import 25.4x off"
    ),
)


def _render_u006() -> str:
    """Render a Part-21 with CONVERSION_BASED_UNIT INCH and mm coordinates (double-scale trigger)."""
    return (
        "ISO-10303-21;\n"
        "/* U006: PrePoMax double-applies inch->mm scaling on SolidWorks inch STEP */\n"
        "/* File declares CONVERSION_BASED_UNIT('INCH',...) with 25.4 mm factor */\n"
        "/* Coordinates are in mm (25.4 = 1 inch, 50.8 = 2 inches) */\n"
        "/* PrePoMax sees INCH unit and multiplies by 25.4 again => 25.4x too large */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U006: SolidWorks inch STEP; PrePoMax double-applies 25.4x factor'),'2;1');\n"
        "FILE_NAME('U006.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 1x2x1 inch part; coordinates in mm (25.4 mm = 1 in, 50.8 mm = 2 in) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(25.4,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.8,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(25.4,50.8,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: CONVERSION_BASED_UNIT declares INCH; coordinates are already in mm */\n"
        "/* PrePoMax applies the 25.4 inch->mm factor a second time => 25.4x too large */\n"
        "/* SI mm basis for the inch conversion factor */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* 1 inch = 25.4 mm — this is the conversion factor */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: CONVERSION_BASED_UNIT('INCH') triggers double-scaling in PrePoMax */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0254),#8,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('solidworks-inch-mm-coords',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u006(path) -> None:
    Path(path).write_text(_render_u006())


f.render = _render_u006  # type: ignore[method-assign]
f.write = _write_u006    # type: ignore[method-assign]
