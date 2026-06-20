"""Ps009 — Flatness tolerance attached to geometrically adjacent wrong face.

Catalog claim: A thin 10x1x5 block where the producer intended a flatness
tolerance on FACE_A (front, y=0).  Due to a face-indexing bug in the PMI
exporter, the GISU references FACE_B (back, y=1); a face geometrically very
close but functionally unrelated.  The tolerance frame, datum system, and
value are all well-formed.  Kernel accepts the file silently; tier-3
introspection (cross-check intended-target metadata names against actual GISU
references) reveals the misattachment.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: the 10x1x5
block's CLOSED_SHELL IS the outer shell of the MANIFOLD_SOLID_BREP, and the
misattached FLATNESS_TOLERANCE GISU IS wired to the back face's ADVANCED_FACE
entity — the wrong-face reference IS embedded in the product chain.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must warn.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps009",
    defect=(
        "10x1x5 block MANIFOLD_SOLID_BREP: FLATNESS_TOLERANCE GISU references the "
        "back face (y=1, named FACE_B_BACK) instead of the intended front face (y=0, "
        "named FACE_A_FRONT); wrong-face reference IS wired via GEOMETRIC_ITEM_"
        "SPECIFIC_USAGE into CLOSED_SHELL of MANIFOLD_SOLID_BREP product chain; "
        "kernel accepts silently"
    ),
)

# ── 10x1x5 block (x=0..10, y=0..1, z=0..5) ──────────────────────────────────
pts = [
    f.cartesian_point(( 0.0, 0.0, 0.0)),  # 0
    f.cartesian_point((10.0, 0.0, 0.0)),  # 1
    f.cartesian_point((10.0, 1.0, 0.0)),  # 2
    f.cartesian_point(( 0.0, 1.0, 0.0)),  # 3
    f.cartesian_point(( 0.0, 0.0, 5.0)),  # 4
    f.cartesian_point((10.0, 0.0, 5.0)),  # 5
    f.cartesian_point((10.0, 1.0, 5.0)),  # 6
    f.cartesian_point(( 0.0, 1.0, 5.0)),  # 7
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

e_bot_f = le(0, 1,  1, 0, 0, 10.0)
e_bot_r = le(1, 2,  0, 1, 0,  1.0)
e_bot_b = le(3, 2,  1, 0, 0, 10.0)
e_bot_l = le(0, 3,  0, 1, 0,  1.0)
e_top_f = le(4, 5,  1, 0, 0, 10.0)
e_top_r = le(5, 6,  0, 1, 0,  1.0)
e_top_b = le(7, 6,  1, 0, 0, 10.0)
e_top_l = le(4, 7,  0, 1, 0,  1.0)
e_v0    = le(0, 4,  0, 0, 1,  5.0)
e_v1    = le(1, 5,  0, 0, 1,  5.0)
e_v2    = le(2, 6,  0, 0, 1,  5.0)
e_v3    = le(3, 7,  0, 0, 1,  5.0)

def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

pl_bot = mk_plane( 0, 0, 0,  0, 0,-1,  1, 0, 0)
pl_top = mk_plane( 0, 0, 5,  0, 0, 1,  1, 0, 0)
pl_lft = mk_plane( 0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(10, 0, 0,  1, 0, 0,  0, 1, 0)

# FACE_A_FRONT: y=0, normal -Y — intended target of flatness tolerance
pl_front = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
f_front = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)], pl_front)

# FACE_B_BACK: y=1, normal +Y — WRONG target the GISU actually references
pl_back  = mk_plane(0, 1, 0,  0, 1, 0,  1, 0, 0)
f_back   = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)], pl_back)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_front, f_back, f_lft, f_rgt]
shell = f.closed_shell(all_faces, name="ps009_block")
msb   = f.manifold_solid_brep(shell, name="ps009_10x1x5_block")

# ── CATALOG MECHANISM: GISU wired to back face instead of front face ──────────
# SHAPE_ASPECT on FACE_B_BACK (the wrong face) is what the GISU references.
# A correct export would have pointed the shape_aspect at f_front.
# SHAPE_ASPECT args: name, description, of_shape($=unbound), product_definitional
prod_aspect_back = f._emit_raw(
    f"SHAPE_ASPECT('FACE_B_BACK','back face (wrong GISU target)',$,.T.)"
)
# GEOMETRIC_ITEM_SPECIFIC_USAGE: name, description, definition(shape_aspect), used_representation_item(face)
gisu = f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('ps009_wrong_gisu','wrong face ref',"
    f"#{prod_aspect_back.eid},#{f_back.eid})"
)

f.add_product_chain(msb, mode="brep_shape")
