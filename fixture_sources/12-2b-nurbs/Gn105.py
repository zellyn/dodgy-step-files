"""Gn105 — rational-with-coincident-poles IsClosed

Catalog claim: "ShapeAnalysis_Curve.IsClosed checks position only, ignoring
weights on coincident poles. Closed rational curve with coincident start/end
but different weights."

Demonstration: A B_SPLINE_CURVE_WITH_KNOTS with rational weights where the
start and end poles have identical 3D positions (coincident) but different
weights. IsClosed should reject this as topologically inconsistent (the curve
closes spatially but the underlying weights differ), yet the defect is that
IsClosed only compares coordinates and ignores the weight mismatch.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn105",
             defect="rational curve coincident poles with differing weights; IsClosed ignores weight mismatch")

# Control points for a closed curve: form a loop in 3D but with rational weights
# Start pole (0,0,0) weight 1.0
# Mid pole (1,0,0) weight sqrt(2)≈1.414
# End pole (0,0,0) weight 2.0 (same position as start, different weight)
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
cp2 = f.cartesian_point((0.0, 0.0, 0.0))  # coincident with cp0

# Rational B-spline degree-2, 3 control points, weights [1.0, 1.414, 2.0]
# Knots [0,0,0,1,1,1] (C0 open ends)
bspline_curve = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('rational_closed',"
    "2,.F.,"
    f"({cp0.ref()},{cp1.ref()},{cp2.ref()}),"
    ".UNSPECIFIED.,.F.,.F.,"
    "(1,1,1),"
    "(0.0,1.0),"
    ".UNSPECIFIED.,"
    "(1.0,1.414213562373095,2.0))"
)

# Edge using the curve (degenerate closure but with weight asymmetry)
v0 = f.vertex_point(cp0)
v2 = f.vertex_point(cp2)
edge = f.edge_curve(v0, v2, bspline_curve, same_sense=True)

# Single edge loop (degenerate as closure)
loop = f.edge_loop([f.oriented_edge(edge)])
fob = f.face_outer_bound(loop)

# Use a plane as the underlying surface for the face (we only care about the edge defect)
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
plane = f.plane(placement)

face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
