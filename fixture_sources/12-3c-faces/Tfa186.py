"""Tfa186 — ShapeFix_Face.FixOrientation with-inner-wires-only

Catalog claim: "Face containing only inner wires (no outer boundary).
FixOrientation assumes outer wire exists for reference classification;
undefined behavior when missing."

Demonstration: ADVANCED_FACE with two rectangular FACE_INNER_BOUND loops only,
no FACE_OUTER_BOUND. The inner loops represent isolated wires without a
containing outer boundary.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa186",
             defect="Face with only inner wires, missing outer boundary")

def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)

# First inner wire: 3×3 rectangle at (1,1) to (4,4)
p1_0 = f.cartesian_point((1.0, 1.0, 0.0))
p1_1 = f.cartesian_point((4.0, 1.0, 0.0))
p1_2 = f.cartesian_point((4.0, 4.0, 0.0))
p1_3 = f.cartesian_point((1.0, 4.0, 0.0))

v1_0 = f.vertex_point(p1_0)
v1_1 = f.vertex_point(p1_1)
v1_2 = f.vertex_point(p1_2)
v1_3 = f.vertex_point(p1_3)

inner1_edges = [
    _edge(p1_0, p1_1, v1_0, v1_1),
    _edge(p1_1, p1_2, v1_1, v1_2),
    _edge(p1_2, p1_3, v1_2, v1_3),
    _edge(p1_3, p1_0, v1_3, v1_0),
]
inner1 = f.edge_loop([f.oriented_edge(e) for e in inner1_edges])

# Second inner wire: 2×2 rectangle at (6,6) to (8,8)
p2_0 = f.cartesian_point((6.0, 6.0, 0.0))
p2_1 = f.cartesian_point((8.0, 6.0, 0.0))
p2_2 = f.cartesian_point((8.0, 8.0, 0.0))
p2_3 = f.cartesian_point((6.0, 8.0, 0.0))

v2_0 = f.vertex_point(p2_0)
v2_1 = f.vertex_point(p2_1)
v2_2 = f.vertex_point(p2_2)
v2_3 = f.vertex_point(p2_3)

inner2_edges = [
    _edge(p2_0, p2_1, v2_0, v2_1),
    _edge(p2_1, p2_2, v2_1, v2_2),
    _edge(p2_2, p2_3, v2_2, v2_3),
    _edge(p2_3, p2_0, v2_3, v2_0),
]
inner2 = f.edge_loop([f.oriented_edge(e) for e in inner2_edges])

# Create plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Create face with ONLY inner bounds (no outer bound)
# This is the defect: missing outer boundary
face = f.advanced_face([
    f.face_bound(inner1, True),   # Inner bound 1
    f.face_bound(inner2, True),   # Inner bound 2
    # NO f.face_outer_bound() — intentional defect
], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
