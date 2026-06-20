"""Tsh186 — ShapeFix_Solid.SolidFromShell orientation-infinite-point non-closed shell.

Catalog claim: BRepClass3d_SolidClassifier.PerformInfinitePoint tests shell
orientation by containment at infinity. Non-closed shells with dangling boundary
faces produce undefined State() results. Classifier assumes watertight closure but
receives open topology, causing IN/OUT misclassification.

Mechanism IS the SHELL_BASED_SURFACE_MODEL face topology: 5 faces forming a
box-without-lid (open box) are wired as a SHELL_BASED_SURFACE_MODEL. The shell
is not closed (no top face), yet the face normals are set so SolidFromShell's
PerformInfinitePoint call produces an inconsistent IN/OUT State() result.

Tier-3 assertion: n_faces_total == 5
Expected: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh186",
    defect=(
        "OPEN_SHELL with 5 faces: 4 walls + 1 floor of unit box (no lid); "
        "shell is NOT closed; face normals all point outward as if it were closed; "
        "BRepClass3d_SolidClassifier.PerformInfinitePoint on this open shell "
        "produces undefined IN/OUT State() — misclassification trigger IS wired "
        "into SHELL_BASED_SURFACE_MODEL face topology"
    ),
)

# Unit box 0..1 in X,Y; height 0..1 in Z; NO top face → open shell
# Corners: 4 bottom, 4 top
pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),  # 0 bl-bot
    f.cartesian_point((1.0, 0.0, 0.0)),  # 1 br-bot
    f.cartesian_point((1.0, 1.0, 0.0)),  # 2 tr-bot
    f.cartesian_point((0.0, 1.0, 0.0)),  # 3 tl-bot
    f.cartesian_point((0.0, 0.0, 1.0)),  # 4 bl-top
    f.cartesian_point((1.0, 0.0, 1.0)),  # 5 br-top
    f.cartesian_point((1.0, 1.0, 1.0)),  # 6 tr-top
    f.cartesian_point((0.0, 1.0, 1.0)),  # 7 tl-top
]
vts = [f.vertex_point(p) for p in pts]

def le(ia, ib, dx, dy, dz, length):
    d   = f.direction((dx, dy, dz))
    vec = f.vector(d, length)
    ln  = f.line(pts[ia], vec)
    return f.edge_curve(vts[ia], vts[ib], ln)

# Bottom ring
e_bot_f = le(0, 1,  1, 0, 0, 1.0)
e_bot_r = le(1, 2,  0, 1, 0, 1.0)
e_bot_b = le(3, 2,  1, 0, 0, 1.0)
e_bot_l = le(0, 3,  0, 1, 0, 1.0)
# Vertical edges
e_v0 = le(0, 4,  0, 0, 1, 1.0)
e_v1 = le(1, 5,  0, 0, 1, 1.0)
e_v2 = le(2, 6,  0, 0, 1, 1.0)
e_v3 = le(3, 7,  0, 0, 1, 1.0)
# Top ring (partial — 4 edges, but no top face)
e_top_f = le(4, 5,  1, 0, 0, 1.0)
e_top_r = le(5, 6,  0, 1, 0, 1.0)
e_top_b = le(7, 6,  1, 0, 0, 1.0)
e_top_l = le(4, 7,  0, 1, 0, 1.0)

def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
    orig = f.cartesian_point((px, py, pz))
    zd   = f.direction((zx, zy, zz))
    xd   = f.direction((xx, xy, xz))
    return f.plane(f.axis2_placement_3d(orig, zd, xd))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop)], plane)

# 5 faces: floor + 4 walls. No lid. Normals point outward.
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

# CATALOG MECHANISM: open shell — 5 faces, no top
shell = f.open_shell([f_bot, f_frt, f_bck, f_lft, f_rgt], name="tsh186_open_box")
sbsm  = f.shell_based_surface_model([shell], name="tsh186_unclosed_solid")
f.add_product_chain(sbsm, mode="surface_shape")
