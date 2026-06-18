"""Tsh040 — EDGE_CURVE shared across two OPEN_SHELLs in one SHELL_BASED_SURFACE_MODEL.

Catalog claim: "Two adjacent OPEN_SHELLs inside one SHELL_BASED_SURFACE_MODEL
share an EDGE_CURVE along a perfectly manifold T-junction. A slicer mesher
classifies the shared edge as non-manifold because the edge has 3+ face
references once the shells are joined."

Demonstration: Build two separate OPEN_SHELLs that both reference the same
EDGE_CURVE. When the shells are combined, the shared edge has >2 face references,
triggering a false non-manifold classification.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh040",
             defect="Shared EDGE_CURVE across two OPEN_SHELLs misclassified as non-manifold")

# Shared edge: will be referenced by both shells
p_shared_0 = f.cartesian_point((0.5, 0.0, 0.0))
p_shared_1 = f.cartesian_point((0.5, 1.0, 0.0))

v_shared_0 = f.vertex_point(p_shared_0)
v_shared_1 = f.vertex_point(p_shared_1)

d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p_shared_0, vec)
shared_edge = f.edge_curve(v_shared_0, v_shared_1, ln)

# SHELL 1: Left face (0,0,0)-(0.5,1,0)
p1_0 = f.cartesian_point((0.0, 0.0, 0.0))
p1_1 = p_shared_0  # shared point
p1_2 = p_shared_1  # shared point
p1_3 = f.cartesian_point((0.0, 1.0, 0.0))

v1_0 = f.vertex_point(p1_0)
v1_1 = v_shared_0
v1_2 = v_shared_1
v1_3 = f.vertex_point(p1_3)

# Edges for shell 1's face
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(p1_0, vec)
e1_0 = f.edge_curve(v1_0, v1_1, ln)
# shared_edge goes v1_1 → v1_2 (used below)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(p1_2, vec)
e1_2 = f.edge_curve(v1_2, v1_3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1_3, vec)
e1_3 = f.edge_curve(v1_3, v1_0, ln)

loop1 = f.edge_loop([
    f.oriented_edge(e1_0, True),
    f.oriented_edge(shared_edge, True),  # ← SHARED edge, first use
    f.oriented_edge(e1_2, True),
    f.oriented_edge(e1_3, True),
])

# Plane for shell 1
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)
shell1 = f.open_shell([face1])

# SHELL 2: Right face (0.5,0,0)-(1,1,0)
p2_0 = p_shared_0  # shared point
p2_1 = f.cartesian_point((1.0, 0.0, 0.0))
p2_2 = f.cartesian_point((1.0, 1.0, 0.0))
p2_3 = p_shared_1  # shared point

v2_0 = v_shared_0
v2_1 = f.vertex_point(p2_1)
v2_2 = f.vertex_point(p2_2)
v2_3 = v_shared_1

# Edges for shell 2's face
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(p2_0, vec)
e2_0 = f.edge_curve(v2_0, v2_1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2_1, vec)
e2_1 = f.edge_curve(v2_1, v2_2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 0.5); ln = f.line(p2_2, vec)
e2_2 = f.edge_curve(v2_2, v2_3, ln)
# shared_edge goes v2_3 → v2_0 (reversed for shell 2)

loop2 = f.edge_loop([
    f.oriented_edge(e2_0, True),
    f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True),
    f.oriented_edge(shared_edge, False),  # ← SHARED edge, second use (reversed)
])

plc2 = f.axis2_placement_3d(p2_0, zdir, xdir)
plane2 = f.plane(plc2)

face2 = f.advanced_face([f.face_outer_bound(loop2)], plane2)
shell2 = f.open_shell([face2])

# SHELL_BASED_SURFACE_MODEL with both shells sharing the edge
sbsm = f.shell_based_surface_model([shell1, shell2])
f.add_product_chain(sbsm)
