"""Tfa173 — ShapeFix_Face.FixSplitFace splitter-tangent-at-vertex

Catalog claim: "Splitter LINE that is tangent to the face boundary at one of
its endpoint vertices. FixSplitFace does not detect the tangency condition
and produces degenerate sub-face with zero area, violating the face validity
contract."

Demonstration: 10×10 planar face with a vertical splitter line (x=5) that
is tangent to the top edge at vertex (5,10). The splitter touches the outer
boundary at exactly one point without crossing it transversally.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa173",
             defect="Splitter line tangent to face boundary at endpoint vertex")

# Create outer 10×10 rectangle on z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Build outer boundary edges
def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)

outer_edges = [
    _edge(p0, p1, v0, v1),
    _edge(p1, p2, v1, v2),
    _edge(p2, p3, v2, v3),
    _edge(p3, p0, v3, v0),
]
outer = f.edge_loop([f.oriented_edge(e) for e in outer_edges])

# Splitter line: vertical at x=5, from (5,0) to (5,10)
# This line is TANGENT to the top edge at (5,10)
ps_bot = f.cartesian_point((5.0, 0.0, 0.0))
ps_top = f.cartesian_point((5.0, 10.0, 0.0))
vs_bot = f.vertex_point(ps_bot)
vs_top = f.vertex_point(ps_top)
splitter_edge = _edge(ps_bot, ps_top, vs_bot, vs_top)
splitter = f.edge_loop([f.oriented_edge(splitter_edge)])

# Create face with outer boundary and tangent splitter
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([
    f.face_outer_bound(outer, True),
    f.face_bound(splitter, True),  # Inner splitter wire
], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
