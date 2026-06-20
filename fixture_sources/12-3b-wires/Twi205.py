"""Twi205 — ShapeAnalysis_Wire.CheckIntersectingEdges B-spline-tangent-touch.

Catalog claim: Two B-spline edges touching tangentially (single point, no
crossing). CheckIntersectingEdges reports intersection despite no transverse
crossing.

Mechanism: A 3-edge EDGE_LOOP on a PLANE. Edges E0 (LINE) and E2 (B-spline)
share start/end vertices normally. The defect is that E1 and E2 are both
cubic B-spline curves that arrive at their shared vertex (P2) with the SAME
tangent direction — they touch tangentially, meeting at a single point with
parallel tangents. CheckIntersectingEdges' pairwise curve-intersection logic
finds this tangential contact and records it as an intersection event even
though the curves don't actually cross (no transverse intersection). The false
positive IS the mechanism.

Wire on PLANE (normal +Z):
  P0 = (0, 0, 0)  P1 = (10, 0, 0)  P2 = (5, 8, 0)
  E0: LINE from P0 to P1 (base)
  E1: B-spline from P1 to P2 — control pts (10,0), (11,4), (8,8), (5,8)
      arrives at P2 with tangent direction (-3, 0) i.e. going left
  E2: B-spline from P2 to P0 — control pts (5,8), (2,8), (-1,4), (0,0)
      departs P2 with tangent direction (-3, 0) i.e. same tangent going left
  The two B-splines share tangent direction at P2 — tangential touch IS defect.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi205",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; 3-edge EDGE_LOOP; "
        "E1 and E2 are cubic B_SPLINE_CURVE_WITH_KNOTS that arrive/depart "
        "shared vertex P2=(5,8,0) with the same tangent direction (-3,0,0) — "
        "tangential touch at single point IS the defect; "
        "CheckIntersectingEdges reports intersection despite no transverse "
        "crossing — false positive IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# -- PLANE: normal +Z ---------------------------------------------------------
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# -- Vertices -----------------------------------------------------------------
P0 = (0.0,  0.0, 0.0)
P1 = (10.0, 0.0, 0.0)
P2 = (5.0,  8.0, 0.0)

v0 = f.vertex_point(f.cartesian_point(P0))
v1 = f.vertex_point(f.cartesian_point(P1))
v2 = f.vertex_point(f.cartesian_point(P2))

# -- E0: P0 -> P1, base LINE --------------------------------------------------
import math as _math
dx0 = P1[0] - P0[0]
ln_e0 = f.line(f.cartesian_point(P0), f.vector(f.direction((1.0, 0.0, 0.0)), dx0))
e0 = f.edge_curve(v0, v1, ln_e0)

# -- E1: P1 -> P2, cubic B-spline ---------------------------------------------
# Control points: (10,0,0), (11,4,0), (8,8,0), (5,8,0)
# Arrives at P2=(5,8,0) with tangent proportional to (5,8)-(8,8) = (-3,0) -> left
# degree=3, 4 control points: sum(mults) = 4+3+1 = 8; clamped: [4,4]
cp1_pts = [
    f.cartesian_point((10.0, 0.0, 0.0)),
    f.cartesian_point((11.0, 4.0, 0.0)),
    f.cartesian_point((8.0,  8.0, 0.0)),
    f.cartesian_point((5.0,  8.0, 0.0)),
]
bsp_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp1_pts,
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e1 = f.edge_curve(v1, v2, bsp_e1)

# -- E2: P2 -> P0, cubic B-spline with SAME tangent at P2 --------------------
# Control points: (5,8,0), (2,8,0), (-1,4,0), (0,0,0)
# Departs P2=(5,8,0) with tangent proportional to (2,8)-(5,8) = (-3,0) -> left
# SAME tangent direction as E1 arrives — tangential touch IS the defect
cp2_pts = [
    f.cartesian_point((5.0,  8.0, 0.0)),
    f.cartesian_point((2.0,  8.0, 0.0)),
    f.cartesian_point((-1.0, 4.0, 0.0)),
    f.cartesian_point((0.0,  0.0, 0.0)),
]
bsp_e2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp2_pts,
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
e2 = f.edge_curve(v2, v0, bsp_e2)

# -- EDGE_LOOP ----------------------------------------------------------------
loop  = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], plane)
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi205.stp")
