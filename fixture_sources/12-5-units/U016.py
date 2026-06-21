"""U016 — Duplicate CONVERSION_BASED_UNIT 'INCH' instances (factor 25.4) in dimension export.

Catalog claim: Writing dimensions in inches produces STEP files with invalid cross-references
between dimension entities. Common signature: two separate CONVERSION_BASED_UNIT('INCH', ..)
instances (different #NNN ids) both defined with the same conversion factor 25.4, with
different LENGTH_MEASURE_WITH_UNIT records pointing at one or the other; duplicate unit
definitions reused inconsistently across multiple measures.

Reproducer recipe: XCAF document with dimensions in inch units; export to STEP.

Byte assertions:
  count(b"CONVERSION_BASED_UNIT('INCH'") >= 2
  count(b"'INCH'") >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U016",
    defect=(
        "Duplicate CONVERSION_BASED_UNIT 'INCH' instances (factor 25.4) cause invalid cross-references; "
        "input: XCAF document with dimensions in inch units exported to STEP via OCCT; "
        "common signature: two separate CONVERSION_BASED_UNIT('INCH',#NNN) instances with "
        "different entity IDs but the same conversion factor 25.4; "
        "different LENGTH_MEASURE_WITH_UNIT records point at one instance or the other "
        "creating inconsistent cross-references across multiple dimension measures; "
        "a kernel reading these inconsistent references cannot canonicalize the inch unit "
        "and may fail to resolve dimensions or apply the wrong scale to some; "
        "kernel must normalize to a single CONVERSION_BASED_UNIT instance for a given "
        "unit name and factor; emit a diagnostic on redundant duplicate definitions; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: duplicate INCH CONVERSION_BASED_UNIT instances, two #N for same INCH unit, "
        "duplicate inch unit definitions in STEP, dimension export uses inconsistent inch units, "
        "redundant INCH conversion entities"
    ),
)


def _render_u016() -> str:
    """Render a Part-21 with two distinct CONVERSION_BASED_UNIT('INCH') instances."""
    return (
        "ISO-10303-21;\n"
        "/* U016: Duplicate CONVERSION_BASED_UNIT('INCH') instances in dimension export */\n"
        "/* OCCT XCAF inch dimension export creates two separate INCH unit entities */\n"
        "/* Both carry conversion factor 25.4 but have different #NNN ids */\n"
        "/* Dimension measures use one or the other inconsistently -- invalid cross-refs */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U016: Duplicate INCH CONVERSION_BASED_UNIT in dimension export'),'2;1');\n"
        "FILE_NAME('U016.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: a simple 2-inch square part (coordinates in mm: 50.8 mm = 2 inches) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.8,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.8,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.8,50.8,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* SI mm basis for inch conversion */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* DEFECT: two separate LENGTH_MEASURE_WITH_UNIT records for the same 25.4 factor */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "#30=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: two separate CONVERSION_BASED_UNIT('INCH') instances with different ids */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#31=(CONVERSION_BASED_UNIT('INCH',#30) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0254),#8,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Dimension measures: each references a different INCH unit instance */\n"
        "/* This is the signature of the OCCT dimension export bug */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('width',LENGTH_MEASURE(2.0),#10);\n"
        "#41=MEASURE_REPRESENTATION_ITEM('height',LENGTH_MEASURE(1.0),#31);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('xcaf-dup-inch-unit',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u016(path) -> None:
    Path(path).write_text(_render_u016())


f.render = _render_u016  # type: ignore[method-assign]
f.write = _write_u016    # type: ignore[method-assign]
