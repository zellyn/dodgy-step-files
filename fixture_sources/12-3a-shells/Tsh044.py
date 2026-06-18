"""Tsh044 — Free edges in OPEN_SHELL distinguished from non-watertight defects.

Catalog claim: "A shell-orientation analyzer checks that each edge appears
either once (free edge, legal in an open shell) or twice with opposite
FORWARD/REVERSED orientations (legal for a connected pair). Edges appearing
twice with the same orientation, or three or more times, are defects.
The diagnostic must distinguish a true non-watertight ('naked', 'leaky')
defect from a legitimately open free boundary."

Demonstration: Build an OPEN_SHELL with two completely disjoint square faces
that share NO common edge — every edge appears exactly once. All edges are free,
which is legal for an open shell. The analyzer must NOT flag this as a defect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh044",
             defect="Free edges in open shell correctly distinguished from non-manifold")

# FACE 1: Square at (0,0,0)-(1,1,0)
p1_0 = f.cartesian_point((0.0, 0.0, 0.0))
p1_1 = f.cartesian_point((1.0, 0.0, 0.0))
p1_2 = f.cartesian_point((1.0, 1.0, 0.0))
p1_3 = f.cartesian_point((0.0, 1.0, 0.0))

v1_0 = f.vertex_point(p1_0)
v1_1 = f.vertex_point(p1_1)
v1_2 = f.vertex_point(p1_2)
v1_3 = f.vertex_point(p1_3)

# Edges for Face 1
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1_0, vec)
e1_0 = f.edge_curve(v1_0, v1_1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1_1, vec)
e1_1 = f.edge_curve(v1_1, v1_2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1_2, vec)
e1_2 = f.edge_curve(v1_2, v1_3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1_3, vec)
e1_3 = f.edge_curve(v1_3, v1_0, ln)

loop1 = f.edge_loop([
    f.oriented_edge(e1_0, True),
    f.oriented_edge(e1_1, True),
    f.oriented_edge(e1_2, True),
    f.oriented_edge(e1_3, True),
])

# Plane for both faces
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)

# FACE 2: Disjoint square at (2,0,0)-(3,1,0)
# No shared vertices or edges with Face 1
p2_0 = f.cartesian_point((2.0, 0.0, 0.0))
p2_1 = f.cartesian_point((3.0, 0.0, 0.0))
p2_2 = f.cartesian_point((3.0, 1.0, 0.0))
p2_3 = f.cartesian_point((2.0, 1.0, 0.0))

v2_0 = f.vertex_point(p2_0)
v2_1 = f.vertex_point(p2_1)
v2_2 = f.vertex_point(p2_2)
v2_3 = f.vertex_point(p2_3)

# Edges for Face 2
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2_0, vec)
e2_0 = f.edge_curve(v2_0, v2_1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2_1, vec)
e2_1 = f.edge_curve(v2_1, v2_2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2_2, vec)
e2_2 = f.edge_curve(v2_2, v2_3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2_3, vec)
e2_3 = f.edge_curve(v2_3, v2_0, ln)

loop2 = f.edge_loop([
    f.oriented_edge(e2_0, True),
    f.oriented_edge(e2_1, True),
    f.oriented_edge(e2_2, True),
    f.oriented_edge(e2_3, True),
])

face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

# OPEN_SHELL with two completely disjoint faces
# All edges are free (appear once) — legal for an open shell
# Analyzer must NOT flag this as defective
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
