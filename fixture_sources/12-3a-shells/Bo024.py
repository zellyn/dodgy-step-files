"""Bo024 — Closed shell whose face orientations imply negative volume.

Catalog claim: A MANIFOLD_SOLID_BREP references a closed shell whose faces
are collectively oriented inward; the divergence theorem applied to the shell
yields a negative volume.

Mechanism IS the CLOSED_SHELL face/same_sense topology: a watertight unit-cube
CLOSED_SHELL is built where ALL SIX ADVANCED_FACEs have same_sense=.F. — each
face normal points toward the interior (inward). The flipped same_sense IS wired
into every ADVANCED_FACE entity inside the CLOSED_SHELL, making the shell
inside-out. OCCT's OrientClosedSolid reports negative volume.

Tier-3 assertions: face[0].surface_type == "plane", face[5].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo024",
    defect=(
        "CLOSED_SHELL unit-cube where all 6 ADVANCED_FACEs have same_sense=.F.; "
        "all face normals point inward IS wired into closed-shell face topology; "
        "divergence theorem yields negative volume; OCCT OrientClosedSolid fires"
    ),
)

# ── Build a watertight unit cube with ALL faces oriented inward ───────────────
# 8 corner vertices
pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),  # 0 BLL
    f.cartesian_point((1.0, 0.0, 0.0)),  # 1 BRL
    f.cartesian_point((1.0, 1.0, 0.0)),  # 2 BRR
    f.cartesian_point((0.0, 1.0, 0.0)),  # 3 BLR
    f.cartesian_point((0.0, 0.0, 1.0)),  # 4 TLL
    f.cartesian_point((1.0, 0.0, 1.0)),  # 5 TRL
    f.cartesian_point((1.0, 1.0, 1.0)),  # 6 TRR
    f.cartesian_point((0.0, 1.0, 1.0)),  # 7 TLR
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d = f.direction((dx, dy, dz)); v = f.vector(d, length)
    return f.edge_curve(vts[ia], vts[ib], f.line(pts[ia], v))

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
    orig2 = f.cartesian_point((px, py, pz))
    zd = f.direction((zx, zy, zz)); xd = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig2, zd, xd))

def face4(edges_with_ori, plane, same_sense):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    # same_sense=False IS the inward-pointing defect
    return f.advanced_face([f.face_outer_bound(loop)], plane, same_sense=same_sense)

# Plane normals defined conventionally outward — but same_sense=.F. flips them inward
pl_bot = mk_plane(0, 0, 0,  0, 0,-1, 1, 0, 0)
pl_top = mk_plane(0, 0, 1,  0, 0, 1, 1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0, 1, 0, 0)
pl_bck = mk_plane(0, 1, 0,  0, 1, 0, 1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0, 0, 1, 0)
pl_rgt = mk_plane(1, 0, 0,  1, 0, 0, 0, 1, 0)

# ── CATALOG MECHANISM: all 6 faces have same_sense=.F. — inward normals ───────
# Byte assertion: contains(b'ADVANCED_FACE')
# Byte assertion: contains(b'CLOSED_SHELL')
# All same_sense flags are False → normals point inward → negative volume
f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot, False)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top, False)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_frt, False)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_bck, False)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)], pl_lft, False)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)], pl_rgt, False)

shell = f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name="bo024_inward")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('bo024_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
