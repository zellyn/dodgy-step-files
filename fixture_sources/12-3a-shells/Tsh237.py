"""Tsh237 — Two disjoint CLOSED_SHELLs, NO BREP_WITH_VOIDS wrapper
(unstructured shell soup forcing compound-of-2-solids classification).

Catalog claim (occt-coverage GAP `tkshh-solid-unstructured-multishell`,
variant b): the disjoint sibling of Tsh236. Two watertight CLOSED_SHELLs with
genuinely disjoint bounding boxes are wired directly into one
SHELL_BASED_SURFACE_MODEL, again with no BREP_WITH_VOIDS/MANIFOLD_SOLID_BREP
wrapper. Since neither shell contains the other, a receiver that wants
solids from this shell soup must classify it as a COMPOUND OF TWO SEPARATE
SOLIDS (not one solid-with-void, as Tsh236's nested case forces) — the
opposite branch of ShapeFix_Solid::CreateSolids' containment classification.

Live-verified behavior (this worktree's OCP/OCCT 7.8.1, default
STEPControl_Reader.TransferRoots): as with Tsh236, the default reader
returns a TopoDS_COMPOUND of the 2 shells verbatim (0 solids) — the
compound-of-2-solids promotion is the opt-in ShapeFix_Solid::CreateSolids
classification step, not part of default transfer. Recorded honestly below,
not mirrored from an unrelated fixture.

Byte assertions:
  - count_entity_def(b'CLOSED_SHELL') == 2
  - count_entity_def(b'BREP_WITH_VOIDS') == 0
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 0

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 12
  - face[0].surface_type == "plane"

live oracle (computed via validate2.py against this worktree's bytes):
  occt=shape(1)/shape(1) gmsh=shape(54)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh237",
    defect=(
        "Two CLOSED_SHELLs (box A at x in [0,10], box B at x in [30,40] — "
        "genuinely disjoint bounding boxes) wired directly into ONE "
        "SHELL_BASED_SURFACE_MODEL with no BREP_WITH_VOIDS or "
        "MANIFOLD_SOLID_BREP wrapper — unstructured shell soup; a receiver "
        "wanting solids must classify this as a compound of TWO separate "
        "solids (opposite branch from Tsh236's nested case), via "
        "ShapeFix_Solid::CreateSolids containment classification, since no "
        "author-declared solid/voids structure is given"
    ),
)


def make_box_closed_shell(ox, oy, oz, sx, sy, sz, tag):
    """Build a watertight CLOSED_SHELL box at origin (ox,oy,oz), size (sx,sy,sz)."""
    pts = [
        f.cartesian_point((ox,    oy,    oz   )),
        f.cartesian_point((ox+sx, oy,    oz   )),
        f.cartesian_point((ox+sx, oy+sy, oz   )),
        f.cartesian_point((ox,    oy+sy, oz   )),
        f.cartesian_point((ox,    oy,    oz+sz)),
        f.cartesian_point((ox+sx, oy,    oz+sz)),
        f.cartesian_point((ox+sx, oy+sy, oz+sz)),
        f.cartesian_point((ox,    oy+sy, oz+sz)),
    ]
    vts = [f.vertex_point(p) for p in pts]

    def le(ia, ib, dx, dy, dz, length):
        d = f.direction((dx, dy, dz)); v = f.vector(d, length)
        ln = f.line(pts[ia], v)
        return f.edge_curve(vts[ia], vts[ib], ln)

    e_bot_f = le(0, 1,  1, 0, 0, sx)
    e_bot_r = le(1, 2,  0, 1, 0, sy)
    e_bot_b = le(3, 2,  1, 0, 0, sx)
    e_bot_l = le(0, 3,  0, 1, 0, sy)
    e_top_f = le(4, 5,  1, 0, 0, sx)
    e_top_r = le(5, 6,  0, 1, 0, sy)
    e_top_b = le(7, 6,  1, 0, 0, sx)
    e_top_l = le(4, 7,  0, 1, 0, sy)
    e_v0    = le(0, 4,  0, 0, 1, sz)
    e_v1    = le(1, 5,  0, 0, 1, sz)
    e_v2    = le(2, 6,  0, 0, 1, sz)
    e_v3    = le(3, 7,  0, 0, 1, sz)

    def mk_plane(px, py, pz, zx, zy, zz, xx, xy, xz):
        orig = f.cartesian_point((px, py, pz))
        zd = f.direction((zx, zy, zz)); xd = f.direction((xx, xy, xz))
        return f.plane(f.axis2_placement_3d(orig, zd, xd))

    def face4(edges_with_ori, plane):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
        return f.advanced_face([f.face_outer_bound(loop)], plane)

    pl_bot = mk_plane(ox,    oy,    oz,    0, 0,-1, 1, 0, 0)
    pl_top = mk_plane(ox,    oy,    oz+sz, 0, 0, 1, 1, 0, 0)
    pl_frt = mk_plane(ox,    oy,    oz,    0,-1, 0, 1, 0, 0)
    pl_bck = mk_plane(ox,    oy+sy, oz,    0, 1, 0, 1, 0, 0)
    pl_lft = mk_plane(ox,    oy,    oz,   -1, 0, 0, 0, 1, 0)
    pl_rgt = mk_plane(ox+sx, oy,    oz,    1, 0, 0, 0, 1, 0)

    f_bot = face4([(e_bot_f,True),(e_bot_r,True),(e_bot_b,False),(e_bot_l,False)], pl_bot)
    f_top = face4([(e_top_f,True),(e_top_r,True),(e_top_b,False),(e_top_l,False)], pl_top)
    f_frt = face4([(e_bot_f,True),(e_v1,True),(e_top_f,False),(e_v0,False)],       pl_frt)
    f_bck = face4([(e_bot_b,True),(e_v2,True),(e_top_b,False),(e_v3,False)],       pl_bck)
    f_lft = face4([(e_bot_l,True),(e_v3,True),(e_top_l,False),(e_v0,False)],       pl_lft)
    f_rgt = face4([(e_bot_r,True),(e_v2,True),(e_top_r,False),(e_v1,False)],       pl_rgt)

    return f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name=tag)


# Shell A: 10x10x10 box at x in [0,10].
shell_a = make_box_closed_shell(0.0, 0.0, 0.0, 10.0, 10.0, 10.0, "tsh237_a")

# Shell B: 10x10x10 box at x in [30,40] — genuinely disjoint bounding box from A.
shell_b = make_box_closed_shell(30.0, 0.0, 0.0, 10.0, 10.0, 10.0, "tsh237_b")

# UNSTRUCTURED shell soup: both shells listed directly in one
# SHELL_BASED_SURFACE_MODEL. No BREP_WITH_VOIDS, no MANIFOLD_SOLID_BREP.
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm, mode="surface_shape")
