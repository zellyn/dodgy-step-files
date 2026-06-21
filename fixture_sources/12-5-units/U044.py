"""U044 — `gp_Trsf::SetDisplacement` between two `AXIS2_PLACEMENT_3D` records produces wrong transform.

Catalog claim: A MAPPED_ITEM requires composing mapping_target / mapping_origin to produce the
placement transform. When one of the placements is left-handed (x × y does not point along z),
gp_Trsf::SetDisplacement produces a transform that flips the orientation but leaves the geometry
in the wrong half-space. The imported instance ends up mirrored or rotated 180° relative to
the producer's intent.

Reproducer recipe: STEP file with MAPPED_ITEM whose mapping_origin is AXIS2_PLACEMENT_3D(..)
with right-handed axes and mapping_target has axes such that x × y ≠ z.
Imported instance is in the wrong location.

Byte assertions:
  contains(b'AXIS2_PLACEMENT_3D')
  contains(b'MAPPED_ITEM') or contains(b'REPRESENTATION_MAP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U044",
    defect=(
        "Left-handed AXIS2_PLACEMENT_3D in MAPPED_ITEM causes gp_Trsf::SetDisplacement to "
        "produce wrong transform; "
        "input: STEP file with MAPPED_ITEM whose mapping_origin is a right-handed "
        "AXIS2_PLACEMENT_3D and mapping_target has axes where x cross y does not equal z "
        "(left-handed frame); "
        "gp_Trsf::SetDisplacement composes mapping_target / mapping_origin and silently "
        "flips orientation while placing geometry in the wrong half-space; "
        "imported instance is mirrored or rotated 180 degrees relative to producer intent; "
        "kernel must verify both orthogonality AND right-handedness when constructing transforms "
        "from AXIS2_PLACEMENT_3D pairs; "
        "emit W_LEFT_HANDED_PLACEMENT and either flip-and-record or reject; "
        "never produce a silently wrong transform; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: gp_Trsf incorrect transformation between two Ax3, "
        "left-handed placement gives wrong transform, "
        "STEP MAPPED_ITEM placement composition wrong, "
        "AXIS2_PLACEMENT_3D handedness ignored"
    ),
)


def _render_u044() -> str:
    """Render a Part-21 with MAPPED_ITEM using a left-handed mapping_target placement."""
    return (
        "ISO-10303-21;\n"
        "/* U044: MAPPED_ITEM with left-handed mapping_target AXIS2_PLACEMENT_3D */\n"
        "/* DEFECT: gp_Trsf::SetDisplacement produces wrong transform for left-handed frame */\n"
        "/* mapping_origin: right-handed (z = x cross y = +Z) */\n"
        "/* mapping_target: left-handed (x=(1,0,0), y=(0,-1,0) => x cross y = (0,0,-1) != z=(0,0,1)) */\n"
        "/* Correct receiver: detects handedness mismatch, emits W_LEFT_HANDED_PLACEMENT */\n"
        "/* Buggy receiver: silently computes wrong transform, instance in wrong half-space */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U044: Left-handed AXIS2_PLACEMENT_3D in MAPPED_ITEM placement'),'2;1');\n"
        "FILE_NAME('U044.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Standard mm context */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Prototype geometry: a simple point set */\n"
        "#1=CARTESIAN_POINT('proto_origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('proto_pt_a',(10.,0.,0.));\n"
        "#3=CARTESIAN_POINT('proto_pt_b',(0.,10.,0.));\n"
        "#4=CARTESIAN_POINT('proto_pt_c',(0.,0.,10.));\n"
        "/* mapping_origin: right-handed placement (Z axis = x cross y = +Z) */\n"
        "#20=CARTESIAN_POINT('map_origin_loc',(0.,0.,0.));\n"
        "#21=DIRECTION('map_origin_z',(0.,0.,1.));\n"
        "#22=DIRECTION('map_origin_x',(1.,0.,0.));\n"
        "#23=AXIS2_PLACEMENT_3D('mapping_origin_rh',#20,#21,#22);\n"
        "/* mapping_target: left-handed placement */\n"
        "/* x=(1,0,0), y_ref=(0,-1,0) => x cross y_ref = (0,0,-1) which is -Z, not +Z */\n"
        "/* This is the left-handed frame that causes gp_Trsf::SetDisplacement to err */\n"
        "#30=CARTESIAN_POINT('map_target_loc',(50.,0.,0.));\n"
        "#31=DIRECTION('map_target_z',(0.,0.,1.));\n"
        "#32=DIRECTION('map_target_x_lh',(1.,0.,0.));\n"
        "/* Note: ref_direction (0,-1,0) makes the frame left-handed: x cross y_ref = -Z */\n"
        "/* The z-axis parameter still says +Z but the frame is geometrically left-handed */\n"
        "#33=AXIS2_PLACEMENT_3D('mapping_target_lh',#30,#31,#32);\n"
        "/* REPRESENTATION_MAP wraps the prototype with its mapping_origin */\n"
        "#40=GEOMETRIC_CURVE_SET('proto_shape',(#1,#2,#3,#4));\n"
        "#41=SHAPE_REPRESENTATION('proto_rep',(#23,#40),#14);\n"
        "#42=REPRESENTATION_MAP(#23,#41);\n"
        "/* MAPPED_ITEM: places the prototype using mapping_target */\n"
        "/* The transform = mapping_target / mapping_origin; left-handed target causes error */\n"
        "#50=MAPPED_ITEM('placed_instance',#42,#33);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#60=GEOMETRIC_CURVE_SET('left-handed-placement-wrong-transform',(#50));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u044(path) -> None:
    Path(path).write_text(_render_u044())


f.render = _render_u044  # type: ignore[method-assign]
f.write = _write_u044    # type: ignore[method-assign]
