"""Gn160 — Periodic B-spline curve with parameter wrapping.

Catalog claim: 5-pole closed curve (degree 2, periodic); period=1.0.
Projection parameter may exceed definition range [0,1) after wrapping.
Falsifiable: theProjParam validation must enforce domain bounds in periodic NURBS.

Fixture: A degree-2 periodic B_SPLINE_CURVE_WITH_KNOTS with 5 control
points forming a closed loop. The periodic flag (.T.) means the domain
wraps. An EDGE_CURVE on this curve has vertices at the full-period point
(parameter == period), which should alias to 0 but some kernels fail to
wrap the projection back into [0, 1).

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn160",
    defect=(
        "degree-2 periodic B_SPLINE_CURVE_WITH_KNOTS (5 poles, closed loop, period=1.0); "
        "projection parameter may equal period (1.0) rather than wrapping to 0.0; "
        "theProjParam domain enforcement fails for exactly-periodic endpoints; "
        "EDGE_CURVE on this curve with vertices at start = parameter 0 and end = parameter 1.0"
    ),
)

# 5 control points forming a pentagon (closed periodic curve)
# Degree 2, periodic: knot vector has 5+2=7 knots with uniform spacing
# For periodic degree-2 with 5 poles: knots span one extra period at each end
# Standard periodic knot vector: (-2/5, -1/5, 0, 1/5, 2/5, 3/5, 4/5, 1, 6/5, 7/5)
# We use 5 poles, degree 2, periodic .T.
# Simplified: knots (0, 1/5, 2/5, 3/5, 4/5) repeated with period prefix/suffix
# For OCC periodic B-spline: mults all 1 except for closure
# Use uniform knots 0..4, period = 5, poles on a circle of radius 5

r = 5.0
cp0 = f.cartesian_point((r,           0.0,         0.0))
cp1 = f.cartesian_point((r * math.cos(2*math.pi/5), r * math.sin(2*math.pi/5), 0.0))
cp2 = f.cartesian_point((r * math.cos(4*math.pi/5), r * math.sin(4*math.pi/5), 0.0))
cp3 = f.cartesian_point((r * math.cos(6*math.pi/5), r * math.sin(6*math.pi/5), 0.0))
cp4 = f.cartesian_point((r * math.cos(8*math.pi/5), r * math.sin(8*math.pi/5), 0.0))

# Periodic degree-2 B-spline: 5 knots with mult 1 each, period = 5/5 = 1.0
# STEP encoding: for periodic curve, knot vector is the base knots only
# knots: 0, 0.2, 0.4, 0.6, 0.8 — each mult 1; period wraps at 1.0
# DEFECT: vertex at parameter 1.0 (== period) should wrap to 0.0
curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('periodic_pentagon',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(1,1,1,1,1),(0.0,0.2,0.4,0.6,0.8),.UNSPECIFIED.)"
)

# Vertices at the "start" and "end" of the curve's parameter domain
# Start at parameter 0.0 = point cp0; end at parameter 1.0 (== period, alias to 0.0)
# Both should map to the same 3D point (r, 0, 0) for a periodic curve
v_start = f.vertex_point(cp0, name="v_period_start")
v_end   = f.vertex_point(
    f.cartesian_point((r, 0.0, 0.0), name="period_end_1.0"),
    name="v_period_end_at_1"
)

edge = f.edge_curve(v_start, v_end, curve, name="periodic_edge")
loop = f.edge_loop([f.oriented_edge(edge, True)])

# Host plane to make an ADVANCED_FACE
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
