"""Tsh041 — Shell extrusion with shared edges yields CompSolid with duplicated internal faces.

Catalog claim: "Per-face extrusion of a connected Shell creates one Solid per
face with coincident-but-duplicated internal faces. Boolean ops on the result fail."

Demonstration: Build a two-triangle OPEN_SHELL sharing one edge. The topology
is set up so that if each face were extruded independently, it would produce
internal walls that should not exist in a proper solid.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh041",
             defect="Multi-face shell with shared edges prone to duplication on extrusion")

# Build a two-triangle open shell sharing one edge.

# Shared edge: from (0,0,0) to (1,0,0)
p_shared_0 = f.cartesian_point((0.0, 0.0, 0.0))
p_shared_1 = f.cartesian_point((1.0, 0.0, 0.0))

v_shared_0 = f.vertex_point(p_shared_0)
v_shared_1 = f.vertex_point(p_shared_1)

d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p_shared_0, vec)
shared_edge = f.edge_curve(v_shared_0, v_shared_1, ln)

# TRIANGLE 1: (0,0,0) → (1,0,0) → (0.5,1,0)
p1_0 = p_shared_0
p1_1 = p_shared_1
p1_2 = f.cartesian_point((0.5, 1.0, 0.0))

v1_0 = v_shared_0
v1_1 = v_shared_1
v1_2 = f.vertex_point(p1_2)

# Edges for triangle 1
# Edge 0: shared edge (v1_0 → v1_1)
# Edge from p1_1 (1,0,0) to p1_2 (0.5, 1, 0)
d_norm = (0.5**2 + 1.0**2)**0.5
d_normalized = (0.5/d_norm, 1.0/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p1_1, vec)
e1_1 = f.edge_curve(v1_1, v1_2, ln)

# Edge from p1_2 (0.5, 1, 0) to p1_0 (0, 0, 0)
d_norm = (0.5**2 + 1.0**2)**0.5
d_normalized = (-0.5/d_norm, -1.0/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p1_2, vec)
e1_2 = f.edge_curve(v1_2, v1_0, ln)

loop1 = f.edge_loop([
    f.oriented_edge(shared_edge, True),
    f.oriented_edge(e1_1, True),
    f.oriented_edge(e1_2, True),
])

# Plane for both triangles
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)

# TRIANGLE 2: (0,0,0) → (1,0,0) → (0.5,-1,0)
p2_0 = p_shared_0
p2_1 = p_shared_1
p2_2 = f.cartesian_point((0.5, -1.0, 0.0))

v2_0 = v_shared_0
v2_1 = v_shared_1
v2_2 = f.vertex_point(p2_2)

# Edges for triangle 2
# Edge 0: shared edge (v2_0 → v2_1), reversed orientation
# Edge from p2_1 (1, 0, 0) to p2_2 (0.5, -1, 0)
d_norm = (0.5**2 + 1.0**2)**0.5
d_normalized = (0.5/d_norm, -1.0/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p2_1, vec)
e2_1 = f.edge_curve(v2_1, v2_2, ln)

# Edge from p2_2 (0.5, -1, 0) to p2_0 (0, 0, 0)
d_norm = (0.5**2 + 1.0**2)**0.5
d_normalized = (-0.5/d_norm, 1.0/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p2_2, vec)
e2_2 = f.edge_curve(v2_2, v2_0, ln)

loop2 = f.edge_loop([
    f.oriented_edge(shared_edge, False),  # Reversed (manifold pair)
    f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True),
])

face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

# Two-triangle shell sharing one edge
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
