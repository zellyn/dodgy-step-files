"""N086 — Closed BSpline SameParameter wrapping.

Catalog claim: "ShapeFix_Edge.FixSameParameter fails to account for parameter
wrapping in periodic B-splines. Computes SameParameter assuming open curve;
closed spline edges with v ∈ [0,2π) incorrectly flagged as non-same-parameter
when edge uses modulo arithmetic."

Demonstration: An edge whose 3D curve is a closed periodic B-spline circle
approximation with knot domain [0, 2π]. The EDGE_CURVE's start and end
VERTEX_POINTs are coincident (same 3D location), as required for a closed
curve. The edge parameter runs the full domain [0, 2π]. ShapeFix_Edge's
FixSameParameter computes the parameter for the start vertex on the open-curve
assumption, gets a different value than 2π (since the curve wraps), and
incorrectly flags the edge as non-same-parameter. The actual parameter should
be treated modulo 2π.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="N086",
             defect="FixSameParameter ignores parameter wrapping on periodic closed B-spline edge")

# -----------------------------------------------------------------------
# Closed periodic B-spline circle approximation.
# We use a degree-3 B-spline with 9 control points approximating a circle
# of radius 1 centered at origin, in the XY plane.
# The knot domain runs [0, 2π] and the curve is periodic (closed).
# Control points: evenly spaced on the unit circle at angles k*π/4, k=0..8
# with cp[8] == cp[0] (closure).
# -----------------------------------------------------------------------
TAU = 2 * math.pi
angles = [k * TAU / 8 for k in range(9)]  # 0, π/4, π/2, ..., 2π
ctrl_pts = []
for a in angles:
    cp = f.cartesian_point((math.cos(a), math.sin(a), 0.0))
    ctrl_pts.append(cp)
# ctrl_pts[8] is at angle 2π = angle 0, same location as ctrl_pts[0]

# Periodic B-spline curve (degree 3, 9 ctrl pts, uniform periodic knots).
# Knot vector for periodic degree-3 with 9 pts: 12 knots spaced evenly
# by 2π/8 = π/4. Multiplicities all 1 for uniform periodic.
knot_step = TAU / 8
knots = [k * knot_step for k in range(10)]  # 0, π/4, ..., 2π (10 knots for 9 pts, deg 3, periodic)
# For a periodic B-spline of degree d with n control points:
# number of knots = n + 1 for the knot vector, but encoding varies.
# Use standard: n_ctrl=9, deg=3, #knots=9+3+1=13 with uniform spacing.
# We'll use a simpler approach: 13 knots spaced π/4 apart, starting from -3*(π/4)
# Actually: for this fixture the exact knot count matters less than the
# key property that the curve is periodic (CLOSED_CURVE flag) with domain
# spanning exactly 2π, so FixSameParameter mismatch occurs at parameter wrap.
# Use explicit periodic encoding: 13 knots, multiplicities all 1.
n_knots = 13
periodic_knots = [round((k - 3) * knot_step, 10) for k in range(n_knots)]
knot_mults = [1] * n_knots
knots_str = ",".join(f"{v:.6f}" for v in periodic_knots)
mults_str = ",".join(str(m) for m in knot_mults)
ctrl_ref_str = ",".join(cp.ref() for cp in ctrl_pts)

# B_SPLINE_CURVE_WITH_KNOTS: closed periodic curve (PERIODIC_KNOTS or UNSPECIFIED)
# Args: name, degree, control_points_list, curve_form, closed_curve,
#       self_intersect, knot_multiplicities, knots, knot_spec
bspline_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('closed_bspline_circle',3,"
    f"({ctrl_ref_str}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"({mults_str}),"
    f"({knots_str}),"
    f".UNSPECIFIED.)"
)

# -----------------------------------------------------------------------
# Edge: start and end vertex at the same 3D point (angle=0 = angle=2π)
# Both vertices share the same CARTESIAN_POINT (the closure point).
# The edge runs the full [0,2π] domain of the B-spline.
# -----------------------------------------------------------------------
closure_pt = f.cartesian_point((1.0, 0.0, 0.0))   # angle=0 on unit circle
v_start = f.vertex_point(closure_pt)
v_end   = f.vertex_point(closure_pt)   # same point — closed loop

edge = f.edge_curve(v_start, v_end, bspline_curve, True)
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

# A face on the planar disk (z=0 plane); the closed B-spline defines the boundary
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
