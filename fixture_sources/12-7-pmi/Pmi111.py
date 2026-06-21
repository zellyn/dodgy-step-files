"""Pmi111 — COMPOSITE_FEATURE with cyclic sub-feature reference (A → B → A).

Catalog claim: AP242 SHAPE_ASPECT_RELATIONSHIP graph must be acyclic. This
fixture creates a two-node cycle: SAR(A→B) and SAR(B→A). Receivers must
detect the cycle with E_COMPOSITE_CYCLE; never silently break it.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=signal(11) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi111",
    defect=(
        "SHAPE_ASPECT_RELATIONSHIP cycle: composite_A references composite_B as "
        "sub-feature and composite_B references composite_A as sub-feature; "
        "two-node cycle in feature membership graph"
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

# DEFECT: cyclic SHAPE_ASPECT_RELATIONSHIP (A→B and B→A)
comp_A = f._emit_raw("SHAPE_ASPECT('composite_A','composite node A',#9055,.T.)")
comp_B = f._emit_raw("SHAPE_ASPECT('composite_B','composite node B',#9055,.T.)")
# A → B (A claims B as sub-feature)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('A_has_B','A has sub B',"
    f"#{comp_A.eid},#{comp_B.eid})"
)
# B → A (B claims A as sub-feature) — creates cycle
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('B_has_A','B has sub A',"
    f"#{comp_B.eid},#{comp_A.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('compA_gisu',$,#{comp_A.eid},#9061,#{face.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('compB_gisu',$,#{comp_B.eid},#9061,#{face.eid})"
)
f._emit_raw(f"DIMENSIONAL_SIZE(#{comp_A.eid},'composite_cycle_depth')")
