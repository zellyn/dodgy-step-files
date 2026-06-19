"""Tfa171 — FixLoopWire triple-point self-intersection.

Catalog claim: face inner wire contains a triple-point self-intersection
(three edges meeting at one vertex inside the boundary). FixLoopWire's
merge logic handles double points but not triples.

Previous fixture made a *4-way* meet (vertex incident on 4 edge-endpoints,
not 3). Regen with a clean Y-shape inner wire: three edges all incident
to one center vertex.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa171",
             defect="inner wire Y-shape (3 edges meeting at one center vertex)")

# Outer 10×10 rectangle.
p_out = [f.cartesian_point(p) for p in
         [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]]
v_out = [f.vertex_point(p) for p in p_out]

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e_out = [
    line_edge(p_out[0], (1.0, 0.0, 0.0), 10.0, v_out[0], v_out[1]),
    line_edge(p_out[1], (0.0, 1.0, 0.0), 10.0, v_out[1], v_out[2]),
    line_edge(p_out[2], (-1.0, 0.0, 0.0), 10.0, v_out[2], v_out[3]),
    line_edge(p_out[3], (0.0, -1.0, 0.0), 10.0, v_out[3], v_out[0]),
]
outer_loop = f.edge_loop([f.oriented_edge(e, True) for e in e_out])

# Triple point: center vertex incident on exactly 3 inner edges (Y shape).
center = f.cartesian_point((5.0, 5.0, 0.0))
v_center = f.vertex_point(center)

# Three radial directions, 120° apart.
angles = [0.0, 2 * math.pi / 3, 4 * math.pi / 3]
radial_edges = []
for a in angles:
    px = 5.0 + 2.0 * math.cos(a)
    py = 5.0 + 2.0 * math.sin(a)
    p_tip = f.cartesian_point((px, py, 0.0))
    v_tip = f.vertex_point(p_tip)
    radial_edges.append(line_edge(
        center, (math.cos(a), math.sin(a), 0.0), 2.0, v_center, v_tip))

# Inner Y wire: three edges all incident on v_center.
inner_loop = f.edge_loop([f.oriented_edge(e, True) for e in radial_edges])

# Plane carrier.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner_loop),
], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
