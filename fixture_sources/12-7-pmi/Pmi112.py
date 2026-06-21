"""Pmi112 — COMPOSITE_FEATURE depth-attribute conflict between parent and sub-feature.

Catalog claim: AP242 composite_feature invariant: sub-feature depth must not
exceed parent depth. This fixture emits composite_slot depth=5.0 mm with a
child sub_groove depth=8.0 mm (greater than parent). Receivers must reject or
warn W_COMPOSITE_DEPTH_CONFLICT and clamp to parent depth.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi112",
    defect=(
        "composite_slot SHAPE_ASPECT depth=5.0 mm; child sub_groove depth=8.0 mm; "
        "sub-feature depth (8) exceeds parent depth (5) — sub-groove punches "
        "through slot floor"
    ),
)

# 50x50 mm planar face
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((50.0, 0.0, 0.0))
p2 = f.cartesian_point((50.0, 50.0, 0.0)); p3 = f.cartesian_point((0.0, 50.0, 0.0))
loop = f.closed_polyline_loop([p0, p1, p2, p3])
face = f.advanced_face([f.face_outer_bound(loop)], plane, name="host_face")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# DEFECT: composite depth conflict (sub-feature depth > parent depth)
host_asp   = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
parent_asp = f._emit_raw("SHAPE_ASPECT('composite_slot','',#9055,.T.)")
child_asp  = f._emit_raw("SHAPE_ASPECT('sub_groove','',#9055,.T.)")

# parent depth = 5 mm
f._emit_raw(f"DIMENSIONAL_SIZE(#{parent_asp.eid},'depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('parent_depth',LENGTH_MEASURE(5.0),#9056)"
)
# child depth = 8 mm — EXCEEDS parent depth (defect)
f._emit_raw(f"DIMENSIONAL_SIZE(#{child_asp.eid},'depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('child_depth',LENGTH_MEASURE(8.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('slot_has_groove','composite slot has sub groove',"
    f"#{parent_asp.eid},#{child_asp.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('parent_on_face','composite on host',"
    f"#{host_asp.eid},#{parent_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('comp_gisu',$,#{parent_asp.eid},#9061,#{face.eid})"
)
