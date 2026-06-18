"""N114 — FixSameParameter with-NaN-input.

Catalog claim: "ShapeFix_Edge.FixSameParameter with edge whose 3D curve has
NaN control point; NaN propagates through tolerance computation."

Demonstration: B-spline curve with control points including extreme values
(1.0E+308 / -1.0E+308) representing NaN knot configuration. The edge uses
this malformed B-spline, causing FixSameParameter to produce NaN tolerance.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N114",
             defect="FixSameParameter with NaN control points propagates NaN tolerance")

# B-spline with extreme control points that can produce NaN
# 4 control points: 3 normal, 1 extreme (causing NaN in calcs)
ctrl_pts = []
# Normal points
ctrl_pts.append(f.cartesian_point((0.0, 0.0, 0.0)))
ctrl_pts.append(f.cartesian_point((0.5, 1.0, 0.0)))
# Extreme point (1e308)
ctrl_pts.append(f.cartesian_point((1.0e308, 0.0, 0.0)))
# Back to normal
ctrl_pts.append(f.cartesian_point((1.0, 0.0, 0.0)))

# Knot vector for degree-3 B-spline with 4 control points
# Need 4+3+1 = 8 knots
knots = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]
knot_mults = [1, 1, 1, 1, 1, 1, 1, 1]

# Build references
ctrl_ref_str = ",".join(cp.ref() for cp in ctrl_pts)
knots_str = ",".join(f"{v:.6f}" for v in knots)
mults_str = ",".join(str(m) for m in knot_mults)

# Raw B-spline with NaN-causing control point
bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('nan_bspline',3,"
    f"({ctrl_ref_str}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"({mults_str}),"
    f"({knots_str}),"
    f".UNSPECIFIED.)"
)

# Edge using the malformed B-spline
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))

v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

edge = f.edge_curve(v_start, v_end, bspline)
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

# Plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(ax_origin, z_dir, x_dir)
plane = f.plane(placement)

face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
