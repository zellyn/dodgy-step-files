"""Ps008 — Inch-valued coordinates labeled as millimetres.

Catalog claim: The SI_UNIT context declares LENGTH_MEASURE in mm.  The
CARTESIAN_POINTs and VECTORs encode coordinate values that the producer
intended as inches (e.g., a "100mm cube" whose vertices are (0,0,0) and
(100,100,100) but where 100 is actually the inch value, making the real-world
dimension 2540 mm).  The kernel cannot detect this from the file alone; both
unit declaration and coordinates are individually well-formed.  Kernel accepts
the file silently; tier-3 introspection (cross-checking PRODUCT.name
conventions against AABB extents) reveals the mismatch.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology: a 100x100x100
cube IS wired into the CLOSED_SHELL / MANIFOLD_SOLID_BREP whose enclosing
PRODUCT_DEFINITION_CONTEXT declares SI mm — but the cube coordinates represent
inch values, making it 2540x2540x2540 mm in reality.  The defect lives in the
mismatch between the geometry embedded in the faces and the declared unit
context of the product chain.

Tier-3 assertions:
  - face[0].area >= 99
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must warn.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps008",
    defect=(
        "100x100x100 cube with SI_UNIT mm context; coordinates encode inch values "
        "(100 in = 2540 mm) but declared as mm; unit/coordinate mismatch IS wired into "
        "CLOSED_SHELL of MANIFOLD_SOLID_BREP under SI-mm product context; "
        "kernel accepts silently; AABB check reveals 100-unit extents in 'mm' file"
    ),
)

# ── Cube with 100-unit coordinates (intended as inches, labeled mm) ───────────
# A "100 inch cube" whose coordinates are all exactly 100 — but the file
# declares SI millimetres.  Downstream tools checking AABB vs expected 100mm
# class will flag the 2540× scale discrepancy.
S = 100.0  # "100" in the producer's intended unit (inches), declared as mm

pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),  # 0
    f.cartesian_point((  S, 0.0, 0.0)),  # 1
    f.cartesian_point((  S,   S, 0.0)),  # 2
    f.cartesian_point((0.0,   S, 0.0)),  # 3
    f.cartesian_point((0.0, 0.0,   S)),  # 4
    f.cartesian_point((  S, 0.0,   S)),  # 5
    f.cartesian_point((  S,   S,   S)),  # 6
    f.cartesian_point((0.0,   S,   S)),  # 7
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d  = f.direction((dx, dy, dz))
    v  = f.vector(d, length)
    ln = f.line(pts[ia], v)
    return f.edge_curve(vts[ia], vts[ib], ln)

e_bot_f = le(0, 1,  1, 0, 0, S)
e_bot_r = le(1, 2,  0, 1, 0, S)
e_bot_b = le(3, 2,  1, 0, 0, S)
e_bot_l = le(0, 3,  0, 1, 0, S)
e_top_f = le(4, 5,  1, 0, 0, S)
e_top_r = le(5, 6,  0, 1, 0, S)
e_top_b = le(7, 6,  1, 0, 0, S)
e_top_l = le(4, 7,  0, 1, 0, S)
e_v0    = le(0, 4,  0, 0, 1, S)
e_v1    = le(1, 5,  0, 0, 1, S)
e_v2    = le(2, 6,  0, 0, 1, S)
e_v3    = le(3, 7,  0, 0, 1, S)

def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

pl_bot = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
pl_top = mk_plane(0, 0, S,  0, 0, 1,  1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane(0, S, 0,  0, 1, 0,  1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(S, 0, 0,  1, 0, 0,  0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]
shell = f.closed_shell(all_faces, name="ps008_inch_cube_mislabeled_mm")
msb   = f.manifold_solid_brep(shell, name="ps008_100in_cube_declared_mm")

# The CATALOG MECHANISM: unit mismatch IS the product chain — the 100-unit cube
# geometry IS in the CLOSED_SHELL of the MANIFOLD_SOLID_BREP, and the file's
# SI_UNIT declaration (added by StepFile) declares these as mm.
f.add_product_chain(msb, mode="brep_shape")
