"""Xp014 — Open shell as MANIFOLD_SOLID_BREP.outer × tolerance-violation × unit mismatch."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

# Defect 1: MANIFOLD_SOLID_BREP.outer references OPEN_SHELL (spec requires CLOSED_SHELL)
# Defect 2: tolerance hierarchy inverted (vertex_tol > edge_tol)
# Defect 3: coordinates are 1000× too small (metres authored, mm declared in context)
# → Coordinates in range 0.001 with mm declared

f = StepFile(catalog_id="Xp014",
             defect='Open shell as MANIFOLD_SOLID_BREP.outer x tolerance-violation x unit mismatch')

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1.0e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Defect 3: coordinates 1e-3 scale (metres authored, mm declared)
# A "1 metre cube" written as 0.001..0.002 in mm context
s = 0.001  # scale factor = 1/1000 (metre to mm mismatch)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((s,   0.0, 0.0))
p2 = f.cartesian_point((s,   s,   0.0))
p3 = f.cartesian_point((0.0, s,   0.0))
p4 = f.cartesian_point((0.0, 0.0, s  ))
p5 = f.cartesian_point((s,   0.0, s  ))
p6 = f.cartesian_point((s,   s,   s  ))
p7 = f.cartesian_point((0.0, s,   s  ))

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4); v5 = f.vertex_point(p5)
v6 = f.vertex_point(p6); v7 = f.vertex_point(p7)

# 12 cube edges
eb0 = line_edge(p0, p1, v0, v1); eb1 = line_edge(p1, p2, v1, v2)
eb2 = line_edge(p2, p3, v2, v3); eb3 = line_edge(p3, p0, v3, v0)
et0 = line_edge(p4, p5, v4, v5); et1 = line_edge(p5, p6, v5, v6)
et2 = line_edge(p6, p7, v6, v7); et3 = line_edge(p7, p4, v7, v4)
ev0 = line_edge(p0, p4, v0, v4); ev1 = line_edge(p1, p5, v1, v5)
ev2 = line_edge(p2, p6, v2, v6); ev3 = line_edge(p3, p7, v3, v7)

def oe(e, fwd=True):
    return f.oriented_edge(e, fwd)

def mkplane(ox, oy, oz, nx, ny, nz, rx, ry, rz):
    o = f.cartesian_point((ox, oy, oz))
    n = f.direction((nx, ny, nz))
    r = f.direction((rx, ry, rz))
    plc = f.axis2_placement_3d(o, n, r)
    return f.plane(plc)

pl_bot   = mkplane(0,0,0,   0,0,1,  1,0,0)
pl_top   = mkplane(0,0,s,   0,0,-1, 1,0,0)
pl_front = mkplane(0,0,0,   0,-1,0, 1,0,0)
pl_back  = mkplane(0,s,0,   0,1,0, -1,0,0)
pl_right = mkplane(s,0,0,   1,0,0,  0,1,0)

# 5-face open shell (missing one face → defect 1 when used in MANIFOLD_SOLID_BREP)
l_bot   = f.edge_loop([oe(eb0), oe(eb1), oe(eb2), oe(eb3)])
l_top   = f.edge_loop([oe(et0), oe(et1), oe(et2), oe(et3)])
l_front = f.edge_loop([oe(eb0), oe(ev1), oe(et0, False), oe(ev0, False)])
l_back  = f.edge_loop([oe(eb2), oe(ev3), oe(et2, False), oe(ev2, False)])
l_right = f.edge_loop([oe(eb1), oe(ev2), oe(et1, False), oe(ev1, False)])

face_bot   = f.advanced_face([f.face_outer_bound(l_bot)],   pl_bot)
face_top   = f.advanced_face([f.face_outer_bound(l_top)],   pl_top)
face_front = f.advanced_face([f.face_outer_bound(l_front)], pl_front)
face_back  = f.advanced_face([f.face_outer_bound(l_back)],  pl_back)
face_right = f.advanced_face([f.face_outer_bound(l_right)], pl_right)

# Defect 1: OPEN_SHELL (5 faces, not 6) used as MANIFOLD_SOLID_BREP.outer
shell = f.open_shell([face_bot, face_top, face_front, face_back, face_right])
msb = f.manifold_solid_brep(shell)  # builder accepts open_shell for defect demonstration
f.add_product_chain(msb, mode="brep_shape")

# Defect 2: tolerance hierarchy inverted: emit vertex-tolerance > edge-tolerance comments
f._emit_raw(
    "/* xp014 defect-2: vertex_tol=0.01 > edge_tol=0.001 — tolerance hierarchy inverted */"
)
f._emit_raw(
    f"/* xp014 defect-3: coordinates at scale {s} (metres); "
    f"context declares mm — 1000x mismatch */"
)
