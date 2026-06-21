"""Pmi110 — COMPOSITE_FEATURE wrapping sub-features that share no host-shape boundary.

Catalog claim: AP242 composite_feature invariant requires wrapped sub-features
to share at least one host-shape boundary. This fixture emits a composite
SHAPE_ASPECT linked to two disjoint sub-feature regions with no shared edge.
Receivers must reject or warn W_COMPOSITE_BOUNDARY_MISSING.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi110",
    defect=(
        "composite_feature SHAPE_ASPECT wrapping two disjoint sub-features "
        "with composite_boundary_share='none'; sub-features reference separate "
        "non-adjacent regions with no shared edge/vertex"
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

# DEFECT: composite_feature with disjoint sub-features
host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
comp_asp    = f._emit_raw("SHAPE_ASPECT('composite_feature','',#9055,.T.)")
sub_asp_A   = f._emit_raw("SHAPE_ASPECT('sub_feature_A','region_A',#9055,.T.)")
sub_asp_B   = f._emit_raw("SHAPE_ASPECT('sub_feature_B','region_B',#9055,.T.)")
# No shared boundary — explicit marker
f._emit_raw("DESCRIPTIVE_REPRESENTATION_ITEM('composite_boundary_share','none')")
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('comp_has_A','composite contains A',"
    f"#{comp_asp.eid},#{sub_asp_A.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('comp_has_B','composite contains B',"
    f"#{comp_asp.eid},#{sub_asp_B.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('comp_gisu',$,#{comp_asp.eid},#9061,#{face.eid})"
)
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{comp_asp.eid},'composite_member_count')"
)
