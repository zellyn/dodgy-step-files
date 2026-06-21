"""Pmi120 — PROFILE_FEATURE with self-intersecting profile (figure-eight loop).

Catalog claim: AP242 profile_feature requires a simple non-self-intersecting
closed loop. This fixture emits a figure-eight: four vertices at
(5,5),(15,15),(5,15),(15,5) connected p0→p1→p2→p3→p0 — the diagonals cross.
Receivers must reject E_PROFILE_SELF_INTERSECT; never silently split.

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 4
  face[0].area > 2499 and < 2501

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi120",
    defect=(
        "profile_feature SHAPE_ASPECT with figure-eight self-intersecting "
        "profile: vertices (5,5),(15,15),(5,15),(15,5) connected p0→p1→p2→p3→p0; "
        "diagonals cross at (10,10)"
    ),
)

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

# DEFECT: figure-eight self-intersecting profile
host_asp    = f._emit_raw("SHAPE_ASPECT('host_face','',#9055,.T.)")
profile_asp = f._emit_raw("SHAPE_ASPECT('profile_feature','',#9055,.T.)")

# Four vertices forming a figure-eight (two diagonals that cross)
qA = f.cartesian_point((5.0, 5.0, 0.0))   # lower-left
qB = f.cartesian_point((15.0, 15.0, 0.0)) # upper-right
qC = f.cartesian_point((5.0, 15.0, 0.0))  # upper-left
qD = f.cartesian_point((15.0, 5.0, 0.0))  # lower-right
vA = f.vertex_point(qA); vB = f.vertex_point(qB)
vC = f.vertex_point(qC); vD = f.vertex_point(qD)

# Four line segments forming figure-eight: A→B, B→C, C→D, D→A
# A(5,5)→B(15,15): diagonal ↗
dAB = f.direction((1.0, 1.0, 0.0))
eAB = f.edge_curve(vA, vB, f.line(qA, f.vector(dAB, 14.14)))
# B(15,15)→C(5,15): left ←
dBC = f.direction((-1.0, 0.0, 0.0))
eBC = f.edge_curve(vB, vC, f.line(qB, f.vector(dBC, 10.0)))
# C(5,15)→D(15,5): diagonal ↘ — CROSSES A→B at (10,10)
dCD = f.direction((1.0, -1.0, 0.0))
eCD = f.edge_curve(vC, vD, f.line(qC, f.vector(dCD, 14.14)))
# D(15,5)→A(5,5): left ←
dDA = f.direction((-1.0, 0.0, 0.0))
eDA = f.edge_curve(vD, vA, f.line(qD, f.vector(dDA, 10.0)))

fig8_loop = f.edge_loop([
    f.oriented_edge(eAB, True), f.oriented_edge(eBC, True),
    f.oriented_edge(eCD, True), f.oriented_edge(eDA, True),
])
f._emit_raw(f"DIMENSIONAL_SIZE(#{profile_asp.eid},'sweep_depth')")
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('sweep_depth',LENGTH_MEASURE(5.0),#9056)"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('profile_on_face','profile on host',"
    f"#{host_asp.eid},#{profile_asp.eid})"
)
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('profile_gisu',$,#{profile_asp.eid},#9061,#{face.eid})"
)
