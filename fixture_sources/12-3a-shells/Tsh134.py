"""Tsh134 — CheckOrientedShells edge-tolerance.

Catalog claim: "Shell with two adjacent faces sharing an edge within geometric
tolerance (1.0E-7mm) but with slightly offset vertex positions (within tolerance,
but identity-mismatch triggers false-positive). Tests ShapeAnalysis_Shell::
CheckOrientedShells vertex-matching using identity rather than tolerance-aware
comparison."

Demonstration: build two rectangular faces that share one edge. The shared edge
vertices have the SAME 3D coordinates but belong to DIFFERENT VERTEX_POINT entities.
The vertices are mathematically coincident (within tolerance) but have distinct IDs.
This triggers the identity-mismatch defect in CheckOrientedShells, which should
use tolerance-aware comparison instead of entity ID equality.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh134",
             defect="Two faces with shared edge where vertices are coincident in 3D but distinct entities")

# Create two rectangular faces sharing an edge.
# The shared edge will have vertices that are geometrically identical but
# represented by different VERTEX_POINT entities.

# Face A: rectangle 1 at z=0
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = f.cartesian_point((1.0, 0.0, 0.0))  # Shared edge endpoint (A's side)
pA2 = f.cartesian_point((1.0, 1.0, 0.0))  # Shared edge endpoint (A's side)
pA3 = f.cartesian_point((0.0, 1.0, 0.0))

vA0 = f.vertex_point(pA0)
vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2)
vA3 = f.vertex_point(pA3)

# Build edges for Face A
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pA0, vec)
eA_bot = f.edge_curve(vA0, vA1, line)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pA1, vec)
eA_right_shared = f.edge_curve(vA1, vA2, line)  # This is the SHARED edge

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pA2, vec)
eA_top = f.edge_curve(vA2, vA3, line)

d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pA3, vec)
eA_left = f.edge_curve(vA3, vA0, line)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(eA_right_shared, True),
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_left, True),
])

# Face B: rectangle 2 at z=0, adjacent to Face A (sharing the right edge of A).
# Its left edge is geometrically identical to A's right edge, but uses DIFFERENT
# VERTEX_POINT entities pointing to EQUIVALENT (but distinct) CARTESIAN_POINTS.
pB0 = f.cartesian_point((1.0, 0.0, 0.0))   # Coincident with pA1, but distinct entity
pB1 = f.cartesian_point((2.0, 0.0, 0.0))
pB2 = f.cartesian_point((2.0, 1.0, 0.0))
pB3 = f.cartesian_point((1.0, 1.0, 0.0))   # Coincident with pA2, but distinct entity

vB0 = f.vertex_point(pB0)
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)
vB3 = f.vertex_point(pB3)

# Build edges for Face B
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pB0, vec)
eB_bot = f.edge_curve(vB0, vB1, line)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pB1, vec)
eB_right = f.edge_curve(vB1, vB2, line)

d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pB2, vec)
eB_top = f.edge_curve(vB2, vB3, line)

d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pB3, vec)
eB_left_shared = f.edge_curve(vB3, vB0, line)  # B's left = A's right (geometrically)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_right, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(eB_left_shared, True),
])

# Create the shared plane for both faces
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

# Open shell containing both faces
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
