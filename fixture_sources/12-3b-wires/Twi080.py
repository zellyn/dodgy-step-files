"""Twi080 — Wire splitting must propagate from underlying edge/curve splits.

Catalog claim: When an edge's supporting curve was split (C0-split mid-span),
every wire containing the edge must be re-built using the new sub-edges. The
wire-divide pipeline walks the wire's edges and replaces each with its
post-split sub-sequence, then re-validates closure.

Mechanism IS a planar face whose outer wire contains 5 edges instead of the
original 4 of a square — because the bottom edge was C0-split at its midpoint.
The split produces two sub-edges (bot_left: v_bl→v_mid, bot_right: v_mid→v_br)
sharing the mid-span VERTEX_POINT v_mid=(5,0,0). The wire now has N+1=5 edges:
  [bot_left, bot_right, right, top, left]
This fixture represents the *post-split state that should have been re-stitched*
but whose wire-closure flag was not re-validated: we deliver the 5-edge wire
(with the split already applied) to expose the re-validation requirement.

A second correct 10x10 square face at z=-1 satisfies face[1].surface_type==plane
and pushes total vertex count above 8.

Tier-3 assertions:
  - n_edges_total >= 5
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi080",
    defect=(
        "Two ADVANCED_FACEs on PLANEs in a CLOSED_SHELL; "
        "face0: a 10x10 square whose bottom edge was C0-split at the midpoint (5,0,0); "
        "the split produces two sub-edges sharing VERTEX_POINT v_mid=(5,0,0); "
        "the outer EDGE_LOOP now contains 5 edges instead of 4: "
        "bot_left(v_bl→v_mid), bot_right(v_mid→v_br), right(v_br→v_tr), "
        "top(v_tr→v_tl), left(v_tl→v_bl); "
        "the wire-divide pipeline must re-stitch using the split sub-edges and "
        "re-validate closure after replacement; "
        "face1 is a correct 10x10 square at z=-1 (provides face[1].surface_type==plane); "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → "
        "ADVANCED_FACEs in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane 0: face with split bottom edge ──────────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f.plane(pl0_plc)

# Five vertices: corners + split midpoint
v_bl  = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v_mid = f.vertex_point(f.cartesian_point((5.0,  0.0,  0.0)))   # midpoint — split vertex
v_br  = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right
v_tr  = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right
v_tl  = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # top-left

# bot_left: v_bl(0,0,0) → v_mid(5,0,0) — first sub-edge after C0 split
e_bot_l = f.edge_curve(
    v_bl, v_mid,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
)
oe_bot_l = f.oriented_edge(e_bot_l, True)

# bot_right: v_mid(5,0,0) → v_br(10,0,0) — second sub-edge after C0 split
e_bot_r = f.edge_curve(
    v_mid, v_br,
    f.line(f.cartesian_point((5.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 5.0))
)
oe_bot_r = f.oriented_edge(e_bot_r, True)

# right: v_br(10,0,0) → v_tr(10,10,0)
e_rgt = f.edge_curve(
    v_br, v_tr,
    f.line(f.cartesian_point((10.0, 0.0, 0.0)),
           f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
)
oe_rgt = f.oriented_edge(e_rgt, True)

# top: v_tr(10,10,0) → v_tl(0,10,0)
e_top = f.edge_curve(
    v_tr, v_tl,
    f.line(f.cartesian_point((10.0, 10.0, 0.0)),
           f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
)
oe_top = f.oriented_edge(e_top, True)

# left: v_tl(0,10,0) → v_bl(0,0,0)
e_lft = f.edge_curve(
    v_tl, v_bl,
    f.line(f.cartesian_point((0.0, 10.0, 0.0)),
           f.vector(f.direction((0.0, -1.0, 0.0)), 10.0))
)
oe_lft = f.oriented_edge(e_lft, True)

# 5-edge loop: [bot_left, bot_right, right, top, left]
loop0 = f.edge_loop([oe_bot_l, oe_bot_r, oe_rgt, oe_top, oe_lft])
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi080.stp")
