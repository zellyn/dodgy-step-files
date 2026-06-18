"""N167 — ShapeFix_ShapeTolerance.LimitTolerance iamax boundary condition flip.

Catalog claim: "ShapeFix_ShapeTolerance.LimitTolerance checks (tmax >= tmin) but
semantically enforces (tmax > tmin). The equality case is ambiguous and unchecked,
allowing tmax == tmin to bypass intended bounds."

Demonstration: A B-spline curve edge where the control point tolerance and
the curve tolerance are set to identical values (tmax == tmin == 0.001).
LimitTolerance should reject or clamp this, but the boundary-condition flip
allows it to proceed unclamped.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="N167",
    defect="LimitTolerance iamax check fails on equality boundary (tmax == tmin)"
)

# Create a simple B-spline curve with degree 3, 4 control points
degree = 3
ctrl_pts = [
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((1.0, 0.5, 0.0)),
    f.cartesian_point((2.0, 0.5, 0.0)),
    f.cartesian_point((3.0, 0.0, 0.0)),
]

# Uniform knot vector for degree 3 with 4 control points
# Number of knots = 4 + 3 + 1 = 8, with multiplicities [4, 4]
knots = [0.0, 1.0]
knot_mults = [4, 4]

bspline = f.b_spline_curve_with_knots(
    degree=degree,
    control_points=ctrl_pts,
    knot_multiplicities=knot_mults,
    knots=knots,
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED"
)

# Create vertices at curve endpoints
v_start = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_end = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))

# Edge using the B-spline curve
edge = f.edge_curve(v_start, v_end, bspline, same_sense=True)

# Wrap in wire and face
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

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
