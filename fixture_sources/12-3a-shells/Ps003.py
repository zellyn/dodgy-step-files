"""Ps003 — Single ADVANCED_FACE with same_sense flipped on outer skin.

Catalog claim: A unit cube where five faces correctly orient outward but the
TOP face has ADVANCED_FACE.same_sense=.F., effectively inverting that face's
normal so it points down into the solid instead of up.  Topology is consistent
(every edge has degree 2), the shell is closed, and the kernel reports a valid
solid.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: the top face
of a unit cube has same_sense=.F. while its underlying PLANE.position.axis still
points +Z.  This flipped same_sense IS wired directly into the ADVANCED_FACE
entity that IS in the CLOSED_SHELL of the MANIFOLD_SOLID_BREP.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must reject.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps003",
    defect=(
        "Unit cube top ADVANCED_FACE has same_sense=.F. while PLANE.axis points +Z; "
        "effective face normal points DOWN into solid instead of up; other 5 faces "
        "correct; flipped same_sense IS wired into ADVANCED_FACE in CLOSED_SHELL "
        "of MANIFOLD_SOLID_BREP; BRepCheck passes, point-in-solid tests fail"
    ),
)

# ── Unit cube 0..1 ────────────────────────────────────────────────────────────
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

def face4(edges_with_ori, plane, same_sense=True):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    fob  = f.face_outer_bound(loop)
    # same_sense controls ADVANCED_FACE's third arg
    ss   = ".T." if same_sense else ".F."
    return f._emit_raw(
        f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},{ss})"
    )

# ── Five normal faces (correct outward normals, same_sense=.T.) ───────────────
pl_bot = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane(0, 1, 0,  0, 1, 0,  1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(1, 0, 0,  1, 0, 0,  0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

# ── CATALOG MECHANISM: top face with same_sense=.F. ──────────────────────────
# PLANE.axis points +Z (correct outward direction for top face), but
# same_sense=.F. inverts the effective normal to point -Z (into the solid).
pl_top = mk_plane(0, 0, 1,  0, 0, 1,  1, 0, 0)  # axis +Z (correct)
# Loop orientation is consistent with the flipped sense so BRepCheck still passes
f_top  = face4(
    [(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)],
    pl_top,
    same_sense=False,  # ← THE DEFECT: effective normal now points DOWN into solid
)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]

# CLOSED_SHELL IS the outer shell of MANIFOLD_SOLID_BREP — flipped same_sense wired in
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ps003_top_face_flipped',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ps003_cube_one_face_flipped',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
