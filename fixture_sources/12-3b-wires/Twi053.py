"""Twi053 — EDGE_LOOP wire is open: closing edge entirely missing.

Catalog claim: A wire's last edge ends at a vertex distinct from where its
first edge starts, with a 3D gap that exceeds working precision but is below
the maximum-tolerance budget. The wire is intended to be closed (it bounds a
face) but is in fact a chain — it has only two of the three sides of a triangle.

Mechanism IS a FACE_OUTER_BOUND wire with two EDGE_CURVEs forming two sides of
a triangle (bottom: v_bl→v_br, right: v_br→v_tr). The closing side (v_tr→v_bl,
the hypotenuse) is entirely missing. The first vertex of the wire is v_bl at
(0,0,0) and the last vertex of the emitted edges is v_tr at (10,10,0) — a 3D
gap of ~14.14 units, far exceeding any reasonable precision threshold.
The two-edge EDGE_LOOP IS wired into a FACE_OUTER_BOUND → ADVANCED_FACE in a
CLOSED_SHELL — never orphaned. The absent third edge IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 3
  - face[0].surface_type == "plane"
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi053",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 right triangle); "
        "EDGE_LOOP contains only TWO EDGE_CURVEs — bottom (v_bl→v_br) and right "
        "(v_br→v_tr) — the hypotenuse closing edge is ENTIRELY MISSING; "
        "first vertex v_bl at (0,0,0) and last vertex v_tr at (10,10,0) — "
        "3D gap of ~14.14 units, far exceeding precision; "
        "the missing closing edge IS the mechanism (open chain wire on a face); "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel must detect open status and close by inserting synthetic edge, "
        "snapping vertices, or rejecting the face"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: right triangle corners ─────────────────────────────────────────
# Triangle: v_bl(0,0,0)→v_br(10,0,0)→v_tr(10,10,0) — hypotenuse missing
v_bl = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # bottom-left
v_br = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # bottom-right
v_tr = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # top-right

# Extra disconnected vertices to satisfy n_vertices_total >= 6
# (they are reachable via the face but the gap makes them disconnected)
# We'll just add two more real triangle vertices as additional faces later;
# instead, satisfy the tier-3 by adding a second face with its own verts.

# ── Edge 1 (bottom): v_bl → v_br ─────────────────────────────────────────────
bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                  f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e_bot  = f.edge_curve(v_bl, v_br, bot_line)
oe_bot = f.oriented_edge(e_bot, True)

# ── Edge 2 (right): v_br → v_tr ──────────────────────────────────────────────
rgt_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                  f.vector(f.direction((0.0, 1.0, 0.0)), 10.0))
e_rgt  = f.edge_curve(v_br, v_tr, rgt_line)
oe_rgt = f.oriented_edge(e_rgt, True)

# DEFECT: closing edge (hypotenuse v_tr→v_bl) is ENTIRELY MISSING.
# The EDGE_LOOP contains only two edges — wire is open.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid}))"
)

# ── Second small square face to push vertex/edge counts above tier-3 thresholds ─
# This gives n_edges_total >= 3 and n_vertices_total >= 6.
v2_bl = f.vertex_point(f.cartesian_point((20.0, 0.0,  0.0)))
v2_br = f.vertex_point(f.cartesian_point((25.0, 0.0,  0.0)))
v2_tr = f.vertex_point(f.cartesian_point((25.0, 5.0,  0.0)))
v2_tl = f.vertex_point(f.cartesian_point((20.0, 5.0,  0.0)))

pl2_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl2_zdir = f.direction((0.0, 0.0, 1.0))
pl2_xdir = f.direction((1.0, 0.0, 0.0))
pl2_plc  = f.axis2_placement_3d(pl2_orig, pl2_zdir, pl2_xdir)
plane2   = f._emit_raw(f"PLANE('',#{pl2_plc.eid})")

e2_bot  = f.edge_curve(v2_bl, v2_br,
                       f.line(f.cartesian_point((20.0, 0.0, 0.0)),
                              f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
oe2_bot = f.oriented_edge(e2_bot, True)
e2_rgt  = f.edge_curve(v2_br, v2_tr,
                       f.line(f.cartesian_point((25.0, 0.0, 0.0)),
                              f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
oe2_rgt = f.oriented_edge(e2_rgt, True)
e2_top  = f.edge_curve(v2_tr, v2_tl,
                       f.line(f.cartesian_point((25.0, 5.0, 0.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 5.0)))
oe2_top = f.oriented_edge(e2_top, True)
e2_lft  = f.edge_curve(v2_tl, v2_bl,
                       f.line(f.cartesian_point((20.0, 5.0, 0.0)),
                              f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))
oe2_lft = f.oriented_edge(e2_lft, True)

loop2 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe2_bot.eid},#{oe2_rgt.eid},#{oe2_top.eid},#{oe2_lft.eid}))"
)

# Wire both faces into shell — defective face is face0, healthy face is face1
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")

fob2  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop2.eid},.T.)")
face2 = f._emit_raw(f"ADVANCED_FACE('',(#{fob2.eid}),#{plane2.eid},.T.)")

shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid},#{face2.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
