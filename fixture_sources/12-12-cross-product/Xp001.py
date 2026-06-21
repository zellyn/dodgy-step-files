"""Xp001 — Malformed \\X2\\ escape in PRODUCT.name AND self-intersecting wire."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp001",
             defect='Malformed \\X2\\ escape in PRODUCT.name AND self-intersecting wire')

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Figure-eight wire: two triangles sharing origin, creating a self-intersection
# Triangle 1: (0,0,0) -> (1,1,0) -> (-1,1,0) -> (0,0,0)
# Triangle 2: (0,0,0) -> (1,-1,0) -> (-1,-1,0) -> (0,0,0)
# These diagonals cross at origin — self-intersecting wire

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 1.0, 0.0))
p2 = f.cartesian_point((-1.0, 1.0, 0.0))
p3 = f.cartesian_point((1.0, -1.0, 0.0))
p4 = f.cartesian_point((-1.0, -1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# First leg: p0->p1
e0 = line_edge(p0, p1, v0, v1)
# Second leg: p1->p2
e1 = line_edge(p1, p2, v1, v2)
# Third leg: p2->p3 (crosses e0)
e2 = line_edge(p2, p3, v2, v3)
# Fourth leg: p3->p0
e3 = line_edge(p3, p0, v3, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect: malformed \X2\ escape — three hex digits, no closing \X0\
# The PRODUCT name references a UCS-2 escape that is syntactically invalid
f._emit_raw(r"DESCRIPTIVE_REPRESENTATION_ITEM('xp001_defect','part-\X2\30A2 30A4')")
