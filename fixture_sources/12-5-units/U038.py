"""U038 — STEP read produces unexpectedly enormous scaling on parts (MAPPED_ITEM cross-context unit composition error).

Catalog claim: A STEP file declares millimetres, but an internal MAPPED_ITEM chain composes
scale factors where a parent reuses a child via a scaled placement. The reader composes the
scales correctly for translation but applies them as additional unit conversions, producing
parts kilometres in size.

Reproducer recipe: STEP file with LENGTH_UNIT = MM, root part containing a MAPPED_ITEM
whose source has unit metres. Reader composes scale = 1000 x 1000 = 1e6.

Byte assertions:
  contains(b'MAPPED_ITEM')
  contains(b'.MILLI.') and contains(b'.METRE.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U038",
    defect=(
        "MAPPED_ITEM cross-context unit composition error — reader compounds scale 1000x1000 = 1e6; "
        "input: STEP file with LENGTH_UNIT = millimetres at the root GEOMETRIC_REPRESENTATION_CONTEXT "
        "and a MAPPED_ITEM whose source REPRESENTATION_MAP was authored in metres; "
        "the outer context is mm (SI_UNIT(.MILLI.,.METRE.)) and the REPRESENTATION_MAP source "
        "carries its own GEOMETRIC_REPRESENTATION_CONTEXT in metres (SI_UNIT($,.METRE.)); "
        "a conformant reader applies unit normalisation at the leaf level only: "
        "the MAPPED_ITEM placement compose as affine transforms, not as additional unit factors; "
        "a buggy reader re-applies the 1000x unit conversion on top of the MAPPED_ITEM transform, "
        "yielding an effective scale of 1000 * 1000 = 1e6 (part appears kilometres in size); "
        "kernel must heal: normalise the unit-conversion factor exactly once at the leaf representation; "
        "MAPPED_ITEM placements compose as transforms only, never as additional unit factors; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: MAPPED_ITEM cross-context unit composition, STEP scales composed as additional units, "
        "model kilometres in size from MAPPED_ITEM, 1000x1000 unit composition error, "
        "cross-context REPRESENTATION_MAP unit bug"
    ),
)


def _render_u038() -> str:
    """Render a Part-21 with MAPPED_ITEM spanning mm outer context and metre source context."""
    return (
        "ISO-10303-21;\n"
        "/* U038: MAPPED_ITEM cross-context unit composition error */\n"
        "/* Root context: mm; REPRESENTATION_MAP source context: metres */\n"
        "/* DEFECT: buggy reader re-applies 1000x unit factor on MAPPED_ITEM placement */\n"
        "/* Correct: unit factor applied once at leaf level; MAPPED_ITEM is a transform only */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U038: MAPPED_ITEM target mm vs source metre cross-context unit composition'),'2;1');\n"
        "FILE_NAME('U038.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Root geometry context: millimetres */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* Root context in mm (MILLI METRE) */\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('root_mm','3D'));\n"
        "/* Source REPRESENTATION_MAP context: metres (no prefix) */\n"
        "#20=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#21=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#23=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#20,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* DEFECT: source context is metres — 1000x mismatch with root mm context */\n"
        "#24=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#23))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#20,#21,#22)) REPRESENTATION_CONTEXT('source_m','3D'));\n"
        "/* Source geometry in metres: 0.05m = 50mm cube */\n"
        "#30=CARTESIAN_POINT('src_origin',(0.,0.,0.));\n"
        "#31=CARTESIAN_POINT('src_corner_x',(0.05,0.,0.));\n"
        "#32=CARTESIAN_POINT('src_corner_y',(0.,0.05,0.));\n"
        "#33=CARTESIAN_POINT('src_corner_z',(0.,0.,0.025));\n"
        "#34=CARTESIAN_POINT('src_corner_xyz',(0.05,0.05,0.025));\n"
        "/* Source SHAPE_REPRESENTATION in metre context */\n"
        "#35=GEOMETRIC_CURVE_SET('source_geometry_in_metres',(#30,#31,#32,#33,#34));\n"
        "/* REPRESENTATION_MAP wraps source geometry in metre context */\n"
        "/* DEFECT: REPRESENTATION_MAP source carries metre context; parent root uses mm */\n"
        "#40=DIRECTION('x_axis',(1.,0.,0.));\n"
        "#41=DIRECTION('z_axis',(0.,0.,1.));\n"
        "#42=CARTESIAN_POINT('map_origin',(0.,0.,0.));\n"
        "#43=AXIS2_PLACEMENT_3D('map_origin_placement',#42,#41,#40);\n"
        "#44=REPRESENTATION_MAP(#43,#35);\n"
        "/* MAPPED_ITEM in root mm context references the REPRESENTATION_MAP from metre context */\n"
        "/* A correct reader applies unit conversion at leaf level only */\n"
        "/* A buggy reader applies 1000x TWICE: once for mm->m and once more via MAPPED_ITEM */\n"
        "#50=DIRECTION('x_axis_root',(1.,0.,0.));\n"
        "#51=DIRECTION('z_axis_root',(0.,0.,1.));\n"
        "#52=CARTESIAN_POINT('mapped_origin',(10.,0.,0.));\n"
        "#53=AXIS2_PLACEMENT_3D('mapped_placement',#52,#51,#50);\n"
        "/* MAPPED_ITEM: source uses metres; target root context uses mm */\n"
        "#54=MAPPED_ITEM('cross_context_map',#44,#53);\n"
        "/* Root model entity with GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#60=GEOMETRIC_CURVE_SET('root_mm_entity',(#54));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u038(path) -> None:
    Path(path).write_text(_render_u038())


f.render = _render_u038  # type: ignore[method-assign]
f.write = _write_u038    # type: ignore[method-assign]
