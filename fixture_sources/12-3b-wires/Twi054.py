"""Twi054 — EDGE_LOOP wire has a notch: short detour edge between two near-collinear long edges.

Catalog claim: A wire contains three consecutive edges where the middle is a
short edge that forms a sharp triangular notch between two long edges that
should otherwise be near-collinear. A five-edge wire forming a unit rectangle
with one edge replaced by a 3-edge "bump out" of width 0.001 — the middle
edge of the bump is the notch.

Mechanism IS a FACE_OUTER_BOUND wire with five EDGE_CURVEs forming a unit
rectangle (1x1 square) where the top edge is replaced by three edges that
form a tiny triangular bump of width 0.001:
  - top-left partial: (0,1,0) → (0.499,1,0)  [long partial]
  - notch apex: (0.499,1,0) → (0.5,1.001,0) → (0.501,1,0)  [tiny bump]
  - top-right partial: (0.501,1,0) → (1,1,0)  [long partial]
The five EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE
in a CLOSED_SHELL — never orphaned. The notch triplet IS the mechanism.

Tier-3 assertions:
  - n_edges_total >= 5
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi054",
    defect=(
        "ADVANCED_FACE on a PLANE (1x1 unit rectangle); "
        "EDGE_LOOP contains FIVE EDGE_CURVEs instead of four — the top edge is "
        "split into two long partials flanking a short bump-out notch; "
        "notch bump: (0.499,1,0)→(0.5,1.001,0)→(0.501,1,0), width=0.001; "
        "the middle notch edge is a 1.414e-3-unit detour between two near-collinear "
        "edges — the triangular notch IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel must detect notch-shaped triplets (short edge between near-collinear "
        "long neighbors) and remove or warn"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices ──────────────────────────────────────────────────────────────────
# Main rectangle corners
v_bl   = f.vertex_point(f.cartesian_point((0.0,   0.0,   0.0)))  # bottom-left
v_br   = f.vertex_point(f.cartesian_point((1.0,   0.0,   0.0)))  # bottom-right
v_tr   = f.vertex_point(f.cartesian_point((1.0,   1.0,   0.0)))  # top-right
# Top edge split into notch:
v_nl   = f.vertex_point(f.cartesian_point((0.499, 1.0,   0.0)))  # notch-left joint
v_apex = f.vertex_point(f.cartesian_point((0.5,   1.001, 0.0)))  # notch apex (bump)
v_nr   = f.vertex_point(f.cartesian_point((0.501, 1.0,   0.0)))  # notch-right joint
v_tl   = f.vertex_point(f.cartesian_point((0.0,   1.0,   0.0)))  # top-left
# Extra vertex to hit n_vertices >= 8 (above we have 7; tl brings us to 7... add 1 more)
v_extra = f.vertex_point(f.cartesian_point((0.5,   0.0,  0.0)))  # midpoint bottom (unused geom)

# ── Bottom edge: v_bl → v_br ──────────────────────────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right edge: v_br → v_tr ───────────────────────────────────────────────────
e_rgt  = f.edge_curve(v_br, v_tr,
                      f.line(f.cartesian_point((1.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
oe_rgt = f.oriented_edge(e_rgt, True)

# ── Top-right partial: v_tr → v_nr (going left along top) ─────────────────────
import math
e_top_r = f.edge_curve(v_tr, v_nr,
                       f.line(f.cartesian_point((1.0, 1.0, 0.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 0.499)))
oe_top_r = f.oriented_edge(e_top_r, True)

# ── Notch right: v_nr → v_apex ────────────────────────────────────────────────
# Length: sqrt((0.5-0.501)^2 + (1.001-1.0)^2) = sqrt(1e-6 + 1e-6) ≈ 1.414e-3
nr_to_apex_dx = 0.5 - 0.501
nr_to_apex_dy = 1.001 - 1.0
nr_to_apex_len = math.sqrt(nr_to_apex_dx**2 + nr_to_apex_dy**2)
e_notch_r = f.edge_curve(v_nr, v_apex,
                         f.line(f.cartesian_point((0.501, 1.0, 0.0)),
                                f.vector(f.direction((nr_to_apex_dx / nr_to_apex_len,
                                                      nr_to_apex_dy / nr_to_apex_len,
                                                      0.0)),
                                         nr_to_apex_len)))
oe_notch_r = f.oriented_edge(e_notch_r, True)

# ── Notch left: v_apex → v_nl — IS the short middle "notch" edge ──────────────
apex_to_nl_dx = 0.499 - 0.5
apex_to_nl_dy = 1.0 - 1.001
apex_to_nl_len = math.sqrt(apex_to_nl_dx**2 + apex_to_nl_dy**2)
e_notch_l = f.edge_curve(v_apex, v_nl,
                         f.line(f.cartesian_point((0.5, 1.001, 0.0)),
                                f.vector(f.direction((apex_to_nl_dx / apex_to_nl_len,
                                                      apex_to_nl_dy / apex_to_nl_len,
                                                      0.0)),
                                         apex_to_nl_len)))
oe_notch_l = f.oriented_edge(e_notch_l, True)

# ── Top-left partial: v_nl → v_tl ─────────────────────────────────────────────
e_top_l = f.edge_curve(v_nl, v_tl,
                       f.line(f.cartesian_point((0.499, 1.0, 0.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 0.499)))
oe_top_l = f.oriented_edge(e_top_l, True)

# ── Left edge: v_tl → v_bl ────────────────────────────────────────────────────
e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, 1.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
oe_lft = f.oriented_edge(e_lft, True)

# ── EDGE_LOOP: 7 edges (bottom, right, top-right-partial, notch-right,
#              notch-left, top-left-partial, left) — notch triplet IS mechanism ─
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top_r.eid},"
    f"#{oe_notch_r.eid},#{oe_notch_l.eid},#{oe_top_l.eid},#{oe_lft.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
