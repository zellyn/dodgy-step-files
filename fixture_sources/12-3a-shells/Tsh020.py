"""Tsh020 — Edge appearing more than twice on faces (non-manifold T-junction).

Catalog claim: "For a 2-manifold solid, every edge must be incident to
exactly two faces. Schema validation flags edges that appear on only one
face (free / naked edge) or three or more faces (non-manifold T-junction)."

Demonstration: build a T-shaped sheet where one EDGE_CURVE is referenced
by THREE ORIENTED_EDGEs across three different face EDGE_LOOPs. A
schema-strict reader rejects; OCCT warns and reclassifies.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh020",
             defect="Edge appearing 3 times across faces (T-junction non-manifold)")

# Three coplanar rectangular faces sharing a single interior edge:
#
#   +------+------+
#   |  A   |  B   |
#   |      |      |
#   +------+------+
#         |
#         | (C glued underneath, sharing the AB-vertical edge)
#         |
#         +------+
#
# The central vertical edge (between p1 and p2) is part of A, B, and C's
# loops — referenced by 3 ORIENTED_EDGEs.

# Vertices for face A (left rectangle)
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = f.cartesian_point((1.0, 0.0, 0.0))  # shared with face B and C
pA2 = f.cartesian_point((1.0, 1.0, 0.0))  # shared with face B
pA3 = f.cartesian_point((0.0, 1.0, 0.0))
# Vertex for face B (right rectangle, extending from p1/p2)
pB1 = f.cartesian_point((2.0, 0.0, 0.0))
pB2 = f.cartesian_point((2.0, 1.0, 0.0))
# Vertex for face C (below the shared edge, also touching p1)
pC0 = f.cartesian_point((1.0, -1.0, 0.0))
pC1 = f.cartesian_point((2.0, -1.0, 0.0))

# The shared edge endpoints
vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2)
# Direction + line for the shared edge
shared_dir = f.direction((0.0, 1.0, 0.0))
shared_vec = f.vector(shared_dir, 1.0)
shared_line = f.line(pA1, shared_vec)
shared_edge = f.edge_curve(vA1, vA2, shared_line)

# Build the other edges of face A
loopA_others_dirs = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0)]
# Face A vertices + 3 non-shared edges
vA0 = f.vertex_point(pA0)
vA3 = f.vertex_point(pA3)

# A's bottom edge (pA0 → pA1)
d0 = f.direction((1.0, 0.0, 0.0)); ve = f.vector(d0, 1.0); ln = f.line(pA0, ve)
eA_bot = f.edge_curve(vA0, vA1, ln)
# A's top edge (pA2 → pA3)
d1 = f.direction((-1.0, 0.0, 0.0)); ve = f.vector(d1, 1.0); ln = f.line(pA2, ve)
eA_top = f.edge_curve(vA2, vA3, ln)
# A's left edge (pA3 → pA0)
d2 = f.direction((0.0, -1.0, 0.0)); ve = f.vector(d2, 1.0); ln = f.line(pA3, ve)
eA_left = f.edge_curve(vA3, vA0, ln)

# Face A loop uses shared_edge with .T. orientation
loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(shared_edge, True),  # ← 1st use of shared edge
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_left, True),
])

# Face B (right rectangle)
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)
d = f.direction((1.0, 0.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pA1, ve)
eB_bot = f.edge_curve(vA1, vB1, ln)
d = f.direction((0.0, 1.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pB1, ve)
eB_right = f.edge_curve(vB1, vB2, ln)
d = f.direction((-1.0, 0.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pB2, ve)
eB_top = f.edge_curve(vB2, vA2, ln)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_right, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(shared_edge, False),  # ← 2nd use of shared edge (reversed)
])

# Face C (glued underneath, sharing pA1 via vertical)
vC0 = f.vertex_point(pC0)
vC1 = f.vertex_point(pC1)
d = f.direction((1.0, 0.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pC0, ve)
eC_bot = f.edge_curve(vC0, vC1, ln)
d = f.direction((0.0, 1.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pC1, ve)
eC_right = f.edge_curve(vC1, vB1, ln)
d = f.direction((-1.0, 0.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pB1, ve)
eC_top = f.edge_curve(vB1, vA1, ln)
d = f.direction((0.0, -1.0, 0.0)); ve = f.vector(d, 1.0); ln = f.line(pA1, ve)
eC_left = f.edge_curve(vA1, vC0, ln)
loopC = f.edge_loop([
    f.oriented_edge(eC_bot, True),
    f.oriented_edge(eC_right, True),
    f.oriented_edge(shared_edge, False),  # ← 3rd use of shared edge (T-junction!)
    f.oriented_edge(eC_left, True),
])

# Place the plane and build faces
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)
faceC = f.advanced_face([f.face_outer_bound(loopC)], plane)

# Open shell (not closed — sheet topology). Shared edge appears in 3 loops.
shell = f.open_shell([faceA, faceB, faceC])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
