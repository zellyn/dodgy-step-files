"""Tfa188 — ShapeFix_Face.FixSmallAreaWire wire-bigger-than-face

Catalog claim: "FixSmallAreaWire removes small-area wires but does not
validate that inner-wire area ≤ outer-wire area. Inner wire with computed
area > outer wire creates impossible topology."

Demonstration: ADVANCED_FACE with outer wire (2×2 square, area=4) and
inner wire (4.5×4.5 rectangle, area≈20, extends past outer bounds).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa188",
             defect="Inner wire with area larger than outer wire")

def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)

# Outer wire: 2×2 square centered at origin
# Area = 4
p0_outer = f.cartesian_point((0.0, 0.0, 0.0))
p1_outer = f.cartesian_point((2.0, 0.0, 0.0))
p2_outer = f.cartesian_point((2.0, 2.0, 0.0))
p3_outer = f.cartesian_point((0.0, 2.0, 0.0))

v0_outer = f.vertex_point(p0_outer)
v1_outer = f.vertex_point(p1_outer)
v2_outer = f.vertex_point(p2_outer)
v3_outer = f.vertex_point(p3_outer)

outer_edges = [
    _edge(p0_outer, p1_outer, v0_outer, v1_outer),
    _edge(p1_outer, p2_outer, v1_outer, v2_outer),
    _edge(p2_outer, p3_outer, v2_outer, v3_outer),
    _edge(p3_outer, p0_outer, v3_outer, v0_outer),
]
outer = f.edge_loop([f.oriented_edge(e) for e in outer_edges])

# Inner wire: 4.5×4.5 rectangle centered at (1, 1)
# Extends from (-1.25, -1.25) to (3.25, 3.25)
# Area = 20.25 >> 4 (outer area)
# Extends OUTSIDE the outer boundary (impossible topology)
p0_inner = f.cartesian_point((-1.25, -1.25, 0.0))
p1_inner = f.cartesian_point((3.25, -1.25, 0.0))
p2_inner = f.cartesian_point((3.25, 3.25, 0.0))
p3_inner = f.cartesian_point((-1.25, 3.25, 0.0))

v0_inner = f.vertex_point(p0_inner)
v1_inner = f.vertex_point(p1_inner)
v2_inner = f.vertex_point(p2_inner)
v3_inner = f.vertex_point(p3_inner)

inner_edges = [
    _edge(p0_inner, p1_inner, v0_inner, v1_inner),
    _edge(p1_inner, p2_inner, v1_inner, v2_inner),
    _edge(p2_inner, p3_inner, v2_inner, v3_inner),
    _edge(p3_inner, p0_inner, v3_inner, v0_inner),
]
inner = f.edge_loop([f.oriented_edge(e) for e in inner_edges])

# Create plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Face with outer and oversized inner wire
face = f.advanced_face([
    f.face_outer_bound(outer, True),
    f.face_bound(inner, True),  # Inner wire bigger than outer (impossible)
], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
