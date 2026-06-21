"""Xp008 — Empty EDGE_LOOP × empty FACE_OUTER_BOUND × otherwise-valid solid."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp008",
             defect='Empty EDGE_LOOP x empty FACE_OUTER_BOUND x otherwise-valid solid')

# Build a 6-face box where face 5 has empty EDGE_LOOP and face 6 has $ face_geometry.
# Coordinates: unit cube 0..1 in all axes

def mkpt(xyz):
    return f.cartesian_point(xyz)

def mkv(p):
    return f.vertex_point(p)

def mkdir(d):
    return f.direction(d)

def mkvec(d, l):
    return f.vector(d, l)

def mkline(p, v):
    return f.line(p, v)

def mkedge(va, vb, ln):
    return f.edge_curve(va, vb, ln)

def oe(e, s=True):
    return f.oriented_edge(e, s)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# 8 vertices of unit cube
p000 = mkpt((0.0, 0.0, 0.0)); p100 = mkpt((1.0, 0.0, 0.0))
p110 = mkpt((1.0, 1.0, 0.0)); p010 = mkpt((0.0, 1.0, 0.0))
p001 = mkpt((0.0, 0.0, 1.0)); p101 = mkpt((1.0, 0.0, 1.0))
p111 = mkpt((1.0, 1.0, 1.0)); p011 = mkpt((0.0, 1.0, 1.0))

v000 = mkv(p000); v100 = mkv(p100); v110 = mkv(p110); v010 = mkv(p010)
v001 = mkv(p001); v101 = mkv(p101); v111 = mkv(p111); v011 = mkv(p011)

# 12 edges (each edge shared by 2 faces)
e_bot0 = line_edge(p000, p100, v000, v100)  # bottom face edges
e_bot1 = line_edge(p100, p110, v100, v110)
e_bot2 = line_edge(p110, p010, v110, v010)
e_bot3 = line_edge(p010, p000, v010, v000)
e_top0 = line_edge(p001, p101, v001, v101)  # top face edges
e_top1 = line_edge(p101, p111, v101, v111)
e_top2 = line_edge(p111, p011, v111, v011)
e_top3 = line_edge(p011, p001, v011, v001)
e_v0 = line_edge(p000, p001, v000, v001)  # vertical edges
e_v1 = line_edge(p100, p101, v100, v101)
e_v2 = line_edge(p110, p111, v110, v111)
e_v3 = line_edge(p010, p011, v010, v011)

# Axis placements for each face
orig = f.cartesian_point((0.0, 0.0, 0.0))
zd = f.direction((0.0, 0.0, 1.0)); xd = f.direction((1.0, 0.0, 0.0))
plc_z = f.axis2_placement_3d(orig, zd, xd)
plane_bot = f.plane(plc_z)

orig_top = f.cartesian_point((0.0, 0.0, 1.0))
zd_neg = f.direction((0.0, 0.0, -1.0))
plc_top = f.axis2_placement_3d(orig_top, zd_neg, xd)
plane_top = f.plane(plc_top)

orig_front = f.cartesian_point((0.0, 0.0, 0.0))
yd_neg = f.direction((0.0, -1.0, 0.0)); xd_f = f.direction((1.0, 0.0, 0.0))
plc_front = f.axis2_placement_3d(orig_front, yd_neg, xd_f)
plane_front = f.plane(plc_front)

orig_back = f.cartesian_point((0.0, 1.0, 0.0))
yd = f.direction((0.0, 1.0, 0.0)); xd_b = f.direction((-1.0, 0.0, 0.0))
plc_back = f.axis2_placement_3d(orig_back, yd, xd_b)
plane_back = f.plane(plc_back)

orig_right = f.cartesian_point((1.0, 0.0, 0.0))
xd_right = f.direction((1.0, 0.0, 0.0)); yd_r = f.direction((0.0, 1.0, 0.0))
plc_right = f.axis2_placement_3d(orig_right, xd_right, yd_r)
plane_right = f.plane(plc_right)

orig_left = f.cartesian_point((0.0, 0.0, 0.0))
xd_neg = f.direction((-1.0, 0.0, 0.0)); yd_l = f.direction((0.0, -1.0, 0.0))
plc_left = f.axis2_placement_3d(orig_left, xd_neg, yd_l)
plane_left = f.plane(plc_left)

# Face 1: bottom (valid)
loop1 = f.edge_loop([oe(e_bot0), oe(e_bot1), oe(e_bot2), oe(e_bot3)])
face1 = f.advanced_face([f.face_outer_bound(loop1)], plane_bot)

# Face 2: top (valid)
loop2 = f.edge_loop([oe(e_top0), oe(e_top1), oe(e_top2), oe(e_top3)])
face2 = f.advanced_face([f.face_outer_bound(loop2)], plane_top)

# Face 3: front (valid)
loop3 = f.edge_loop([oe(e_bot0), oe(e_v1), oe(e_top0, False), oe(e_v0, False)])
face3 = f.advanced_face([f.face_outer_bound(loop3)], plane_front)

# Face 4: back (valid)
loop4 = f.edge_loop([oe(e_bot2), oe(e_v3), oe(e_top2, False), oe(e_v2, False)])
face4 = f.advanced_face([f.face_outer_bound(loop4)], plane_back)

# Face 5: right (valid)
loop5 = f.edge_loop([oe(e_bot1), oe(e_v2), oe(e_top1, False), oe(e_v1, False)])
face5 = f.advanced_face([f.face_outer_bound(loop5)], plane_right)

# Face 6: Defect — empty EDGE_LOOP (left face)
empty_loop = f._emit_raw("EDGE_LOOP('',())")
fob_empty = f.face_outer_bound(empty_loop)
face6 = f.advanced_face([fob_empty], plane_left)

# Face 7 (extra slot for #7): face_geometry = $ (NULL — unresolved)
loop7 = f.edge_loop([oe(e_bot3), oe(e_v0), oe(e_top3, False), oe(e_v3, False)])
fob7 = f.face_outer_bound(loop7)
# face_geometry slot is $ (None)
face7 = f._emit_raw(f"ADVANCED_FACE('null_geom',(#{fob7.eid}),$,.T.)")

# CLOSED_SHELL with all 7 faces
shell = f.closed_shell([face1, face2, face3, face4, face5, face6])
# MANIFOLD_SOLID_BREP uses the closed_shell
msb = f.manifold_solid_brep(shell)
f.add_product_chain(msb, mode="brep_shape")
