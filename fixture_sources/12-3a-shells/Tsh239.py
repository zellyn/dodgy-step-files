"""Tsh239 — Compound of a normal solid + a width-factor sliver solid adjacent
to it, reached via the STEP.exec.op `dropsmallsolids` operator context.

Catalog claim (occt-coverage GAP `seq-drop-small-solids`, width-factor +
remove-vs-merge-disposition subvariants): the adjacent-neighbor sibling of
Tsh238. `dropsmallsolids` (ShapeProcess_OperLibrary.cxx:594-635,
ShapeFix_FixSmallSolid) chooses Remove vs Merge disposition via its
MergeSolids flag; that choice is only meaningful when the small solid has a
real neighbor to merge into. This fixture supplies a normal 8x8x8 box
(volume 512) plus an 8x0.015x0.015 needle sliver (volume 0.0018,
width-factor vol/half-area ~= 0.00749mm) whose bounding box is flush-adjacent
to the normal solid's x=8 face — a genuine Merge-disposition precondition,
distinct from Tsh238's isolated Remove-disposition precondition.

Geometry family shares the Tsh234/Tsh235/Tsh238 sliver-solid lineage but is
byte-distinct (different dimensions/positions). Like Tsh238, this is a
scaffold fixture: the `dropsmallsolids` operator is available-but-not-default
(ShapeProcess_OperLibrary), so the default STEPControl_Reader transfer path
this corpus's oracles exercise sees only the plain compound, with no
small-solid healing applied.

Byte assertions:
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 2
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 12
  - face[0].surface_type == "plane"

Fixture kind: scaffold (operator-test-pair: shape provides the
adjacent-compound precondition; `dropsmallsolids` operator invocation with
MergeSolids on required post-transfer to reproduce the Merge-disposition
healing decision)

live oracle (computed via validate2.py against this worktree's bytes,
default transfer path — NOT the dropsmallsolids-invoked path):
  occt=shape(1)/shape(1) gmsh=shape(54)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh239",
    defect=(
        "Compound of two genuine MANIFOLD_SOLID_BREP solids in one "
        "ADVANCED_BREP_SHAPE_REPRESENTATION: solid A is an 8x8x8 box "
        "(volume 512) at x in [0,8]; solid B is an 8x0.015x0.015 needle "
        "sliver (volume 0.0018, width-factor vol/half-area ~= 0.00749mm) "
        "at x in [8,16], flush-adjacent to solid A's x=8 face. Static "
        "precondition for the opt-in `dropsmallsolids` STEP.exec.op "
        "operator's Merge disposition (MergeSolids flag) — distinct from "
        "Tsh238's isolated Remove-disposition precondition"
    ),
)


def make_box_solid(ox, oy, oz, sx, sy, sz, tag):
    """Build a watertight MANIFOLD_SOLID_BREP box at origin (ox,oy,oz), size (sx,sy,sz)."""
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

    shell = f.closed_shell([f_bot, f_top, f_frt, f_bck, f_lft, f_rgt], name=tag)
    return f._emit_raw(f"MANIFOLD_SOLID_BREP('{tag}',#{shell.eid})")


# Solid A: normal 8x8x8 box, volume 512, x in [0,8].
solid_a = make_box_solid(0.0, 0.0, 0.0, 8.0, 8.0, 8.0, "tsh239_normal")

# Solid B: needle sliver 8x0.015x0.015, volume 0.0018, x in [8,16] —
# flush against solid A's x=8 face (adjacent, not isolated).
solid_b = make_box_solid(8.0, 3.9925, 3.9925, 8.0, 0.015, 0.015, "tsh239_needle")

# Genuine compound: ONE ADVANCED_BREP_SHAPE_REPRESENTATION with TWO items.
f.add_product_chain([solid_a, solid_b], mode="brep_shape")
