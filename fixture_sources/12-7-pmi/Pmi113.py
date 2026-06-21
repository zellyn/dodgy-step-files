"""Pmi113 — COMPOSITE_FEATURE with empty sub-features list.

Catalog claim: AP242 composite_feature must wrap two-or-more sub-features.
This fixture emits a composite SHAPE_ASPECT with zero incoming
SHAPE_ASPECT_RELATIONSHIP records (empty membership). Receivers must reject
or drop with W_COMPOSITE_EMPTY.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi113",
    defect=(
        "composite_feature SHAPE_ASPECT with zero SHAPE_ASPECT_RELATIONSHIP "
        "records linking sub-features to it — empty composite membership list; "
        "composite_member_count='0'"
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

# DEFECT: composite_feature with no sub-feature relationships
host_asp  = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
comp_asp  = f._emit_raw("SHAPE_ASPECT('composite_feature_empty','',#9055,.T.)")
# Explicit marker: zero sub-features
f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('composite_member_count','0')"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('comp_on_face','composite on host',"
    f"#{host_asp.eid},#{comp_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('comp_gisu',$,#{comp_asp.eid},#9061,#{face.eid})"
)
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{comp_asp.eid},'composite_depth')"
)
