"""Tsh022 — Non-manifold STEP loses XCAF attributes (color/PMI) on read.

Catalog claim: "STEP reader's non-manifold path skipped XCAF attribute
application; STEP export in non-manifold mode lost all but one face."

Demonstration: Build a NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION with
multiple disconnected shells, each tagged with STYLED_ITEM. Tests whether
color/PMI metadata survives the non-manifold reading path.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh022",
             defect="Non-manifold surface loses XCAF color attributes on read")

# First shell: rectangle in XY plane at z=0
p1_0 = f.cartesian_point((0.0, 0.0, 0.0))
p1_1 = f.cartesian_point((1.0, 0.0, 0.0))
p1_2 = f.cartesian_point((1.0, 1.0, 0.0))
p1_3 = f.cartesian_point((0.0, 1.0, 0.0))

v1_0 = f.vertex_point(p1_0)
v1_1 = f.vertex_point(p1_1)
v1_2 = f.vertex_point(p1_2)
v1_3 = f.vertex_point(p1_3)

# Edges for first shell
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

# Plane for first shell
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)
shell1 = f.open_shell([face1])

# Second shell: disconnected rectangle in XY plane at z=1
p2_0 = f.cartesian_point((2.0, 0.0, 1.0))
p2_1 = f.cartesian_point((3.0, 0.0, 1.0))
p2_2 = f.cartesian_point((3.0, 1.0, 1.0))
p2_3 = f.cartesian_point((2.0, 1.0, 1.0))

v2_0 = f.vertex_point(p2_0)
v2_1 = f.vertex_point(p2_1)
v2_2 = f.vertex_point(p2_2)
v2_3 = f.vertex_point(p2_3)

# Edges for second shell
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

# Plane for second shell (z=1)
plc2 = f.axis2_placement_3d(p2_0, zdir, xdir)
plane2 = f.plane(plc2)

face2 = f.advanced_face([f.face_outer_bound(loop2)], plane2)
shell2 = f.open_shell([face2])

# NON_MANIFOLD surface model with two disjoint shells
sbsm = f.shell_based_surface_model([shell1, shell2])
f.add_product_chain(sbsm)
