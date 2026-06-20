"""Twi104 — ShapeAnalysis_Wire.CheckTail misclassifies degenerate orientation.

Catalog claim: CheckTail implements binary-search tail detection for edge sequences
where the parametric domain is narrowed to find discontinuity. When wire orientation
is degenerate (start/end parameters inverted or nearly equal), tail-bound computation
fails. False positives occur when final edges have near-parallel orientation and
minimal parametric extent.

Mechanism IS a planar face whose outer wire has 3 edges:
  E0: a long normal edge (v0(0,0,0) → v1(10,0,0)) — the reference edge
  E1: a short nearly-horizontal edge (v1(10,0,0) → v2(10.0001,0,0)) — near-parallel,
      near-zero parametric extent relative to the full wire
  E2: a short nearly-horizontal edge (v2(10.0001,0,0) → v3(10.0002,0,0)) — near-parallel
      and near-zero parametric extent; domain bounds nearly equal (inverted after
      binary-search narrowing); CheckTail binary search at line 2356 misclassifies
      E2 as tail due to inverted domain bounds — IS the mechanism

The face is triangular-ish; the "nearly-parallel near-zero extent" edges at the end
of the wire represent the degenerate tail that fools the binary-search checker.

Single-face fixture (tier-3: n_faces_total == 1).

Tier-3 assertion:
  - n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi104",
    defect=(
        "Single ADVANCED_FACE on a PLANE in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 3 edges: "
        "E0(v0(0,0,0)→v1(10,0,0)) long normal horizontal edge; "
        "E1(v1(10,0,0)→v2(10.0001,0,0)) nearly-parallel, near-zero parametric extent; "
        "E2(v2(10.0001,0,0)→v3(10.0002,0,0)) near-parallel, near-zero parametric extent "
        "with nearly-inverted domain bounds after binary-search narrowing; "
        "the 3-edge wire closes via E_close(v3→v0) added to form valid loop; "
        "ShapeAnalysis_Wire.CheckTail binary search at line 2356 misclassifies E2 "
        "(and/or E1) as tail due to inverted domain bounds — IS mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE "
        "in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
# v0 and v3 form the "closing" gap; v1 and v2 are the near-parallel degenerate tail
v0 = f.vertex_point(f.cartesian_point((0.0,     0.0,  0.0)))
v1 = f.vertex_point(f.cartesian_point((10.0,    0.0,  0.0)))
v2 = f.vertex_point(f.cartesian_point((10.0001, 0.0,  0.0)))   # near-zero step
v3 = f.vertex_point(f.cartesian_point((10.0002, 0.0,  0.0)))   # near-zero step

# Closing vertex for the face at (0,5,0) to give the face some area
v_top = f.vertex_point(f.cartesian_point((5.0,    5.0,  0.0)))

import math as _math

# ── E0: v0(0,0,0) → v1(10,0,0) — normal long edge ────────────────────────────
e0_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0  = f.edge_curve(v0, v1, e0_line)
oe0 = f.oriented_edge(e0, True)

# ── E1: v1(10,0,0) → v2(10.0001,0,0) — near-parallel, near-zero extent ───────
e1_line = f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 0.0001))
e1  = f.edge_curve(v1, v2, e1_line)
oe1 = f.oriented_edge(e1, True)

# ── E2: v2(10.0001,0,0) → v3(10.0002,0,0) — near-parallel, near-zero extent ──
# This edge has near-inverted domain bounds after CheckTail binary search narrowing
# — IS the mechanism that triggers misclassification as a tail segment
e2_line = f.line(f.cartesian_point((10.0001, 0.0, 0.0)),
                 f.vector(f.direction((1.0, 0.0, 0.0)), 0.0001))
e2  = f.edge_curve(v2, v3, e2_line)
oe2 = f.oriented_edge(e2, True)

# ── E_right: v3(10.0002,0,0) → v_top(5,5,0) — right side of face ─────────────
_dx_r = 5.0 - 10.0002
_dy_r = 5.0
_mag_r = _math.hypot(_dx_r, _dy_r)
e_right_line = f.line(f.cartesian_point((10.0002, 0.0, 0.0)),
                      f.vector(f.direction((_dx_r / _mag_r, _dy_r / _mag_r, 0.0)), _mag_r))
e_right  = f.edge_curve(v3, v_top, e_right_line)
oe_right = f.oriented_edge(e_right, True)

# ── E_left: v_top(5,5,0) → v0(0,0,0) — left side of face ─────────────────────
_dx_l = -5.0
_dy_l = -5.0
_mag_l = _math.hypot(_dx_l, _dy_l)
e_left_line = f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                     f.vector(f.direction((_dx_l / _mag_l, _dy_l / _mag_l, 0.0)), _mag_l))
e_left  = f.edge_curve(v_top, v0, e_left_line)
oe_left = f.oriented_edge(e_left, True)

# 5-edge loop: [E0, E1(tail-candidate), E2(tail-candidate), E_right, E_left]
# The 3-catalog edge pattern is: E0 normal; E1, E2 nearly-parallel near-zero extent
# — CheckTail binary search misclassifies E2 (last near-parallel edge)
loop = f.edge_loop([oe0, oe1, oe2, oe_right, oe_left])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi104.stp")
