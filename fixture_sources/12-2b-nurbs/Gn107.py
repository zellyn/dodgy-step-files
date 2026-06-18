"""Gn107 — approximate-mode B-spline high-frequency

Catalog claim: "ShapeAnalysis_Curve.FillBndBox approximate mode misses
high-frequency oscillation. Control points form sawtooth pattern;
bounding-box computation should span [0,1] but misses peaks."

Demonstration: A B_SPLINE_CURVE_WITH_KNOTS with control polygon that forms
a sawtooth (high-frequency oscillation). The control points go (0,0), (1,1),
(0,0), (1,1), (0,0) — but interior sampled points of the curve bulge out to
y=1.5 or higher. The approximate bounding-box mode misses these interior peaks
and reports box only covering [0,1] instead of [0,1.5].
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn107",
             defect="B-spline high-frequency sawtooth; bounding-box approximate mode misses peaks")

# Sawtooth control points: low, high, low, high, low
# But the curve interpolation will bulge higher than the control polygon
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.25, 1.5, 0.0))
cp2 = f.cartesian_point((0.5, 0.0, 0.0))
cp3 = f.cartesian_point((0.75, 1.5, 0.0))
cp4 = f.cartesian_point((1.0, 0.0, 0.0))

# Degree-2 B-spline with 5 control points
# Knots: [0,0,0,1,2,3,3,3] (6 intervals, start/end clamped C0)
bspline_curve = f._emit_raw(
    "B_SPLINE_CURVE_WITH_KNOTS('sawtooth',"
    "2,.F.,"
    f"({cp0.ref()},{cp1.ref()},{cp2.ref()},{cp3.ref()},{cp4.ref()}),"
    ".UNSPECIFIED.,.F.,.F.,"
    "(1,2,1,1,1),"
    "(0.0,1.0,2.0,3.0),"
    ".UNSPECIFIED.)"
)

# Edge wrapping the curve
v0 = f.vertex_point(cp0)
v4 = f.vertex_point(cp4)
edge = f.edge_curve(v0, v4, bspline_curve, same_sense=True)

# Simple edge loop
loop = f.edge_loop([f.oriented_edge(edge)])
fob = f.face_outer_bound(loop)

# Plane as background surface
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
plane = f.plane(placement)

face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
