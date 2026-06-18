"""Tfa190 — ShapeFix_Face.FixWiresTwoCoincEdges with-coincident-vertex-only

Catalog claim: "FixWiresTwoCoincEdges detects edge identity via EDGE_CURVE
comparison but treats vertex-only touching (point coincidence) as edge
coincidence, triggering false-positive merges."

Demonstration: ADVANCED_FACE with outer wire (10×10 rectangle) and inner wire
(triangle) touching only at single shared vertex (5,5), no shared edges.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa190",
             defect="Inner and outer wires sharing only a single vertex, not edges")

def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)

# Outer wire: 10×10 square
p0_outer = f.cartesian_point((0.0, 0.0, 0.0))
p1_outer = f.cartesian_point((10.0, 0.0, 0.0))
p2_outer = f.cartesian_point((10.0, 10.0, 0.0))
p3_outer = f.cartesian_point((0.0, 10.0, 0.0))

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

# Inner wire: Triangle with ONE vertex at (5, 5) — shared with outer boundary
# The triangle only TOUCHES the outer wire at this single point
# Vertices: (5, 5) [touching point], (3, 7), (7, 7)
p_shared = f.cartesian_point((5.0, 5.0, 0.0))  # Shared with outer boundary
p_inner_1 = f.cartesian_point((3.0, 7.0, 0.0))
p_inner_2 = f.cartesian_point((7.0, 7.0, 0.0))

v_shared = f.vertex_point(p_shared)
v_inner_1 = f.vertex_point(p_inner_1)
v_inner_2 = f.vertex_point(p_inner_2)

inner_edges = [
    _edge(p_shared, p_inner_1, v_shared, v_inner_1),
    _edge(p_inner_1, p_inner_2, v_inner_1, v_inner_2),
    _edge(p_inner_2, p_shared, v_inner_2, v_shared),
]
inner = f.edge_loop([f.oriented_edge(e) for e in inner_edges])

# Create plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Face with outer rectangle and inner triangle touching at single vertex
face = f.advanced_face([
    f.face_outer_bound(outer, True),
    f.face_bound(inner, True),  # Inner touches outer at one point only
], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
