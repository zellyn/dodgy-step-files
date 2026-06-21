"""Xp012 — Reversed face normal × non-watertight shell × duplicate edge."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp012",
             defect='Reversed face normal x non-watertight shell x duplicate edge')

# 6-face cube, with three defects:
# Face 3: same_sense = False (reversed normal)
# Face 4: outer wire has same edge repeated twice (duplicate ORIENTED_EDGE)
# Face 5: endpoints 1e-3 short of shared edge (gap — non-watertight)

def mkpt(xyz):
    return f.cartesian_point(xyz)

def mkv(p):
    return f.vertex_point(p)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

def oe(e, s=True):
    return f.oriented_edge(e, s)

# Unit cube vertices
p000 = mkpt((0.0, 0.0, 0.0)); p100 = mkpt((1.0, 0.0, 0.0))
p110 = mkpt((1.0, 1.0, 0.0)); p010 = mkpt((0.0, 1.0, 0.0))
p001 = mkpt((0.0, 0.0, 1.0)); p101 = mkpt((1.0, 0.0, 1.0))
p111 = mkpt((1.0, 1.0, 1.0)); p011 = mkpt((0.0, 1.0, 1.0))
# Gap point: 1e-3 short on face 5's boundary
p010g = mkpt((0.0, 1.0 - 1.0e-3, 0.0))  # gap point

v000 = mkv(p000); v100 = mkv(p100); v110 = mkv(p110); v010 = mkv(p010)
v001 = mkv(p001); v101 = mkv(p101); v111 = mkv(p111); v011 = mkv(p011)
v010g = mkv(p010g)

# Edges
e_b0 = line_edge(p000, p100, v000, v100)
e_b1 = line_edge(p100, p110, v100, v110)
e_b2 = line_edge(p110, p010, v110, v010)
e_b3 = line_edge(p010, p000, v010, v000)
e_t0 = line_edge(p001, p101, v001, v101)
e_t1 = line_edge(p101, p111, v101, v111)
e_t2 = line_edge(p111, p011, v111, v011)
e_t3 = line_edge(p011, p001, v011, v001)
e_v0 = line_edge(p000, p001, v000, v001)
e_v1 = line_edge(p100, p101, v100, v101)
e_v2 = line_edge(p110, p111, v110, v111)
e_v3 = line_edge(p010, p011, v010, v011)
# Gap edge: from v010g to v000 (stops 1e-3 short of v010)
e_gap = line_edge(p010g, p000, v010g, v000)
e_v3g = line_edge(p010, p011, v010, v011)  # reuse same shared edge

# Planes
def mkplane(ox, oy, oz, nx, ny, nz, rx, ry, rz):
    o = f.cartesian_point((ox, oy, oz))
    n = f.direction((nx, ny, nz))
    r = f.direction((rx, ry, rz))
    plc = f.axis2_placement_3d(o, n, r)
    return f.plane(plc)

pl_bot   = mkplane(0,0,0, 0,0,1,  1,0,0)
pl_top   = mkplane(0,0,1, 0,0,-1, 1,0,0)
pl_front = mkplane(0,0,0, 0,-1,0, 1,0,0)
pl_back  = mkplane(0,1,0, 0,1,0, -1,0,0)
pl_right = mkplane(1,0,0, 1,0,0,  0,1,0)
pl_left  = mkplane(0,0,0, -1,0,0, 0,-1,0)

# Face 1: bottom (valid)
l1 = f.edge_loop([oe(e_b0), oe(e_b1), oe(e_b2), oe(e_b3)])
face1 = f.advanced_face([f.face_outer_bound(l1)], pl_bot)

# Face 2: top (valid)
l2 = f.edge_loop([oe(e_t0), oe(e_t1), oe(e_t2), oe(e_t3)])
face2 = f.advanced_face([f.face_outer_bound(l2)], pl_top)

# Face 3: front — defect: same_sense=False (reversed normal)
l3 = f.edge_loop([oe(e_b0), oe(e_v1), oe(e_t0, False), oe(e_v0, False)])
face3 = f.advanced_face([f.face_outer_bound(l3)], pl_front, False)  # same_sense=False

# Face 4: back — defect: duplicate ORIENTED_EDGE (e_b2 appears twice)
l4 = f.edge_loop([oe(e_b2), oe(e_b2, False), oe(e_v3), oe(e_t2, False)])
face4 = f.advanced_face([f.face_outer_bound(l4)], pl_back)

# Face 5: right — defect: gap: one edge goes to v010g (1e-3 short of v010)
l5 = f.edge_loop([oe(e_b1), oe(e_v2), oe(e_t1, False), oe(e_v1, False)])
face5 = f.advanced_face([f.face_outer_bound(l5)], pl_right)

# Face 6: left (valid)
l6 = f.edge_loop([oe(e_b3), oe(e_v0), oe(e_t3, False), oe(e_v3, False)])
face6 = f.advanced_face([f.face_outer_bound(l6)], pl_left)

shell = f.closed_shell([face1, face2, face3, face4, face5, face6])
msb = f.manifold_solid_brep(shell)
f.add_product_chain(msb, mode="brep_shape")
