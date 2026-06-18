"""Tsh135 — ShapeUpgrade_ShellSewing.Apply face-with-multiple-edges-to-merge.

Catalog claim: "Two faces with three edges each that should all sew; Apply
merges first matching edge-pair and ignores remaining two edges. Tests
ShapeUpgrade_ShellSewing::Apply incomplete multi-edge merge detection."

Demonstration: build two rectangular faces where all three "adjacent" edges
match geometrically (same endpoints, same curve), but are represented as
distinct EDGE_CURVE entities. The sewing algorithm should merge all three
edge pairs, but the defect causes it to stop after the first match, leaving
two edges unmerged.

To create three shared edges between two faces:
- Face A and Face B share edges A-B (segment 1), B-C (segment 2), C-A (segment 3)
- We'll use three distinct EDGE_CURVE objects with the same geometry
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh135",
             defect="Two faces each with three edges that should all sew but only first is merged")

# Create three shared vertices (A, B, C forming a triangle-ish arrangement)
# We'll construct two faces that both reference these vertices with three edges each.

# Common vertices
pA = f.cartesian_point((0.0, 0.0, 0.0))
pB = f.cartesian_point((1.0, 0.0, 0.0))
pC = f.cartesian_point((0.5, 1.0, 0.0))

# Face 1: triangle with vertices A, B, C
vA1 = f.vertex_point(pA)
vB1 = f.vertex_point(pB)
vC1 = f.vertex_point(pC)

# Build three edges for Face 1: A→B, B→C, C→A
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pA, vec)
e1_AB = f.edge_curve(vA1, vB1, line)

d = f.direction((-0.5, 1.0, 0.0)); mag = (0.25 + 1.0)**0.5; vec = f.vector(d, mag); line = f.line(pB, vec)
e1_BC = f.edge_curve(vB1, vC1, line)

d = f.direction((-0.5, -1.0, 0.0)); mag = (0.25 + 1.0)**0.5; vec = f.vector(d, mag); line = f.line(pC, vec)
e1_CA = f.edge_curve(vC1, vA1, line)

loop1 = f.edge_loop([
    f.oriented_edge(e1_AB, True),
    f.oriented_edge(e1_BC, True),
    f.oriented_edge(e1_CA, True),
])

# Face 2: same triangle geometry but with DISTINCT edge curves
# (same vertices, same curves, but different EDGE_CURVE entities)
# Vertices for Face 2 (same points but different vertex entities)
vA2 = f.vertex_point(pA)
vB2 = f.vertex_point(pB)
vC2 = f.vertex_point(pC)

# Build three edges for Face 2 with identical geometry but opposite orientation
# Edge: B→A (opposite of A→B from Face 1)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); line = f.line(pB, vec)
e2_BA = f.edge_curve(vB2, vA2, line)

# Edge: C→B (opposite of B→C from Face 1)
d = f.direction((0.5, -1.0, 0.0)); mag = (0.25 + 1.0)**0.5; vec = f.vector(d, mag); line = f.line(pC, vec)
e2_CB = f.edge_curve(vC2, vB2, line)

# Edge: A→C (opposite of C→A from Face 1)
d = f.direction((0.5, 1.0, 0.0)); mag = (0.25 + 1.0)**0.5; vec = f.vector(d, mag); line = f.line(pA, vec)
e2_AC = f.edge_curve(vA2, vC2, line)

loop2 = f.edge_loop([
    f.oriented_edge(e2_BA, True),
    f.oriented_edge(e2_CB, True),
    f.oriented_edge(e2_AC, True),
])

# Create the shared plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)
face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

# Open shell containing both faces
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
