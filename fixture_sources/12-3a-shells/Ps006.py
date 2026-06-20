"""Ps006 — Self-overlapping shell: one face double-covers a region of another.

Catalog claim: A "closed" OPEN_SHELL where a single planar region (the bottom
z=0 face) is represented TWICE: once as a full 1x1 unit square, and once as
the (0..0.5, 0..0.5) quadrant of the same PLANE.  Both faces appear in the
same OPEN_SHELL.  Edge-degree checks pass within each face's own loop.
Kernel accepts the file silently; tier-3 introspection (point-in-face count
over a sample grid) reveals certain points are "inside" two faces
simultaneously.  T-vertices appear at (0.5,0,0), (0.5,0.5,0), (0,0.5,0).

Mechanism IS the OPEN_SHELL / SHELL_BASED_SURFACE_MODEL face topology: the
double-coverage IS wired into the face list of the OPEN_SHELL — the large
bottom face AND the smaller quadrant face are both ADVANCED_FACEs on the same
supporting PLANE living inside the same SHELL_BASED_SURFACE_MODEL.

Tier-3 assertions:
  - n_edges_total >= 28
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must reject.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps006",
    defect=(
        "OPEN_SHELL for unit-cube bottom face contains BOTH a full 1x1 square face "
        "AND a 0.5x0.5 quadrant face on the same supporting PLANE at z=0; "
        "double-coverage IS wired into OPEN_SHELL face list of SHELL_BASED_SURFACE_MODEL; "
        "T-vertices appear at (0.5,0,0),(0.5,0.5,0),(0,0.5,0); BRepCheck passes"
    ),
)

# ── Corner points for unit cube (0..1) ───────────────────────────────────────
pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),  # 0
    f.cartesian_point((1.0, 0.0, 0.0)),  # 1
    f.cartesian_point((1.0, 1.0, 0.0)),  # 2
    f.cartesian_point((0.0, 1.0, 0.0)),  # 3
    f.cartesian_point((0.0, 0.0, 1.0)),  # 4
    f.cartesian_point((1.0, 0.0, 1.0)),  # 5
    f.cartesian_point((1.0, 1.0, 1.0)),  # 6
    f.cartesian_point((0.0, 1.0, 1.0)),  # 7
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

# Bottom ring
e_bot_f = le(0, 1,  1, 0, 0, 1.0)
e_bot_r = le(1, 2,  0, 1, 0, 1.0)
e_bot_b = le(3, 2,  1, 0, 0, 1.0)
e_bot_l = le(0, 3,  0, 1, 0, 1.0)
# Top ring
e_top_f = le(4, 5,  1, 0, 0, 1.0)
e_top_r = le(5, 6,  0, 1, 0, 1.0)
e_top_b = le(7, 6,  1, 0, 0, 1.0)
e_top_l = le(4, 7,  0, 1, 0, 1.0)
# Verticals
e_v0 = le(0, 4,  0, 0, 1, 1.0)
e_v1 = le(1, 5,  0, 0, 1, 1.0)
e_v2 = le(2, 6,  0, 0, 1, 1.0)
e_v3 = le(3, 7,  0, 0, 1, 1.0)

def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# ── Five non-bottom faces (clean, no overlap) ─────────────────────────────────
pl_top = mk_plane(0, 0, 1,  0, 0, 1,  1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane(0, 1, 0,  0, 1, 0,  1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(1, 0, 0,  1, 0, 0,  0, 1, 0)

f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

# ── CATALOG MECHANISM: bottom z=0 face appears TWICE in shell ─────────────────
# Face A: full 1x1 bottom square (standard cube bottom)
pl_bot = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)  # normal -Z (outward for bottom)
f_bot_full = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)

# Face B: 0.5x0.5 quadrant on the SAME supporting plane — the double-cover
# Four new points for the quadrant corners
qpts = [
    f.cartesian_point((0.0, 0.0, 0.0)),    # q0 shared corner
    f.cartesian_point((0.5, 0.0, 0.0)),    # q1
    f.cartesian_point((0.5, 0.5, 0.0)),    # q2  — T-vertex
    f.cartesian_point((0.0, 0.5, 0.0)),    # q3
]
qvts = [f.vertex_point(p) for p in qpts]

def qle(ia, ib, dx, dy, length):
    d  = f.direction((dx, dy, 0.0))
    v  = f.vector(d, length)
    ln = f.line(qpts[ia], v)
    return f.edge_curve(qvts[ia], qvts[ib], ln)

qe0 = qle(0, 1,  1, 0, 0.5)
qe1 = qle(1, 2,  0, 1, 0.5)
qe2 = qle(3, 2,  1, 0, 0.5)  # reverse direction edge
qe3 = qle(0, 3,  0, 1, 0.5)

# Same plane object (same z=0, normal -Z) — this is the overlap
pl_bot_dup = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
f_bot_quad = face4([(qe0,True),(qe1,True),(qe2,False),(qe3,False)], pl_bot_dup)

# ALL faces including both bottom representations in the same OPEN_SHELL
all_faces = [f_bot_full, f_bot_quad, f_top, f_frt, f_bck, f_lft, f_rgt]
shell = f.open_shell(all_faces, name="ps006_double_bottom")
sbsm  = f.shell_based_surface_model([shell], name="ps006_overlapping_shell")

f.add_product_chain(sbsm, mode="surface_shape")
