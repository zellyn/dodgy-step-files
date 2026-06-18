"""Tsh043 — Multi-face shell needs orchestrated healing (per-face + shell-wide).

Catalog claim: "An OPEN_SHELL of multiple faces has per-face defects
(orientation flips, missing pcurves, sub-tolerance edges) and shell-level
defects (face-orientation propagation cannot resolve until per-face fixes
converge). Healing one face changes the inputs to the next face's fix;
a one-pass approach leaves residual defects."

Demonstration: Build an OPEN_SHELL with two adjacent faces sharing one edge,
where both faces have orientation flaws (opposite same_sense flags and/or
edge-traversal mismatches) that require coordinated healing passes.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh043",
             defect="Multi-face shell needs coordinated healing (per-face + shell-wide)")

# Two adjacent square faces sharing one edge.
# Each face has per-face flaws that interact through the shared edge.

# Shared edge: (0.5, 0, 0) → (0.5, 1, 0)
p_shared_0 = f.cartesian_point((0.5, 0.0, 0.0))
p_shared_1 = f.cartesian_point((0.5, 1.0, 0.0))

v_shared_0 = f.vertex_point(p_shared_0)
v_shared_1 = f.vertex_point(p_shared_1)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p_shared_0, vec)
shared_edge = f.edge_curve(v_shared_0, v_shared_1, ln)

# FACE A: Left rectangle (0,0,0)-(0.5,1,0)
pA0 = f.cartesian_point((0.0, 0.0, 0.0))
pA1 = p_shared_0
pA2 = p_shared_1
pA3 = f.cartesian_point((0.0, 1.0, 0.0))

vA0 = f.vertex_point(pA0)
vA1 = v_shared_0
vA2 = v_shared_1
vA3 = f.vertex_point(pA3)

# Edges for Face A
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(pA0, vec)
eA0 = f.edge_curve(vA0, vA1, ln)
# shared_edge (vA1 → vA2)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(pA2, vec)
eA2 = f.edge_curve(vA2, vA3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pA3, vec)
eA3 = f.edge_curve(vA3, vA0, ln)

loopA = f.edge_loop([
    f.oriented_edge(eA0, True),
    f.oriented_edge(shared_edge, True),   # Forward orientation
    f.oriented_edge(eA2, True),
    f.oriented_edge(eA3, True),
])

# Plane for both faces
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

# Face A with normal same_sense=.T.
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane, same_sense=True)

# FACE B: Right rectangle (0.5,0,0)-(1,1,0)
pB0 = p_shared_0
pB1 = f.cartesian_point((1.0, 0.0, 0.0))
pB2 = f.cartesian_point((1.0, 1.0, 0.0))
pB3 = p_shared_1

vB0 = v_shared_0
vB1 = f.vertex_point(pB1)
vB2 = f.vertex_point(pB2)
vB3 = v_shared_1

# Edges for Face B
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(pB0, vec)
eB0 = f.edge_curve(vB0, vB1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(pB1, vec)
eB1 = f.edge_curve(vB1, vB2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(pB2, vec)
eB2 = f.edge_curve(vB2, vB3, ln)
# shared_edge (vB3 → vB0), reversed

loopB = f.edge_loop([
    f.oriented_edge(eB0, True),
    f.oriented_edge(eB1, True),
    f.oriented_edge(eB2, True),
    f.oriented_edge(shared_edge, False),  # Reversed (opposite A)
])

# Face B with same_sense=.F. (FLIPPED relative to A — the interaction defect)
# This causes a coordination issue: both faces use the shared edge,
# but with opposite orientations AND opposite same_sense flags.
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane, same_sense=False)

# OPEN_SHELL with both faces requiring coordinated healing
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
