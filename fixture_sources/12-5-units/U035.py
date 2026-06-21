"""U035 — Exporting ellipse with non-mm unit corrupts geometry.

Catalog claim: A document with LENGTH_UNIT = INCH containing an ellipse is exported.
The exporter emits the ellipse's semi-axes in millimetres (the internal representation
unit) but the file's declared unit is inches — re-import scales the values by 25.4x
incorrectly.

Reproducer recipe: Ellipse with semi-axes a=2.0, b=1.0 in inches. Exporter writes
a=2.0, b=1.0 in a file declaring INCH but the internal representation was in millimetres.

Byte assertions:
  contains(b'ELLIPSE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U035",
    defect=(
        "Exporting ellipse with non-mm unit corrupts geometry — semi-axes in wrong units; "
        "input: STEP file declaring CONVERSION_BASED_UNIT('INCH') with LENGTH_UNIT = INCH "
        "containing an ELLIPSE with semi-axes a=50.8 (2 inches in mm) and b=25.4 (1 inch in mm); "
        "exporter emits the ellipse's semi-axes in millimetres (internal representation) "
        "but the file's declared unit is inches — re-import scales the values by 25.4x incorrectly "
        "producing an ellipse 25.4x larger than intended; "
        "exporter must convert all numeric geometry attributes to the declared file unit before writing; "
        "never mix internal-representation units with the declared file unit; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: ellipse semi-axes in mm but STEP declares inch, ellipse exports with mismatched unit, "
        "STEP ellipse re-import 25.4x off, non-mm unit corrupts ellipse export, ELLIPSE coords wrong unit"
    ),
)


def _render_u035() -> str:
    """Render a Part-21 with ELLIPSE semi-axes in mm but file declares INCH unit."""
    return (
        "ISO-10303-21;\n"
        "/* U035: ELLIPSE semi-axes in mm but file declares INCH — 25.4x scale error on re-import */\n"
        "/* Exporter emits internal mm values without converting to declared file unit (INCH) */\n"
        "/* a=50.8 mm, b=25.4 mm are the mm representations of a=2.0, b=1.0 inch */\n"
        "/* DEFECT: file unit is INCH, but ellipse params are in mm — re-import scales by 25.4x */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U035: Ellipse semi-axes in mm but file declares INCH unit'),'2;1');\n"
        "FILE_NAME('U035.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* SI mm basis for conversion reference */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* INCH unit: 25.4 mm per inch */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* File declares INCH as active length unit */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(3.937E-5),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Ellipse placement: centred at origin in XY plane */\n"
        "#20=CARTESIAN_POINT('ellipse-centre',(0.,0.,0.));\n"
        "#21=DIRECTION('zdir',(0.,0.,1.));\n"
        "#22=DIRECTION('xdir',(1.,0.,0.));\n"
        "#23=AXIS2_PLACEMENT_3D('ellipse-placement',#20,#21,#22);\n"
        "/* DEFECT: semi-axes 50.8 and 25.4 are mm values (= 2.0 and 1.0 inch) */\n"
        "/* File unit is INCH so reader multiplies by 25.4 again -> 1289.32 x 645.16 */\n"
        "/* Correct: semi-axes should be 2.0 and 1.0 when file unit is INCH */\n"
        "#24=ELLIPSE('defect-ellipse',#23,50.8,25.4);\n"
        "/* Geometry set containing the mis-scaled ellipse */\n"
        "#25=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#26=CARTESIAN_POINT('ref-point',(2.0,1.0,0.));\n"
        "#30=GEOMETRIC_CURVE_SET('ellipse-wrong-unit',(#24,#25,#26));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u035(path) -> None:
    Path(path).write_text(_render_u035())


f.render = _render_u035  # type: ignore[method-assign]
f.write = _write_u035    # type: ignore[method-assign]
