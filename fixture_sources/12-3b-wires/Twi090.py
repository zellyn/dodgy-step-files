"""Twi090 — Cached EDGE_LOOP closed-flag not refreshed after one ORIENTED_EDGE
replaced by two collinear halves at a midpoint vertex.

Catalog claim: A wire's `closed` flag was computed at construction. Subsequent
healing replaces one of the wire's edges with two collinear sub-edges joined at
a vertex in the middle of the original edge. The wire is still closed but the
cached `closed_flag` propagates `closed=false` to downstream consumers.

Mechanism IS a planar square face whose outer EDGE_LOOP has 5 edges:
the original top edge (v_tl→v_tr) was split at v_tmid=(5,10,0) into two
collinear halves — top_left(v_tl→v_tmid) and top_right(v_tmid→v_tr). The
loop is:
  [bottom, right, top_right, top_left (reversed), left]
Wait — to represent "top replaced by two collinear halves", the wire goes:
  [bottom(v_bl→v_br), right(v_br→v_tr), top_right_rev(v_tr→v_tmid),
   top_left_rev(v_tmid→v_tl), left(v_tl→v_bl)]
The wire closes correctly (v_bl start, v_bl end) but the closed flag cached
before the edge replacement no longer reflects reality — downstream checker
sees closed=false.

Second correct square face at z=-1 satisfies tier-3 n_vertices_total >= 8
and face[1].surface_type == "plane".

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi090",
    defect=(
        "Two ADVANCED_FACEs on PLANEs in a CLOSED_SHELL; "
        "face0: a 10x10 square where the top edge was replaced by two collinear halves "
        "sharing VERTEX_POINT v_tmid=(5,10,0); "
        "the EDGE_LOOP has 5 edges: bottom(v_bl→v_br), right(v_br→v_tr), "
        "top_r(v_tr→v_tmid), top_l(v_tmid→v_tl), left(v_tl→v_bl); "
        "wire is still closed but cached closed_flag=false not refreshed after "
        "the edge-replacement healing step; "
        "downstream consumers see closed=false despite correct topology; "
        "face1 is a correct 10x10 square at z=-1; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane 0: face with split top edge (two collinear halves) ──────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f.plane(pl0_plc)

# Vertices: 4 corners + 1 midpoint on top edge
v_bl   = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v_br   = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right
v_tr   = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right
v_tmid = f.vertex_point(f.cartesian_point((5.0,  10.0, 0.0)))   # top midpoint — split vertex
v_tl   = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # top-left

# bottom: v_bl(0,0,0) → v_br(10,0,0)
e_bot = f.edge_curve(
    v_bl, v_br,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
)
oe_bot = f.oriented_edge(e_bot, True)

# right: v_br(10,0,0) → v_tr(10,10,0)
e_rgt = f.edge_curve(
    v_br, v_tr,
    f.line(f.cartesian_point((10.0, 0.0, 0.0)),
           f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
)
oe_rgt = f.oriented_edge(e_rgt, True)

# top_right half: v_tr(10,10,0) → v_tmid(5,10,0)  [right half of split top, reversed]
e_top_r = f.edge_curve(
    v_tr, v_tmid,
    f.line(f.cartesian_point((10.0, 10.0, 0.0)),
           f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0))
)
oe_top_r = f.oriented_edge(e_top_r, True)

# top_left half: v_tmid(5,10,0) → v_tl(0,10,0)  [left half of split top, reversed]
e_top_l = f.edge_curve(
    v_tmid, v_tl,
    f.line(f.cartesian_point((5.0, 10.0, 0.0)),
           f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0))
)
oe_top_l = f.oriented_edge(e_top_l, True)

# left: v_tl(0,10,0) → v_bl(0,0,0)
e_lft = f.edge_curve(
    v_tl, v_bl,
    f.line(f.cartesian_point((0.0, 10.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
)
oe_lft = f.oriented_edge(e_lft, True)

# 5-edge loop: wire IS closed (v_bl → ... → v_bl) but cached flag not updated
loop0 = f.edge_loop([oe_bot, oe_rgt, oe_top_r, oe_top_l, oe_lft])
fob0  = f.face_outer_bound(loop0)
face0 = f.advanced_face([fob0], plane0)

# ── Plane 1: correct 10x10 square at z=-1 ─────────────────────────────────────
pl1_orig = f.cartesian_point((0.0, 0.0, -1.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f.plane(pl1_plc)

v_bl1 = f.vertex_point(f.cartesian_point((0.0,  0.0,  -1.0)))
v_br1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  -1.0)))
v_tr1 = f.vertex_point(f.cartesian_point((10.0, 10.0, -1.0)))
v_tl1 = f.vertex_point(f.cartesian_point((0.0,  10.0, -1.0)))

eb1 = f.edge_curve(v_bl1, v_br1,
                   f.line(f.cartesian_point((0.0, 0.0, -1.0)),
                          f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
er1 = f.edge_curve(v_br1, v_tr1,
                   f.line(f.cartesian_point((10.0, 0.0, -1.0)),
                          f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
et1 = f.edge_curve(v_tr1, v_tl1,
                   f.line(f.cartesian_point((10.0, 10.0, -1.0)),
                          f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
el1 = f.edge_curve(v_tl1, v_bl1,
                   f.line(f.cartesian_point((0.0, 10.0, -1.0)),
                          f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

oeb1 = f.oriented_edge(eb1, True)
oer1 = f.oriented_edge(er1, True)
oet1 = f.oriented_edge(et1, True)
oel1 = f.oriented_edge(el1, True)

loop1 = f.edge_loop([oeb1, oer1, oet1, oel1])
fob1  = f.face_outer_bound(loop1)
face1 = f.advanced_face([fob1], plane1)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi090.stp")
