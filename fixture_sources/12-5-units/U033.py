"""U033 — Unit-default flag silently overridden by file's first unit-record.

Catalog claim: A reader configured with a default unit (xstep.cascade.unit) receives a STEP
file that emits an explicit LENGTH_UNIT record. The reader assumes the configured default but
the file's record overrides without warning; conversely, when the configured unit and the
file's unit disagree, the reader may apply the conversion factor twice.

Reproducer recipe: STEP file with explicit LENGTH_UNIT of inches; reader configured with
default xstep.cascade.unit = MM. Behaviour varies across versions (some apply file unit,
some apply default, some apply both as conversion).

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('INCH'")
  contains(b'INCH') and contains(b'25.4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U033",
    defect=(
        "Unit-default flag silently overridden by file's first unit-record; "
        "input: STEP file declaring CONVERSION_BASED_UNIT('INCH') with factor 25.4 mm; "
        "reader configured with default xstep.cascade.unit = MM; "
        "file's explicit LENGTH_UNIT of inches overrides the configured default without warning; "
        "across OCCT versions: some apply file unit, some apply default, some apply both as "
        "a double conversion (25.4 × 25.4 = 645.16 mm for a 1-inch value); "
        "kernel must use file-declared units as authoritative; the configured default applies "
        "only when the file omits the unit record; emit a diagnostic when the two disagree; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: xstep.cascade.unit overridden by file unit, default unit ignored when file "
        "declares unit, configured default conflicts with STEP unit, reader applies conversion "
        "twice, STEP unit default vs file divergence"
    ),
)


def _render_u033() -> str:
    """Render a Part-21 with explicit INCH unit that conflicts with MM reader default."""
    return (
        "ISO-10303-21;\n"
        "/* U033: Explicit INCH unit in file conflicts with reader default MM setting */\n"
        "/* xstep.cascade.unit = MM but file declares CONVERSION_BASED_UNIT('INCH',25.4) */\n"
        "/* DEFECT: reader may silently apply default MM, apply file INCH, or double-convert */\n"
        "/* Kernel must: use file-declared unit; warn when file and config disagree */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U033: INCH file unit vs MM reader default — silent override defect'),'2;1');\n"
        "FILE_NAME('U033.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 2x2x1 inch part; values are in inches */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(2.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,2.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,1.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(2.0,2.0,1.0));\n"
        "/* SI mm basis for conversion reference */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* INCH conversion: 25.4 mm per inch (correct factor) */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* File declares INCH as the active length unit */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.000393701),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* DEFECT: reader configured with MM default; file declares INCH */\n"
        "/* Some readers apply default (ignoring file), some double-convert, some warn */\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('inch-vs-mm-default',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u033(path) -> None:
    Path(path).write_text(_render_u033())


f.render = _render_u033  # type: ignore[method-assign]
f.write = _write_u033    # type: ignore[method-assign]
