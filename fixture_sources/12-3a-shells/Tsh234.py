"""Tsh234 — Compound of a normal solid + a sliver solid at 0.5% of its volume.

Catalog claim (occt-coverage GAP `tkshh-sliver-solid`): a compound contains a
normal solid alongside a tiny sliver solid whose volume is a small fraction of
the normal solid's volume — below the volume threshold OCCT's
ShapeFix_FixSmallSolid healer uses to decide whether a solid is "small" debris
(e.g. Boolean residue) that should be dropped or merged. This fixture provides
the isolated (non-touching) case: the sliver has no neighbor solid to merge
into, so a correct healer must choose the "drop" disposition, not "merge".

Mechanism IS the shell/solid topology: two genuine MANIFOLD_SOLID_BREP solids
(each with a real watertight 6-face CLOSED_SHELL, not a bare face) sit in one
compound SHAPE_REPRESENTATION (a single ADVANCED_BREP_SHAPE_REPRESENTATION
with two items). Solid A is a 10x10x10 box (volume 1000 mm^3). Solid B is a
10x10x0.05 slab (volume 5 mm^3 = 0.5% of solid A's volume) placed far away
(disjoint bounding box) from solid A — genuinely isolated, not adjacent.

Byte assertions:
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 2
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 12
  - face[0].surface_type == "plane"

live oracle (computed via validate2.py against this worktree's bytes):
  occt=shape(1)/shape(1) gmsh=shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh234",
    defect=(
        "Compound of two genuine MANIFOLD_SOLID_BREP solids in one "
        "ADVANCED_BREP_SHAPE_REPRESENTATION: solid A is a 10x10x10 box "
        "(volume 1000), solid B is a 10x10x0.05 slab (volume 5, 0.5% of A), "
        "placed with a disjoint bounding box (isolated, not adjacent). "
        "Below ShapeFix_FixSmallSolid's volume threshold; a correct healer "
        "must drop the isolated sliver, not merge it (no neighbor to merge into)"
    ),
)


def make_box_solid(ox, oy, oz, sx, sy, sz, tag):
    """Build a watertight MANIFOLD_SOLID_BREP box at origin (ox,oy,oz), size (sx,sy,sz)."""
    pts = [
        f.cartesian_point((ox,    oy,    oz   )),  # 0
        f.cartesian_point((ox+sx, oy,    oz   )),  # 1
        f.cartesian_point((ox+sx, oy+sy, oz   )),  # 2
        f.cartesian_point((ox,    oy+sy, oz   )),  # 3
        f.cartesian_point((ox,    oy,    oz+sz)),  # 4
        f.cartesian_point((ox+sx, oy,    oz+sz)),  # 5
        f.cartesian_point((ox+sx, oy+sy, oz+sz)),  # 6
        f.cartesian_point((ox,    oy+sy, oz+sz)),  # 7
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

    shell = f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name=tag)
    return f._emit_raw(f"MANIFOLD_SOLID_BREP('{tag}',#{shell.eid})")


# Solid A: normal 10x10x10 box, volume 1000.
solid_a = make_box_solid(0.0, 0.0, 0.0, 10.0, 10.0, 10.0, "tsh234_normal")

# Solid B: sliver slab 10x10x0.05, volume 5 = 0.5% of solid A's volume.
# Placed at x in [50, 60] — bounding box disjoint from solid A (isolated).
solid_b = make_box_solid(50.0, 0.0, 0.0, 10.0, 10.0, 0.05, "tsh234_sliver")

# Genuine compound: ONE ADVANCED_BREP_SHAPE_REPRESENTATION with TWO items.
f.add_product_chain([solid_a, solid_b], mode="brep_shape")
