"""Twi165 — ShapeAnalysis_Wire.CheckTail B-spline subdivided.

Catalog claim: Last edge is B-spline subdivided into multiple sub-curves;
CheckTail's tangent-discontinuity test fires on every sub-curve boundary.

Mechanism: A wire contains:
  - E0: straight LINE from P0=(0,0,0) to P1=(10,0,0) — the lead-in edge
  - E1: degree-3 B-spline sub-curve #1 from P1=(10,0,0) to P2=(14,3,0),
        with a C1 discontinuity at the junction P1 (tangent kink)
  - E2: degree-3 B-spline sub-curve #2 from P2=(14,3,0) to P3=(12,7,0),
        with a C1 discontinuity at P2 (tangent kink between sub-curves)
  - E3: degree-3 B-spline sub-curve #3 from P3=(12,7,0) back to P0=(0,0,0),
        with a C1 discontinuity at P3 (tangent kink between sub-curves)

The three B-spline edges E1, E2, E3 represent what would logically be a single
subdivided B-spline curve. Each junction (P1, P2, P3) has a tangent
discontinuity (C1 break). CheckTail processes the last edge of the wire
(E3) and tests for tangent continuity at its start/end. Without
knot-continuity awareness, CheckTail fires at every sub-curve junction
as a "tail failure" — it sees C1 breaks at P2 and P3 as tail defects
rather than recognising them as sub-curve boundaries of a single logical edge.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi165",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 edges: "
        "E0 LINE (0,0,0)→(10,0,0) — lead-in straight edge; "
        "E1 degree-3 B-spline (10,0,0)→(14,3,0) sub-curve #1 with C1 kink at start; "
        "E2 degree-3 B-spline (14,3,0)→(12,7,0) sub-curve #2 with C1 kink at junction; "
        "E3 degree-3 B-spline (12,7,0)→(0,0,0) sub-curve #3 with C1 kink at junction; "
        "E1/E2/E3 represent subdivided single logical curve; "
        "C1 tangent-discontinuity at every sub-curve boundary IS the defect; "
        "CheckTail without knot-continuity awareness fires at each junction "
        "as tail failure over-reporting defects IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
P0 = ( 0.0,  0.0, 0.0)   # wire start/close
P1 = (10.0,  0.0, 0.0)   # E0 end / E1 start
P2 = (14.0,  3.0, 0.0)   # E1 end / E2 start — C1 break here
P3 = (12.0,  7.0, 0.0)   # E2 end / E3 start — C1 break here

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))
v_P2 = f.vertex_point(f.cartesian_point(P2))
v_P3 = f.vertex_point(f.cartesian_point(P3))

# ── E0: straight LINE P0 → P1 ────────────────────────────────────────────────
e0_line = f.line(
    f.cartesian_point(P0),
    f.vector(f.direction((1.0, 0.0, 0.0)), 10.0),
)
e0  = f.edge_curve(v_P0, v_P1, e0_line, True)
oe0 = f.oriented_edge(e0, True)

# ── E1: B-spline sub-curve #1: P1=(10,0) → P2=(14,3) ─────────────────────────
# Degree-3, 4 control points → need 4+3+1=8 knots (clamped [4,4])
# Control points designed to give a C1 kink at P1 vs E0's +X tangent:
#   cp0=(10,0,0), cp1=(11,0,0), cp2=(13,2,0), cp3=(14,3,0)
# Tangent at start = direction cp1-cp0 = (1,0,0) — same as E0, so C0 continuity
# but C1 requires tangent magnitudes to match across the junction.
# To create C1 break at P1: make E1 start tangent direction ≠ E0 end tangent.
# E0 ends going +X; E1 starts going (+X, +Y) — tangent kink IS the defect.
cp0_e1 = f.cartesian_point((10.0, 0.0, 0.0))
cp1_e1 = f.cartesian_point((11.0, 2.0, 0.0))   # tangent kink vs E0's +X
cp2_e1 = f.cartesian_point((13.0, 2.5, 0.0))
cp3_e1 = f.cartesian_point((14.0, 3.0, 0.0))

bsp_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e1, cp1_e1, cp2_e1, cp3_e1],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
e1  = f.edge_curve(v_P1, v_P2, bsp_e1, True)
oe1 = f.oriented_edge(e1, True)

# ── E2: B-spline sub-curve #2: P2=(14,3) → P3=(12,7) ─────────────────────────
# C1 break at P2: E1 ends tangent direction ≈ (1,0.5) normalized;
#                 E2 starts tangent direction ≈ (-0.5,1) — perpendicular kink.
cp0_e2 = f.cartesian_point((14.0, 3.0, 0.0))
cp1_e2 = f.cartesian_point((14.0, 5.0, 0.0))   # tangent kink vs E1 end tangent
cp2_e2 = f.cartesian_point((13.0, 6.5, 0.0))
cp3_e2 = f.cartesian_point((12.0, 7.0, 0.0))

bsp_e2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e2, cp1_e2, cp2_e2, cp3_e2],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
e2  = f.edge_curve(v_P2, v_P3, bsp_e2, True)
oe2 = f.oriented_edge(e2, True)

# ── E3: B-spline sub-curve #3: P3=(12,7) → P0=(0,0) ─────────────────────────
# C1 break at P3: E2 ends going roughly (-1,0.5); E3 starts going (-1,-0.3).
# 5 control points for longer curve, degree 3: need 5+3+1=9 knots (clamped [4,1,4])
cp0_e3 = f.cartesian_point((12.0, 7.0, 0.0))
cp1_e3 = f.cartesian_point((10.0, 4.0, 0.0))   # tangent kink at P3
cp2_e3 = f.cartesian_point(( 7.0, 2.0, 0.0))
cp3_e3 = f.cartesian_point(( 3.0, 1.0, 0.0))
cp4_e3 = f.cartesian_point(( 0.0, 0.0, 0.0))

bsp_e3 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e3, cp1_e3, cp2_e3, cp3_e3, cp4_e3],
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
e3  = f.edge_curve(v_P3, v_P0, bsp_e3, True)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: lead-in LINE + 3 B-spline sub-curves ──────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi165.stp")
