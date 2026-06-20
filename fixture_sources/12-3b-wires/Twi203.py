"""Twi203 — ShapeAnalysis_Wire.CheckTail B-spline tail-detection.

Catalog claim: Wire's last edge is a B-spline with smoothly decreasing
magnitude approaching zero. CheckTail's threshold uses parameter range not 3D
length, causing false negatives.

Mechanism: The wire has three edges on a plane. The last edge (E2) is a cubic
B-spline whose control-point geometry causes the 3D arc length to nearly vanish
near its end parameter — the curve approaches its start point tangentially,
squeezing to ~1e-5 3D length in the last 10% of the parameter range. CheckTail
measures the tail in parameter space (range fraction ~0.1) rather than 3D arc
length (~1e-5), so the threshold in parameter units (~Precision::Confusion) is
not exceeded and the tail is not flagged. The 3D-length tail goes undetected.

Wire on PLANE (normal +Z):
  E0: (0,0,0) → (10,0,0)   — LINE, bottom
  E1: (10,0,0) → (5,5,0)   — LINE, diagonal back toward center
  E2: B-spline from (5,5,0) → (0,0,0) with a smoothly decelerating tail:
      control points: (5,5,0), (3,3,0), (1,1,0), (0.0001,0.0001,0), (0,0,0)
      The last control points cluster near the origin — parametric range spans
      the full [0,1] but 3D length in the last segment is ~1.4e-4, which
      CheckTail's parameter-based threshold misses.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi203",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; 3-edge outer EDGE_LOOP; "
        "E2 is a degree-3 B_SPLINE_CURVE_WITH_KNOTS from (5,5,0) back to (0,0,0) "
        "with last two control points compressed near origin so 3D tail length "
        "~1.4e-4 in last parameter-range segment ~0.25; "
        "CheckTail threshold uses parameter range not 3D length — false negative "
        "IS the mechanism; EDGE_LOOP IS wired into FACE_OUTER_BOUND -> "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── PLANE: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ─────────────────────────────────────────────────────────────────
P0 = (0.0,    0.0,    0.0)
P1 = (10.0,   0.0,    0.0)
P2 = (5.0,    5.0,    0.0)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))

# ── E0: P0→P1, bottom LINE ───────────────────────────────────────────────────
ln_e0 = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), 10.0))
e0 = f.edge_curve(v0, v1, ln_e0)

# ── E1: P1→P2, diagonal LINE ─────────────────────────────────────────────────
import math as _math
dx1, dy1 = P2[0] - P1[0], P2[1] - P1[1]
mag1 = _math.sqrt(dx1*dx1 + dy1*dy1)
ln_e1 = f.line(
    f.cartesian_point(P1),
    f.vector(f.direction((dx1 / mag1, dy1 / mag1, 0.0)), mag1),
)
e1 = f.edge_curve(v1, v2, ln_e1)

# ── E2: P2→P0, B-spline with decelerating tail ───────────────────────────────
# Degree-3 B-spline; 5 control points.
# Control points: (5,5,0) → (3,3,0) → (1,1,0) → (1e-4,1e-4,0) → (0,0,0)
# The last two CPs are clustered near (0,0,0); parametric range [0,1]
# with uniform knots means the last Bezier segment spans t in [0.75,1.0]
# but its 3D length is ~sqrt(2)*1e-4 ≈ 1.4e-4 — the tail.
cp_coords = [
    (5.0,    5.0,    0.0),
    (3.0,    3.0,    0.0),
    (1.0,    1.0,    0.0),
    (1e-4,   1e-4,   0.0),
    (0.0,    0.0,    0.0),
]
cp_pts = [f.cartesian_point(c) for c in cp_coords]

# degree=3, n_poles=5: sum(mults) = 5 + 3 + 1 = 9
# knots: [0, 0.333, 0.667, 1.0] with mults [4,1,1,3] → sum=9 ✓
# (clamped cubic with one interior knot at 1/3 and 2/3, then end)
# Actually for 5 CPs degree 3: sum = 9; clamped: mults [4,1,4] = 9, knots [0,0.5,1]
bspline_e2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp_pts,
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
)
e2 = f.edge_curve(v2, v0, bspline_e2)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi203.stp")
