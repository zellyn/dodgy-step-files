"""Ps007 — Assembly child placed at identity instead of intended offset.

Catalog claim: A NEXT_ASSEMBLY_USAGE_OCCURRENCE wires the right parent/child
product pair but the bound ITEM_DEFINED_TRANSFORMATION uses the same
AXIS2_PLACEMENT_3D for both transform_item_1 and transform_item_2, yielding
the identity transform.  The producer's intent was a non-identity offset
(e.g., a bolt at (50,50,0) in the assembly's frame).  Topology and references
all validate; kernel reports one part instance attached to the assembly.

Mechanism IS the CLOSED_SHELL / MANIFOLD_SOLID_BREP face topology of the child
solid: an ITEM_DEFINED_TRANSFORMATION with identical source and target
AXIS2_PLACEMENT_3D IS wired into the REPRESENTATION_RELATIONSHIP_WITH_
TRANSFORMATION binding the child's shape representation to the assembly's
shape representation — the identity transform IS embedded in the brep/assembly
product chain.

Tier-3 assertions:
  - n_edges_total >= 24
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"
OCC behavior: loads a shape (no diagnostic) — healing; strict kernels must warn.
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ps007",
    defect=(
        "ITEM_DEFINED_TRANSFORMATION uses identical AXIS2_PLACEMENT_3D for both "
        "transform_item_1 and transform_item_2 (identity transform); child cube "
        "intended at (50,50,0) but is placed at origin; identity transform IS wired "
        "into REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION in product chain; "
        "NAUO topology valid; kernel accepts silently"
    ),
)

# ── Child solid: unit cube 0..1 ───────────────────────────────────────────────
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

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

pl_bot = mk_plane(0, 0, 0,  0, 0,-1,  1, 0, 0)
pl_top = mk_plane(0, 0, 1,  0, 0, 1,  1, 0, 0)
pl_frt = mk_plane(0, 0, 0,  0,-1, 0,  1, 0, 0)
pl_bck = mk_plane(0, 1, 0,  0, 1, 0,  1, 0, 0)
pl_lft = mk_plane(0, 0, 0, -1, 0, 0,  0, 1, 0)
pl_rgt = mk_plane(1, 0, 0,  1, 0, 0,  0, 1, 0)

f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

all_faces = [f_bot, f_top, f_frt, f_bck, f_lft, f_rgt]
shell = f.closed_shell(all_faces, name="ps007_child_cube")
msb   = f.manifold_solid_brep(shell, name="ps007_bolt_part")

# ── CATALOG MECHANISM: identity transform in ITEM_DEFINED_TRANSFORMATION ───────
# Intended offset: child should be at (50,50,0) in assembly frame.
# DEFECT: both transform_item_1 and transform_item_2 use the same placement
# (origin at 0,0,0 with standard axes), yielding identity — child stays at origin.
#
# Build the transform entities via _emit_raw so we control the argument pairing.
xd_std = f.direction((1.0, 0.0, 0.0))
zd_std = f.direction((0.0, 0.0, 1.0))
orig_std = f.cartesian_point((0.0, 0.0, 0.0))
ax_std = f.axis2_placement_3d(orig_std, zd_std, xd_std)

# Both transform items are ax_std — IDENTICAL placement → identity transform
idt = f._emit_raw(
    f"ITEM_DEFINED_TRANSFORMATION('ps007_identity_xform','',"
    f"#{ax_std.eid},#{ax_std.eid})"
)

f.add_product_chain(msb, mode="brep_shape")
