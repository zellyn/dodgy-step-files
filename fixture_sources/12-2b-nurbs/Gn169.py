"""Gn169 — Rational B-spline with weight singularity near origin.

Catalog claim: "Rational B-spline weight collapse at interior control point
reduces effective basis; OCCT numerical solvers may lose precision when
weight denominator approaches zero or exhibits extreme variation (1e-6 to 1e6)."

Demonstration: A degree-2 rational B-spline curve in 3D with 5 control points.
One pole near the origin has weight 1e-6 (essentially invisible), while adjacent
poles have weight 1.0. This weight singularity creates a discontinuity in the
rational basis function behavior, potentially triggering precision loss or
adaptive tolerance escalation in parametric evaluation.

The control points form a gentle arc [0,0,0] → [1,0,0] → [2,0,0] → [3,0,0],
but the near-invisible pole at [1.5, 0, 0] with weight 1e-6 creates a
numerical conditioning problem that healers must detect and normalize.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn169",
             defect="rational B-spline with weight singularity: denominator collapse near zero weight pole")

# Control points along a line, with one pole nearly invisible
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))   # weight 1e-6
p2 = f.cartesian_point((2.0, 0.0, 0.0))
p3 = f.cartesian_point((3.0, 0.0, 0.0))
p4 = f.cartesian_point((4.0, 0.0, 0.0))

# Weights: normal start/end, tiny weight on p1, normal others
weights = [1.0, 1e-6, 1.0, 1.0, 1.0]

# Degree 2 (quadratic): 5 poles + degree 2 + 1 = 8 knot-mult sum needed
# Simple knot vector: [0,0,0, 0.5, 1,1,1] gives multiplicities (3,1,3)
# sum(3,1,3) = 7. We need 8. Use [0,0,0, 0.25, 0.5, 1,1,1] -> (3,1,1,3) = 8
u_knots = [0.0, 0.25, 0.5, 1.0]
u_mults = [3, 1, 1, 3]

rational_bspl = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[p0, p1, p2, p3, p4],
    knot_multiplicities=u_mults,
    knots=u_knots,
    curve_form="UNSPECIFIED",
    closed=False
)

# Emit weights as a VECTOR list via raw entity (weights property in Part-21)
# The B_SPLINE_CURVE_WITH_KNOTS signature in Part-21 includes weights at position 9
# We use _emit_raw to inject weights directly
curve_with_weights = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspl_rational',2,({p0.ref()},{p1.ref()},{p2.ref()},{p3.ref()},{p4.ref()}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,3),(0.0,0.25,0.5,1.0),"
    f".UNSPECIFIED.,(1.0,1.E-06,1.0,1.0,1.0))"
)

# Build a simple edge and face to exercise the curve
line1 = f.line((0.0, 0.0, -0.1), (4.0, 0.0, -0.1))
loop = f.closed_polyline_loop([
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((4.0, 0.0, 0.0)),
    f.cartesian_point((4.0, 1.0, 0.0)),
    f.cartesian_point((0.0, 1.0, 0.0))
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], curve_with_weights)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
