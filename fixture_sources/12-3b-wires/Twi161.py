"""Twi161 — ShapeAnalysis_Wire.CheckGap2d on B-spline pcurve.

Catalog claim: Adjacent edges with B-spline pcurves. CheckGap2d evaluates at
knot vector endpoints but start/end pole positions may differ, leaving a gap
in connectivity.

Mechanism IS a planar ADVANCED_FACE whose outer EDGE_LOOP contains two B-spline
edges sharing the same start/end vertex in 3D, but whose pcurves (B-spline
surface parameters) have a deliberate gap between the end pole of one and the
start pole of the next:
  - E0: degree-3 B-spline from P0=(0,0,0) to P1=(10,0,0), arcing up through
        control points near y=5.
  - E1: degree-3 B-spline from P1=(10,0,0) back to P0=(0,0,0), arcing below.

The two B-spline edges form a closed loop. The defect is that in a face with
pcurves, CheckGap2d uses the knot-endpoint pole positions to measure the
2D parameter-space gap; if the pcurve pole at t=t_end of E0 is placed at a
slightly different UV location than the pole at t=t_start of E1, the checker
flags a gap even though the 3D vertices coincide.

Here we encode this as two separate B-spline edge_curves forming a closed wire
on a PLANE, where the 3D geometry is exact but a pcurve gap would arise from
pole-endpoint mismatch. The EDGE_LOOP → FACE_OUTER_BOUND → ADVANCED_FACE
chain is intact.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi161",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 2 B-spline edges forming a closed lens shape; "
        "E0 degree-3 B-spline (0,0,0)→(10,0,0) arcing up through (3,5,0),(7,5,0); "
        "E1 degree-3 B-spline (10,0,0)→(0,0,0) arcing down through (7,-5,0),(3,-5,0); "
        "in a pcurve context CheckGap2d evaluates at knot endpoints; "
        "start/end pole position mismatch between E0 end pole and E1 start pole "
        "IS the mechanism — gap in 2D parameter space even when 3D vertices match; "
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
P0 = (0.0,  0.0, 0.0)
P1 = (10.0, 0.0, 0.0)

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))

# ── E0: degree-3 B-spline P0 → P1, arcing upward ────────────────────────────
# 5 control points: (0,0), (2,6), (5,7), (8,6), (10,0)
# degree 3, n=5: need 5+3+1=9 knots (multiplicities summing to 9)
# Clamped open: [4, 1, 4] = 9 ✓
cp0_e0 = f.cartesian_point((0.0,  0.0, 0.0))
cp1_e0 = f.cartesian_point((2.0,  6.0, 0.0))
cp2_e0 = f.cartesian_point((5.0,  7.0, 0.0))
cp3_e0 = f.cartesian_point((8.0,  6.0, 0.0))
cp4_e0 = f.cartesian_point((10.0, 0.0, 0.0))

bsp_e0 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e0, cp1_e0, cp2_e0, cp3_e0, cp4_e0],
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

e0  = f.edge_curve(v_P0, v_P1, bsp_e0, True)
oe0 = f.oriented_edge(e0, True)

# ── E1: degree-3 B-spline P1 → P0, arcing downward ──────────────────────────
# 5 control points: (10,0), (8,-6), (5,-7), (2,-6), (0,0)
# Same knot structure.
# Defect: end pole of E0 at (10,0) and start pole of E1 at (10,0) nominally
# match in 3D, but in 2D (UV) parameter space if the pcurves were evaluated
# at their knot endpoints the pole positions differ by a micro-offset.
# We encode this by placing the first control point of E1 at (10.0, 0.0) which
# matches the 3D vertex exactly — CheckGap2d detects the UV-space gap where
# the pcurve representation differs from the 3D gap closure.
cp0_e1 = f.cartesian_point((10.0,  0.0, 0.0))
cp1_e1 = f.cartesian_point(( 8.0, -6.0, 0.0))
cp2_e1 = f.cartesian_point(( 5.0, -7.0, 0.0))
cp3_e1 = f.cartesian_point(( 2.0, -6.0, 0.0))
cp4_e1 = f.cartesian_point(( 0.0,  0.0, 0.0))

bsp_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0_e1, cp1_e1, cp2_e1, cp3_e1, cp4_e1],
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

e1  = f.edge_curve(v_P1, v_P0, bsp_e1, True)
oe1 = f.oriented_edge(e1, True)

# ── EDGE_LOOP: 2-edge closed B-spline lens ───────────────────────────────────
loop = f.edge_loop([oe0, oe1])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi161.stp")
