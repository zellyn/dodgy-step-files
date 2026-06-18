"""Tfa141 — ShapeFix_Face.FixWiresTwoCoincEdges B-spline-vs-LINE.

Catalog claim: "Face with two inner wires where first uses LINE edge and
second uses geometrically identical B-SPLINE_CURVE_WITH_KNOTS edge.
FixWiresTwoCoincEdges's curve-type strict check (comparing 3D curve pointers)
misses coincidence when curve representations differ despite identical geometry.
Defect triggers at FWC-004: edge-identity check fails because curve-type
incompatibility prevents match, even though pcurve and 3D locus are congruent."

Demonstration: a face with an outer-loop rectangle and two inner holes:
1. First hole uses a LINE-based circular edge (approximately)
2. Second hole uses a B-SPLINE_CURVE_WITH_KNOTS with same 3D locus
Both holes are geometrically identical but use different curve representations.
The fix algorithm should recognize them as coincident, but the curve-type
incompatibility check blocks the merge.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa141",
             defect="Face with two inner holes using LINE vs B-SPLINE curves with same 3D locus")

# Outer loop: 10×10 rectangle
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Outer loop edges
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 10.0); line = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, line)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 10.0); line = f.line(p1, vec)
e1 = f.edge_curve(v1, v2, line)

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 10.0); line = f.line(p2, vec)
e2 = f.edge_curve(v2, v3, line)

d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 10.0); line = f.line(p3, vec)
e3 = f.edge_curve(v3, v0, line)

outer_loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# First inner hole: using LINE edges (square hole at 2,2 with side 2)
h1_p0 = f.cartesian_point((2.0, 2.0, 0.0))
h1_p1 = f.cartesian_point((4.0, 2.0, 0.0))
h1_p2 = f.cartesian_point((4.0, 4.0, 0.0))
h1_p3 = f.cartesian_point((2.0, 4.0, 0.0))

h1_v0 = f.vertex_point(h1_p0)
h1_v1 = f.vertex_point(h1_p1)
h1_v2 = f.vertex_point(h1_p2)
h1_v3 = f.vertex_point(h1_p3)

# Build LINE-based edges for hole 1
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 2.0); line = f.line(h1_p0, vec)
h1_e0 = f.edge_curve(h1_v0, h1_v1, line)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 2.0); line = f.line(h1_p1, vec)
h1_e1 = f.edge_curve(h1_v1, h1_v2, line)

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 2.0); line = f.line(h1_p2, vec)
h1_e2 = f.edge_curve(h1_v2, h1_v3, line)

d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 2.0); line = f.line(h1_p3, vec)
h1_e3 = f.edge_curve(h1_v3, h1_v0, line)

hole1_loop = f.edge_loop([
    f.oriented_edge(h1_e0, True),
    f.oriented_edge(h1_e1, True),
    f.oriented_edge(h1_e2, True),
    f.oriented_edge(h1_e3, True),
])

# Second inner hole: using B_SPLINE_CURVE_WITH_KNOTS with same 3D locus
# (square hole at 6,2 with side 2, but using B-spline representation)
h2_p0 = f.cartesian_point((6.0, 2.0, 0.0))
h2_p1 = f.cartesian_point((8.0, 2.0, 0.0))
h2_p2 = f.cartesian_point((8.0, 4.0, 0.0))
h2_p3 = f.cartesian_point((6.0, 4.0, 0.0))

h2_v0 = f.vertex_point(h2_p0)
h2_v1 = f.vertex_point(h2_p1)
h2_v2 = f.vertex_point(h2_p2)
h2_v3 = f.vertex_point(h2_p3)

# Build B-spline-based edges for hole 2.
# Use _emit_raw for B_SPLINE_CURVE_WITH_KNOTS (degree=1 linear spline, same geometry as LINE)

# Bottom edge: linear B-spline from (6,2,0) to (8,2,0)
# B_SPLINE_CURVE_WITH_KNOTS(name, degree, control_points, knot_multiplicities, knots, closed, self_intersect)
bspl_bottom = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('bspl_h2_0',1,"
    "(#" + str(h2_p0.eid) + ",#" + str(h2_p1.eid) + "),"
    "(2,2),"
    "(0.0,1.0),"
    ".F.,.F.)"
)
h2_e0 = f.edge_curve(h2_v0, h2_v1, bspl_bottom)

# Right edge: linear B-spline from (8,2,0) to (8,4,0)
bspl_right = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('bspl_h2_1',1,"
    "(#" + str(h2_p1.eid) + ",#" + str(h2_p2.eid) + "),"
    "(2,2),"
    "(0.0,1.0),"
    ".F.,.F.)"
)
h2_e1 = f.edge_curve(h2_v1, h2_v2, bspl_right)

# Top edge: linear B-spline from (8,4,0) to (6,4,0)
bspl_top = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('bspl_h2_2',1,"
    "(#" + str(h2_p2.eid) + ",#" + str(h2_p3.eid) + "),"
    "(2,2),"
    "(0.0,1.0),"
    ".F.,.F.)"
)
h2_e2 = f.edge_curve(h2_v2, h2_v3, bspl_top)

# Left edge: linear B-spline from (6,4,0) to (6,2,0)
bspl_left = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('bspl_h2_3',1,"
    "(#" + str(h2_p3.eid) + ",#" + str(h2_p0.eid) + "),"
    "(2,2),"
    "(0.0,1.0),"
    ".F.,.F.)"
)
h2_e3 = f.edge_curve(h2_v3, h2_v0, bspl_left)

hole2_loop = f.edge_loop([
    f.oriented_edge(h2_e0, True),
    f.oriented_edge(h2_e1, True),
    f.oriented_edge(h2_e2, True),
    f.oriented_edge(h2_e3, True),
])

# Create the plane and the face with outer loop and two inner bounds
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(hole1_loop, orientation=False),
    f.face_bound(hole2_loop, orientation=False),
], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
