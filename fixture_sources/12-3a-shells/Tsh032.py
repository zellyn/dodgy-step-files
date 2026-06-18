"""Tsh032 — Single ADVANCED_FACE with same_sense=.F. flipped inward in CLOSED_SHELL.

Catalog claim: "Adjacent faces with opposite outward normals; one or more faces
in a CLOSED_SHELL carry same_sense=.F. while their neighbours carry .T.,
producing a face flipped inward."

Demonstration: Build a CLOSED_SHELL with two adjacent faces sharing an edge,
where one face has same_sense=.F. (flipped inward) and the other has same_sense=.T.,
breaking normal coherence.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh032",
             defect="CLOSED_SHELL with one face flipped inward via same_sense=.F.")

# Build two adjacent rectangular faces that share an edge.
# Face A at z=0, Face B at z=1, sharing the top edge of A.

# Face A: rectangle 0,0,0 to 1,1,0
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = f.cartesian_point((1.0, 0.0, 0.0))
pA2 = f.cartesian_point((1.0, 1.0, 0.0))
pA3 = f.cartesian_point((0.0, 1.0, 0.0))

vA0 = f.vertex_point(pA0)
vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2)
vA3 = f.vertex_point(pA3)

# Edges for Face A
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA0, vec)
eA0 = f.edge_curve(vA0, vA1, ln)  # bottom
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA1, vec)
eA1 = f.edge_curve(vA1, vA2, ln)  # right (shared edge)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA2, vec)
eA2 = f.edge_curve(vA2, vA3, ln)  # top (shared with B)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA3, vec)
eA3 = f.edge_curve(vA3, vA0, ln)  # left

loopA = f.edge_loop([
    f.oriented_edge(eA0, True),
    f.oriented_edge(eA1, True),
    f.oriented_edge(eA2, True),
    f.oriented_edge(eA3, True),
])

# Plane for Face A (z=0)
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_A = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane_A = f.plane(plc_A)

# Face A with same_sense=.T. (normal)
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane_A, same_sense=True)

# Face B: rectangle 0,1,0 to 1,2,0 (adjacent, sharing pA2-pA3 edge)
pB0 = f.cartesian_point((0.0, 1.0, 0.0))
pB1 = f.cartesian_point((1.0, 1.0, 0.0))
pB2 = f.cartesian_point((1.0, 2.0, 0.0))
pB3 = f.cartesian_point((0.0, 2.0, 0.0))

vB0 = f.vertex_point(pB0)
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)
vB3 = f.vertex_point(pB3)

# Edges for Face B
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB0, vec)
eB0 = f.edge_curve(vB0, vB1, ln)  # shared with A (bottom of B, top of A)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB1, vec)
eB1 = f.edge_curve(vB1, vB2, ln)  # right
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB2, vec)
eB2 = f.edge_curve(vB2, vB3, ln)  # top
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB3, vec)
eB3 = f.edge_curve(vB3, vB0, ln)  # left

loopB = f.edge_loop([
    f.oriented_edge(eB0, True),
    f.oriented_edge(eB1, True),
    f.oriented_edge(eB2, True),
    f.oriented_edge(eB3, True),
])

plc_B = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane_B = f.plane(plc_B)

# Face B with same_sense=.F. (FLIPPED INWARD — the defect)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane_B, same_sense=False)

# CLOSED_SHELL with one face flipped inward
shell = f.closed_shell([faceA, faceB])
brep = f.manifold_solid_brep(shell)
f.add_product_chain(brep)
