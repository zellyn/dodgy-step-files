"""Xp003 — Sliver face × non-manifold edge (3 faces share one edge)."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp003",
             defect='Sliver face × non-manifold edge (3 faces share one edge)')

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Three faces sharing one common edge (non-manifold)
# Face 1: unit square (0,0)-(1,0)-(1,1)-(0,1)
# Face 2: another square sharing bottom edge (0,0)-(1,0), goes downward
# Face 3: sliver face — shares the bottom edge, near-zero width (1e-4)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p1n = f.cartesian_point((1.0, -1.0, 0.0))
p0n = f.cartesian_point((0.0, -1.0, 0.0))
# Sliver points — near-zero height (1e-4 from bottom edge)
p1s = f.cartesian_point((1.0, 1.0e-4, 0.0))
p0s = f.cartesian_point((0.0, 1.0e-4, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
v1n = f.vertex_point(p1n)
v0n = f.vertex_point(p0n)
v1s = f.vertex_point(p1s)
v0s = f.vertex_point(p0s)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Shared bottom edge (non-manifold — used by all 3 faces)
e_bottom = line_edge(p00, p10, v00, v10)

# Face 1: unit square — uses e_bottom as bottom edge
e1_right = line_edge(p10, p11, v10, v11)
e1_top   = line_edge(p11, p01, v11, v01)
e1_left  = line_edge(p01, p00, v01, v00)
loop1 = f.edge_loop([
    f.oriented_edge(e_bottom, True),
    f.oriented_edge(e1_right, True),
    f.oriented_edge(e1_top, True),
    f.oriented_edge(e1_left, True),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)

# Face 2: downward square — uses e_bottom reversed
e2_left  = line_edge(p00, p0n, v00, v0n)
e2_bot   = line_edge(p0n, p1n, v0n, v1n)
e2_right = line_edge(p1n, p10, v1n, v10)
loop2 = f.edge_loop([
    f.oriented_edge(e_bottom, False),   # reversed: p10->p00
    f.oriented_edge(e2_left, True),
    f.oriented_edge(e2_bot, True),
    f.oriented_edge(e2_right, True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

# Face 3: sliver — shares e_bottom, near-zero height (1e-4)
e3_right = line_edge(p10, p1s, v10, v1s)
e3_top   = line_edge(p1s, p0s, v1s, v0s)
e3_left  = line_edge(p0s, p00, v0s, v00)
loop3 = f.edge_loop([
    f.oriented_edge(e_bottom, True),
    f.oriented_edge(e3_right, True),
    f.oriented_edge(e3_top, True),
    f.oriented_edge(e3_left, True),
])
face3 = f.advanced_face([f.face_outer_bound(loop3)], plane)

shell = f.open_shell([face1, face2, face3])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
