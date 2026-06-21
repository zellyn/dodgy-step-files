"""U020 — Validation properties (mass/area/volume) emitted with units mismatched to GRC.

Catalog claim: Validation properties (volume, surface area, centroid) emitted with measure
units that don't match the model's GEOMETRIC_REPRESENTATION_CONTEXT; or with no unit_component
at all.

Reproducer recipe: XCAF with validation properties exported in non-mm units while geometry
GRC is mm; or MEASURE_REPRESENTATION_ITEM with no unit_component reference.

Byte assertions:
  contains(b'AREA_MEASURE') or contains(b'VOLUME_MEASURE')
  contains(b'MEASURE_REPRESENTATION_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U020",
    defect=(
        "Validation properties (mass/area/volume) emitted with units mismatched to GRC; "
        "input: XCAF document with validation properties exported in non-mm units while "
        "geometry GEOMETRIC_REPRESENTATION_CONTEXT (GRC) is in mm; "
        "MEASURE_REPRESENTATION_ITEM entities carry AREA_MEASURE and VOLUME_MEASURE values "
        "computed in a different unit than the geometry's mm context; "
        "a kernel comparing validation properties against reconstructed geometry will see "
        "a factor-of-1000 (or 1e6) discrepancy for length vs area vs volume measures; "
        "or MEASURE_REPRESENTATION_ITEM has no unit_component reference at all, "
        "making the numeric value dimensionless and uninterpretable; "
        "kernel must normalize emit / validate to the same unit on validation properties "
        "as on geometry; coerce unit_component to be present and consistent; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: validation properties units mismatch GRC, mass area volume in different unit "
        "than geometry, MEASURE_REPRESENTATION_ITEM no unit_component, "
        "STEP validation property unit drift, validation property unit not consistent"
    ),
)


def _render_u020() -> str:
    """Render a Part-21 with MEASURE_REPRESENTATION_ITEM using mismatched units."""
    return (
        "ISO-10303-21;\n"
        "/* U020: Validation properties (area/volume) with units mismatched to geometry GRC */\n"
        "/* Geometry context is mm; validation properties use metre-based measures */\n"
        "/* Also: one MEASURE_REPRESENTATION_ITEM has no unit_component reference */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U020: Validation property units mismatched to GRC'),'2;1');\n"
        "FILE_NAME('U020.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 50x50x10 mm block */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,10.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,10.0));\n"
        "/* Geometry context: mm */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Main model entity */\n"
        "#20=GEOMETRIC_CURVE_SET('geometry',(#1,#2,#3,#4,#5));\n"
        "/* DEFECT: Validation-property context uses METRE (not MILLI METRE) */\n"
        "/* Area: 50x50 mm = 2500 mm^2, but emitted as 0.0025 m^2 in a metre context */\n"
        "#30=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "/* DEFECT: AREA_MEASURE uses metre-squared unit — mismatched to mm GRC */\n"
        "#31=(AREA_UNIT() NAMED_UNIT(*) SI_UNIT($,.SQUARE_METRE.));\n"
        "/* DEFECT: VOLUME_MEASURE uses metre-cubed unit — mismatched to mm GRC */\n"
        "#32=(NAMED_UNIT(*) SI_UNIT($,.CUBIC_METRE.) VOLUME_UNIT());\n"
        "/* Validation property: surface area in m^2 (should be mm^2 to match GRC) */\n"
        "#40=MEASURE_WITH_UNIT(AREA_MEASURE(2.5E-3),#31);\n"
        "#41=MEASURE_REPRESENTATION_ITEM('surface_area',AREA_MEASURE(2.5E-3),#31);\n"
        "/* Validation property: volume in m^3 (should be mm^3 to match GRC) */\n"
        "#42=MEASURE_WITH_UNIT(VOLUME_MEASURE(2.5E-5),#32);\n"
        "#43=MEASURE_REPRESENTATION_ITEM('volume',VOLUME_MEASURE(2.5E-5),#32);\n"
        "/* DEFECT: centroid item with no unit_component reference -- dimensionless value */\n"
        "#44=MEASURE_REPRESENTATION_ITEM('centroid_x',LENGTH_MEASURE(25.0),$);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u020(path) -> None:
    Path(path).write_text(_render_u020())


f.render = _render_u020  # type: ignore[method-assign]
f.write = _write_u020    # type: ignore[method-assign]
