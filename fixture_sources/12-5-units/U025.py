"""U025 — Reader API reports wrong primary length unit on multi-context files.

Catalog claim: The reader API entry point that returns the file's length unit reports a unit
different from the one the receiver actually applied to coordinates during transfer.
Downstream tools that read the reported unit and apply scaling produce wrong geometry.

Reproducer recipe: STEP with multiple length_unit records or with a
LENGTH_UNIT_AND_GLOBAL_UNIT_ASSIGNED_CONTEXT complex; the file-units query returns an
unrelated nested unit.

Byte assertions:
  count(b'LENGTH_UNIT()') >= 2
  count(b'LENGTH_UNIT') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U025",
    defect=(
        "Reader API reports wrong primary length unit on multi-context files; "
        "input: STEP file with multiple LENGTH_UNIT() instances — one in a standalone "
        "complex entity and a second embedded in a GLOBAL_UNIT_ASSIGNED_CONTEXT — "
        "causing the file-units query API to return a unit different from the one "
        "the receiver actually applied to coordinates during transfer; "
        "the file has two GEOMETRIC_REPRESENTATION_CONTEXT complexes: the primary one "
        "uses millimetres for geometry coordinates, and a secondary context embeds an "
        "additional LENGTH_UNIT() with an unrelated scale; "
        "the reader stepfileunits API walks the entity list and returns the secondary "
        "nested unit instead of the primary context's unit; "
        "downstream tools reading the reported unit and applying scaling produce "
        "geometry that is the right shape but the wrong scale; "
        "kernel must normalize the file-units query to walk the active context tree "
        "and return the unit actually applied to coordinates, not an arbitrary nested unit; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP reader returns wrong primary unit, stepfileunits returns wrong unit, "
        "file-units API inconsistent with applied unit, primary length unit mismatched, "
        "reader API unit query wrong"
    ),
)


def _render_u025() -> str:
    """Render a Part-21 with two LENGTH_UNIT() instances causing wrong API report."""
    return (
        "ISO-10303-21;\n"
        "/* U025: Multiple LENGTH_UNIT() records cause reader API to report wrong primary unit */\n"
        "/* Primary context uses mm; secondary context has an extra LENGTH_UNIT() for metres */\n"
        "/* stepfileunits API returns the wrong (secondary) unit instead of mm */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U025: Multi-context file with wrong primary length unit from API'),'2;1');\n"
        "FILE_NAME('U025.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 50x50x25 mm part */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Primary context: mm (the unit actually applied to coordinates) */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('3D Dimensions','3D'));\n"
        "/* DEFECT: secondary context with extra LENGTH_UNIT() in metres */\n"
        "/* Reader API may pick this up and report metre as the primary unit */\n"
        "#20=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#21=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#23=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#20,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* Second GEOMETRIC_REPRESENTATION_CONTEXT with metre LENGTH_UNIT */\n"
        "#24=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#23))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#20,#21,#22)) REPRESENTATION_CONTEXT('CGR','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#30=GEOMETRIC_CURVE_SET('multi-context-wrong-api-unit',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u025(path) -> None:
    Path(path).write_text(_render_u025())


f.render = _render_u025  # type: ignore[method-assign]
f.write = _write_u025    # type: ignore[method-assign]
