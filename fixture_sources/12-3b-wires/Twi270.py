"""Twi270 — ShapeAnalysis_Wire.CheckShapeConnect connectivity validation.

Catalog claim: Multi-edge shape connectivity validation; disconnected edge
chains not flagged when vertices lie within tolerance.

Demonstration: 4-edge wire where edge1's end vertex and edge2's start vertex
are at distinct CARTESIAN_POINT entities with coordinates separated by 5e-8
mm — under the global UNCERTAINTY_MEASURE (1e-7) and so "connected" by
tolerance, but topologically distinct vertices. CheckShapeConnect should
flag this; if it relies only on vertex-identity it misses the disconnect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi270",
             defect="connectivity validation: within-tolerance disconnect")

# Four corner points with a tiny sub-tolerance gap at the (1,0,0) corner:
# edge1 ends at p1a = (1.0, 0.0, 0.0); edge2 starts at p1b = (1.00000005, 0.0, 0.0).
# Gap = 5e-8 mm, under global uncertainty 1e-7 → looks "connected" but isn't.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1a = f.cartesian_point((1.0, 0.0, 0.0))
p1b = f.cartesian_point((1.00000005, 0.0, 0.0))  # within-tolerance offset
p2 = f.cartesian_point((1.00000005, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1a = f.vertex_point(p1a)
v1b = f.vertex_point(p1b)   # distinct VERTEX_POINT — the topological disconnect
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1a)
e1 = line_edge(p1b, (0.0, 1.0, 0.0), 1.0, v1b, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.00000005, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Carrier plane so the wire has a surface to live on.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
