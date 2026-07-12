"""Tsh238 — Compound of a normal solid + a volume-threshold sliver solid,
reached via the STEP.exec.op `dropsmallsolids` operator context.

Catalog claim (occt-coverage GAP `seq-drop-small-solids`, volume-threshold
subvariant): `dropsmallsolids` (ShapeProcess_OperLibrary.cxx:594-635,
backed by ShapeFix_FixSmallSolid) is an "available-but-not-default"
STEP.exec.op healing operator: it is NOT invoked by OCCT's default
STEPControl_Reader.TransferRoots() transfer, only when a caller explicitly
opts into the ShapeProcess operator sequence with `dropsmallsolids` named in
it. This fixture provides the static compound-of-solids precondition the
operator acts on: a normal 8x8x8 box (volume 512) plus an isolated
8x8x0.04 slab sliver (volume 2.56 = 0.5% of the normal solid's volume,
below ShapeFix_FixSmallSolid's default volume-ratio threshold), genuinely
disjoint from the normal solid (no neighbor to merge into — Remove
disposition when `dropsmallsolids` is invoked with MergeSolids off).

Geometry family shares the Tsh234/Tsh235 sliver-solid pattern (same
occt-coverage GAP-item lineage) but is a genuinely distinct fixture at the
byte level (different dimensions/positions) and documents the operator
linkage explicitly, mirroring the N146-N153 "scaffold" convention: the
default STEPControl_Reader path (occt_heal_on/occt_heal_off oracles) sees
only a plain compound-of-2-solids with no small-solid healing applied,
because that healing requires the opt-in `dropsmallsolids` operator to run
post-transfer — not the default translation path.

Byte assertions:
  - count_entity_def(b'MANIFOLD_SOLID_BREP') == 2
  - count_entity_def(b'CLOSED_SHELL') == 2

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 12
  - face[0].surface_type == "plane"

Fixture kind: scaffold (operator-test-pair: shape provides the
compound-of-solids precondition; `dropsmallsolids` operator invocation
required post-transfer to reproduce the Remove/Merge healing decision)

live oracle (computed via validate2.py against this worktree's bytes,
default transfer path — NOT the dropsmallsolids-invoked path):
  occt=shape(1)/shape(1) gmsh=shape(54)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh238",
    defect=(
        "Compound of two genuine MANIFOLD_SOLID_BREP solids in one "
        "ADVANCED_BREP_SHAPE_REPRESENTATION: solid A is an 8x8x8 box "
        "(volume 512) at x in [0,8]; solid B is an 8x8x0.04 slab sliver "
        "(volume 2.56, 0.5% of A) at x in [40,48] — isolated, no adjacent "
        "neighbor. Static precondition for the opt-in `dropsmallsolids` "
        "STEP.exec.op operator (ShapeProcess_OperLibrary.cxx:594-635, "
        "ShapeFix_FixSmallSolid); default transfer applies no small-solid "
        "healing to this compound"
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


# Solid A: normal 8x8x8 box, volume 512.
solid_a = make_box_solid(0.0, 0.0, 0.0, 8.0, 8.0, 8.0, "tsh238_normal")

# Solid B: sliver slab 8x8x0.04, volume 2.56 = 0.5% of solid A's volume.
# Placed at x in [40,48] — isolated, disjoint bounding box from solid A.
solid_b = make_box_solid(40.0, 0.0, 0.0, 8.0, 8.0, 0.04, "tsh238_sliver")

# Genuine compound: ONE ADVANCED_BREP_SHAPE_REPRESENTATION with TWO items.
f.add_product_chain([solid_a, solid_b], mode="brep_shape")
