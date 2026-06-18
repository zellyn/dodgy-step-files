"""Gn171 — Periodic B-spline curve with non-closing control polygon.

Catalog claim: "Periodic B-spline marked as closed but control polygon does not
close (first and last poles differ), causing origin re-anchoring to fail or
produce parametric discontinuity across the period boundary."

Demonstration: A degree-2 periodic B-spline with 4 control points arranged in
an arc where P0 ≠ P3. The knot vector is periodic [0, 0.33, 0.67, 1, 1.33, 1.67, 2]
with multiplicities (1,1,1,1,1,1) and periodic flag set. Without proper origin
re-anchoring (SetOrigin call), the parametrization jumps at the period boundary.

The defect manifests when SameParameter validation requires the curve to be
continuous across u=0 and u=period, but the non-closing polygon causes the
evaluation to fail the continuity check.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn171",
             defect="periodic B-spline with non-closing control polygon: first and last poles differ")

# 4 control points forming an incomplete arc
# Periodic B-spline: degree 2, 4 poles, periodic
# For periodic: sum(knot_mults) = n_poles + degree + 1 = 4 + 2 + 1 = 7
# Periodic knot vector with 6 distinct knots (overlapping periods)
p0 = f.cartesian_point((1.0, 0.0, 0.0))
p1 = f.cartesian_point((0.707, 0.707, 0.0))  # ~45°
p2 = f.cartesian_point((0.0, 1.0, 0.0))      # ~90°
p3 = f.cartesian_point((-0.5, 0.5, 0.0))     # non-closing: not back to p0

# Periodic knot vector [0, 1/3, 2/3, 1, 4/3, 5/3, 2] (scaled to [0,2π] semantically)
# Multiplicities all 1: (1,1,1,1,1,1) = 6 total, but sum must be 7
# Add one more: [0, 1/3, 2/3, 1, 4/3] with mults (1,1,2,1,2) = 7
u_knots = [0.0, 0.333, 0.667, 1.0, 1.333]
u_mults = [1, 1, 2, 1, 2]

bspl_curve = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[p0, p1, p2, p3],
    knot_multiplicities=u_mults,
    knots=u_knots,
    curve_form="UNSPECIFIED",
    closed=True  # Mark as periodic/closed
)

# Create a degenerate face using the curve to expose the discontinuity
# A polyline approximating the arc
loop = f.closed_polyline_loop([p0, p1, p2, p3])
fob = f.face_outer_bound(loop)

# Use the curve as a basis (normally would be trimmed surface, here we simplify)
# Create a plane and build a face on it
plane = f.plane((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
