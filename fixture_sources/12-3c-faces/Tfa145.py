"""Tfa145 — ShapeFix_Face.FixSplitFace two-splitters.

Catalog claim: "Planar face (10×10 square) with two interior splitter
wires: vertical line (x=2, y∈[0,10]) and horizontal line (y=5, x∈[0,10])
intersecting at (2,5). FixSplitFace applies splitters sequentially in a
loop; after first splitter creates two sub-faces, the loop structure
sees stale topology when applying second splitter."

Demonstration: 10×10 ADVANCED_FACE with outer loop + two inner FACE_BOUND
wires representing the splitters. The splitters cross at (2,5).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa145",
             defect="FixSplitFace with two crossing interior splitter wires")


def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)


# Outer 10x10 loop
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
outer = f.edge_loop([
    f.oriented_edge(_edge(p0, p1, v0, v1)),
    f.oriented_edge(_edge(p1, p2, v1, v2)),
    f.oriented_edge(_edge(p2, p3, v2, v3)),
    f.oriented_edge(_edge(p3, p0, v3, v0)),
])

# Vertical splitter wire at x=2: from (2,0) to (2,10)
ps_v_bot = f.cartesian_point((2.0, 0.0, 0.0))
ps_v_top = f.cartesian_point((2.0, 10.0, 0.0))
vs_v_bot = f.vertex_point(ps_v_bot)
vs_v_top = f.vertex_point(ps_v_top)
vertical_splitter = f.edge_loop([
    f.oriented_edge(_edge(ps_v_bot, ps_v_top, vs_v_bot, vs_v_top)),
])

# Horizontal splitter wire at y=5: from (0,5) to (10,5)
ps_h_left = f.cartesian_point((0.0, 5.0, 0.0))
ps_h_right = f.cartesian_point((10.0, 5.0, 0.0))
vs_h_left = f.vertex_point(ps_h_left)
vs_h_right = f.vertex_point(ps_h_right)
horizontal_splitter = f.edge_loop([
    f.oriented_edge(_edge(ps_h_left, ps_h_right, vs_h_left, vs_h_right)),
])

# Build face with outer loop + 2 inner FACE_BOUND wires (the splitters).
# The two splitters cross at (2,5) but the geometry doesn't declare an
# explicit vertex there — that's the defect: FixSplitFace must
# discover the intersection and synchronize edge/vertex dedup between
# the two splitter applications.
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([
    f.face_outer_bound(outer, True),
    f.face_bound(vertical_splitter, True),
    f.face_bound(horizontal_splitter, True),
], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
