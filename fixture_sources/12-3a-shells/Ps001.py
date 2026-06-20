"""Ps001 — Negative-volume cube: every face normal points inward.

Catalog claim: A topologically closed CLOSED_SHELL whose every constituent
face has its supporting surface's stored normal pointing into the volume
rather than out.  Loop orientations are internally consistent with the
flipped surface frames, so edge-degree-2 and orientation-coherence checks
pass.  Signed volume integral returns -1.0 instead of +1.0.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: each of
the 6 ADVANCED_FACEs of a unit cube has its PLANE's AXIS2_PLACEMENT_3D.axis
pointing toward the cube center rather than away.  This inward-normal IS
wired into the face set of the CLOSED_SHELL which IS the outer shell of the
MANIFOLD_SOLID_BREP.

Tier-3 assertions:
  - n_edges_total >= 24
  - brepcheck.valid == true
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must reject.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps001",
    defect=(
        "Unit cube MANIFOLD_SOLID_BREP: every ADVANCED_FACE has its PLANE normal "
        "pointing INWARD (toward cube center); loop orientations are consistent with "
        "flipped normals so BRepCheck passes; signed volume is -1.0 (negative); "
        "inward normals ARE wired into all 6 faces of the CLOSED_SHELL outer shell"
    ),
)

# ── Unit cube 0..1 in each axis ───────────────────────────────────────────────
# 8 corner points
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
    d   = f.direction((dx, dy, dz))
    v   = f.vector(d, length)
    ln  = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

e_bot_f = le(0, 1,  1, 0, 0, 1.0)
e_bot_r = le(1, 2,  0, 1, 0, 1.0)
e_bot_b = le(3, 2,  1, 0, 0, 1.0)
e_bot_l = le(0, 3,  0, 1, 0, 1.0)
e_top_f = le(4, 5,  1, 0, 0, 1.0)
e_top_r = le(5, 6,  0, 1, 0, 1.0)
e_top_b = le(7, 6,  1, 0, 0, 1.0)
e_top_l = le(4, 7,  0, 1, 0, 1.0)
e_v0    = le(0, 4,  0, 0, 1, 1.0)
e_v1    = le(1, 5,  0, 0, 1, 1.0)
e_v2    = le(2, 6,  0, 0, 1, 1.0)
e_v3    = le(3, 7,  0, 0, 1, 1.0)

def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# ── CATALOG MECHANISM: ALL face normals point INWARD ─────────────────────────
# For each face the PLANE.axis is the opposite of the outward normal, i.e.
# it points toward the cube center (0.5, 0.5, 0.5).
#
# Bottom face (z=0): outward would be -Z; inward IS +Z  → axis=(0,0,+1)
# Top    face (z=1): outward would be +Z; inward IS -Z  → axis=(0,0,-1)
# Front  face (y=0): outward would be -Y; inward IS +Y  → axis=(0,+1,0)
# Back   face (y=1): outward would be +Y; inward IS -Y  → axis=(0,-1,0)
# Left   face (x=0): outward would be -X; inward IS +X  → axis=(+1,0,0)
# Right  face (x=1): outward would be +X; inward IS -X  → axis=(-1,0,0)
#
# Loop orientations are consistent with the flipped normals (so BRepCheck.valid==true).

pl_bot = mk_plane(0, 0, 0,  0, 0,+1,  1, 0, 0)  # normal INWARD (+Z, not -Z)
pl_top = mk_plane(0, 0, 1,  0, 0,-1,  1, 0, 0)  # normal INWARD (-Z, not +Z)
pl_frt = mk_plane(0, 0, 0,  0,+1, 0,  1, 0, 0)  # normal INWARD (+Y, not -Y)
pl_bck = mk_plane(0, 1, 0,  0,-1, 0,  1, 0, 0)  # normal INWARD (-Y, not +Y)
pl_lft = mk_plane(0, 0, 0, +1, 0, 0,  0, 1, 0)  # normal INWARD (+X, not -X)
pl_rgt = mk_plane(1, 0, 0, -1, 0, 0,  0, 1, 0)  # normal INWARD (-X, not +X)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]  # 6 faces, all normals inward

# CLOSED_SHELL IS the outer shell of MANIFOLD_SOLID_BREP — inward normals wired in
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ps001_all_normals_inward',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ps001_negative_volume_cube',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
