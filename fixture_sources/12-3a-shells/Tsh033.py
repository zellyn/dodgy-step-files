"""Tsh033 — Mirrored block instances flip surface direction with parameter-space curves.

Catalog claim: "When 'Export parameter space curves' is enabled and the block
instance has a negative-determinant transform (mirror), some surfaces import
with reversed normal. MAPPED_ITEM with mirroring AXIS2_PLACEMENT_3D is exported
with a copy whose orientation is silently corrected, flipping handedness."

Demonstration: Build two identical rectangular faces in different orientations
that could represent a mirrored-instance scenario. The faces share geometry but
have opposite normal directions due to mirror-induced flip.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh033",
             defect="Mirrored block instance flips surface normal direction")

# Face A: rectangle at origin (0,0,0)-(1,1,0) with normal pointing up (+Z)
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = f.cartesian_point((1.0, 0.0, 0.0))
pA2 = f.cartesian_point((1.0, 1.0, 0.0))
pA3 = f.cartesian_point((0.0, 1.0, 0.0))

vA0 = f.vertex_point(pA0)
vA1 = f.vertex_point(pA1)
vA2 = f.vertex_point(pA2)
vA3 = f.vertex_point(pA3)

# Edges for Face A (counterclockwise when viewed from +Z)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA0, vec)
eA0 = f.edge_curve(vA0, vA1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA1, vec)
eA1 = f.edge_curve(vA1, vA2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA2, vec)
eA2 = f.edge_curve(vA2, vA3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA3, vec)
eA3 = f.edge_curve(vA3, vA0, ln)

loopA = f.edge_loop([
    f.oriented_edge(eA0, True),
    f.oriented_edge(eA1, True),
    f.oriented_edge(eA2, True),
    f.oriented_edge(eA3, True),
])

# Plane for Face A
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc_A = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane_A = f.plane(plc_A)

faceA = f.advanced_face([f.face_outer_bound(loopA)], plane_A, same_sense=True)

# Face B: mirrored copy at 2,0,0 with same geometry but mirrored about YZ plane
# This simulates the normal-flip that happens with mirror transforms
pB0 = f.cartesian_point((3.0, 0.0, 0.0))    # Mirrored: 2 + (1-0) = 3
pB1 = f.cartesian_point((2.0, 0.0, 0.0))    # Mirrored: 2 + (1-1) = 2
pB2 = f.cartesian_point((2.0, 1.0, 0.0))
pB3 = f.cartesian_point((3.0, 1.0, 0.0))

vB0 = f.vertex_point(pB0)
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)
vB3 = f.vertex_point(pB3)

# Edges for Face B (clockwise to match the mirrored orientation)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB0, vec)
eB0 = f.edge_curve(vB0, vB1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB1, vec)
eB1 = f.edge_curve(vB1, vB2, ln)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB2, vec)
eB2 = f.edge_curve(vB2, vB3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB3, vec)
eB3 = f.edge_curve(vB3, vB0, ln)

loopB = f.edge_loop([
    f.oriented_edge(eB0, True),
    f.oriented_edge(eB1, True),
    f.oriented_edge(eB2, True),
    f.oriented_edge(eB3, True),
])

plc_B = f.axis2_placement_3d(pB0, zdir, xdir)
plane_B = f.plane(plc_B)

# Face B flipped (normal pointing down due to mirror)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane_B, same_sense=False)

# Open shell with both faces (mirrored instance scenario)
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
