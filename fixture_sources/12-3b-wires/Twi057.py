"""Twi057 — Two edges of one face are confused along their full length (strip pair).

Catalog claim: Two long edges of a wire are within tolerance distance of each
other along the full parameter range of both. The pair-of-edges check is purely
about whether two edges describe approximately the same curve.

Mechanism IS a wire with two parallel edges from (0,0,0)→(100,0,0) and
(0,1e-6,0)→(100,1e-6,0); the gap is 1e-6 over a 100-unit length. The wire
completes a closed shape (a very thin strip) using two short closing edges
at each end. Both long edges ARE parallel and within tolerance; the strip gap
of 1e-6 is the mechanism. All EDGE_CURVEs ARE wired into an EDGE_LOOP →
FACE_OUTER_BOUND → ADVANCED_FACE in a CLOSED_SHELL — never orphaned.

Tier-3 assertions:
  - n_edges_total >= 1
  - face[0].surface_type == "plane"
  - n_vertices_total >= 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi057",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP contains four EDGE_CURVEs forming a closed strip: "
        "edge1 (bottom-long): (0,0,0)→(100,0,0); "
        "edge2 (right-close): (100,0,0)→(100,1e-6,0); "
        "edge3 (top-long): (100,1e-6,0)→(0,1e-6,0); "
        "edge4 (left-close): (0,1e-6,0)→(0,0,0); "
        "edge1 and edge3 are parallel, 1e-6 apart over 100-unit length — "
        "they form a strip pair: both describe approximately the same line; "
        "the 1e-6 gap over 100-unit length IS the mechanism (strip-pair defect); "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel must detect strip-pair and report or merge the confusable edge pair"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices: thin strip, gap = 1e-6 over length 100 ─────────────────────────
GAP = 1.0e-6
LEN = 100.0

v_bl = f.vertex_point(f.cartesian_point((0.0,   0.0,   0.0)))    # bottom-left
v_br = f.vertex_point(f.cartesian_point((LEN,   0.0,   0.0)))    # bottom-right
v_tr = f.vertex_point(f.cartesian_point((LEN,   GAP,   0.0)))    # top-right (1e-6 up)
v_tl = f.vertex_point(f.cartesian_point((0.0,   GAP,   0.0)))    # top-left  (1e-6 up)

# ── Bottom-long edge: v_bl → v_br  (STRIP edge 1) ─────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), LEN)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right-close edge: v_br → v_tr  (tiny short closing edge) ──────────────────
import math
e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((LEN, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), GAP)))
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top-long edge: v_tr → v_tl  (STRIP edge 2 — parallel to bottom, 1e-6 apart) ─
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((LEN, GAP, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), LEN)))
oe_top = f.oriented_edge(e_top, True)

# ── Left-close edge: v_tl → v_bl  (tiny short closing edge) ──────────────────
e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, GAP, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), GAP)))
oe_lft = f.oriented_edge(e_lft, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
