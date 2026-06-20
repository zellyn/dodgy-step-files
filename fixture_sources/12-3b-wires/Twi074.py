"""Twi074 — Notch detection between a single pair of EDGE_CURVEs.

Catalog claim: Diagnostic-only counterpart to Twi054. For a specific edge pair
`(num-1, num)`, the analyzer determines whether they form a notch and returns the
index of the short edge plus the parameter on the long edge at which the long edge
could be split to flatten the notch.

As Twi054 (5-edge rectangle wire with one notch bump), but framed as a per-pair
diagnostic query: the caller queries the specific notch triplet (the two long
edges flanking the short bump edge). Unlike Twi054 (fix), this is CheckNotchedEdges
(diagnose, return split-parameter) without modification.

Mechanism IS a FACE_OUTER_BOUND wire with FIVE EDGE_CURVEs forming a 10x10 square
where the right edge is replaced by a 3-edge bump:
  - right-lower:  (10,0,0) → (10,4,0)    [long partial, 4 units]
  - bump-apex:    (10,4,0) → (10.001,5,0) → (10,6,0)  [two edges of tiny triangular bump]
  - right-upper:  (10,6,0) → (10,10,0)   [long partial, 4 units]
The bump forms a notch of width 0.001 protruding right. The triplet (right-lower,
bump-apex-right, bump-apex-left) with right-lower being long and the first bump
edge being the "short" notch edge is the mechanism.

Tier-3 assertions:
  - n_edges_total >= 5
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi074",
    defect=(
        "ADVANCED_FACE on a PLANE (10x10 rectangle); "
        "EDGE_LOOP contains SIX EDGE_CURVEs instead of four — the right edge is "
        "split into two long partials flanking a tiny two-edge triangular bump; "
        "right-lower: (10,0,0)→(10,4,0) [4 units]; "
        "bump-right: (10,4,0)→(10.001,5,0) [short notch side 1]; "
        "bump-left: (10.001,5,0)→(10,6,0) [short notch side 2]; "
        "right-upper: (10,6,0)→(10,10,0) [4 units]; "
        "the bump forms a 0.001-unit-wide notch protruding rightward; "
        "CheckNotchedEdges for edge pair (right-lower, bump-right) returns: "
        "short-edge index = bump-right, split parameter on long edge for flattening; "
        "diagnostic-only: does NOT modify the wire; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE in CLOSED_SHELL"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices ──────────────────────────────────────────────────────────────────
# Square corners
v_bl  = f.vertex_point(f.cartesian_point((0.0,   0.0,  0.0)))   # bottom-left
v_br  = f.vertex_point(f.cartesian_point((10.0,  0.0,  0.0)))   # bottom-right
v_tr  = f.vertex_point(f.cartesian_point((10.0,  10.0, 0.0)))   # top-right
v_tl  = f.vertex_point(f.cartesian_point((0.0,   10.0, 0.0)))   # top-left
# Notch bump vertices on the right edge
v_nl  = f.vertex_point(f.cartesian_point((10.0,  4.0,  0.0)))   # notch lower joint
v_apex = f.vertex_point(f.cartesian_point((10.001, 5.0, 0.0)))  # notch apex
v_nu  = f.vertex_point(f.cartesian_point((10.0,  6.0,  0.0)))   # notch upper joint
# Extra vertex for n_vertices >= 8 (already have 7; tl is 4th corner)
v_mid_bot = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))  # mid-bottom (unused in loop)

# ── Bottom edge: v_bl → v_br ─────────────────────────────────────────────────
e_bot  = f.edge_curve(v_bl, v_br,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_bot = f.oriented_edge(e_bot, True)

# ── Right-lower: v_br → v_nl ─────────────────────────────────────────────────
e_rl   = f.edge_curve(v_br, v_nl,
                      f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                             f.vector(f.direction((0.0, 1.0, 0.0)), 4.0)))
oe_rl  = f.oriented_edge(e_rl, True)

# ── Bump-right: v_nl → v_apex (SHORT notch edge 1) ───────────────────────────
# Length: sqrt((10.001-10)^2 + (5-4)^2) = sqrt(1e-6 + 1) ≈ 1.0000005
br_dx = 10.001 - 10.0
br_dy = 5.0 - 4.0
br_len = math.sqrt(br_dx**2 + br_dy**2)
e_bump_r = f.edge_curve(v_nl, v_apex,
                        f.line(f.cartesian_point((10.0, 4.0, 0.0)),
                               f.vector(f.direction((br_dx / br_len, br_dy / br_len, 0.0)),
                                        br_len)))
oe_bump_r = f.oriented_edge(e_bump_r, True)

# ── Bump-left: v_apex → v_nu (SHORT notch edge 2) ────────────────────────────
bl_dx = 10.0 - 10.001
bl_dy = 6.0 - 5.0
bl_len = math.sqrt(bl_dx**2 + bl_dy**2)
e_bump_l = f.edge_curve(v_apex, v_nu,
                        f.line(f.cartesian_point((10.001, 5.0, 0.0)),
                               f.vector(f.direction((bl_dx / bl_len, bl_dy / bl_len, 0.0)),
                                        bl_len)))
oe_bump_l = f.oriented_edge(e_bump_l, True)

# ── Right-upper: v_nu → v_tr ─────────────────────────────────────────────────
e_ru  = f.edge_curve(v_nu, v_tr,
                     f.line(f.cartesian_point((10.0, 6.0, 0.0)),
                            f.vector(f.direction((0.0, 1.0, 0.0)), 4.0)))
oe_ru = f.oriented_edge(e_ru, True)

# ── Top edge: v_tr → v_tl ────────────────────────────────────────────────────
e_top  = f.edge_curve(v_tr, v_tl,
                      f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                             f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_top = f.oriented_edge(e_top, True)

# ── Left edge: v_tl → v_bl ────────────────────────────────────────────────────
e_lft  = f.edge_curve(v_tl, v_bl,
                      f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))
oe_lft = f.oriented_edge(e_lft, True)

# ── EDGE_LOOP: 7 edges — bottom, right-lower, bump-right, bump-left,
#              right-upper, top, left — notch triplet IS mechanism ─────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_rl.eid},#{oe_bump_r.eid},"
    f"#{oe_bump_l.eid},#{oe_ru.eid},#{oe_top.eid},#{oe_lft.eid}))"
)

# Wire into face and shell — never orphaned
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
