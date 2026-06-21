"""Gp151 — ShapeAnalysis_Edge.CheckPCurveRange periodic_range_semantics.

Catalog claim: Periodic P-curve with parameter range straddling 2π boundary;
validation assumes wrap-around is intentional without detecting non-monotonic
parametrization. Reproduces OCCT line 1007 defect.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_CURVE whose PCURVE is a
CIRCLE with parameter range [5.5, 0.8] — straddling 2π (i.e., the range
wraps from 5.5 rad to 0.8 rad crossing 2π≈6.283). CheckPCurveRange must
detect the non-monotonic range as a potential parametrization error.
OCC yields empty.

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gp151",
    defect=(
        "EDGE_CURVE with PCURVE that is a CIRCLE (radius 1.0) trimmed to "
        "parameter range [5.5, 0.8] rad — straddling the 2π boundary; "
        "CheckPCurveRange at OCCT line 1007 assumes wrap is intentional "
        "without detecting non-monotonic (decreasing→wrap) parametrization; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

anchor = f.cartesian_point((0.0, 0.0, 0.0))

# Host plane for pcurve
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# 3D LINE for the edge (we need a 3D curve; the defect is in the pcurve range)
p_start_3d = f.cartesian_point((math.cos(5.5), math.sin(5.5), 0.0))
p_end_3d   = f.cartesian_point((math.cos(0.8), math.sin(0.8), 0.0))
v_start = f.vertex_point(p_start_3d)
v_end   = f.vertex_point(p_end_3d)
dx = math.cos(0.8) - math.cos(5.5)
dy = math.sin(0.8) - math.sin(5.5)
mag = math.sqrt(dx**2 + dy**2)
d3d = f.direction((dx/mag, dy/mag, 0.0))
line3d = f.line(p_start_3d, f.vector(d3d, mag))

# PCURVE: CIRCLE of radius 1.0, parameter range [5.5, 0.8] (wraps past 2π)
# The defect: range [5.5, 0.8] straddles 2π≈6.283
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
# 2D circle center at origin, radius 1.0
ctr2d = f.cartesian_point((0.0, 0.0))
z2d   = f.direction((0.0, 0.0, 1.0))  # For 2D, use 2D axis placement
x2d   = f.direction((1.0, 0.0))       # Reference direction in 2D
# 2D axis placement (2D circles use AXIS2_PLACEMENT_2D)
plc2d = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('',#{ctr2d.eid},#{x2d.eid})"
)
circle2d = f._emit_raw(f"CIRCLE('circle_2d_periodic',#{plc2d.eid},1.0)")

# TRIMMED_CURVE wrapping the circle to range [5.5, 0.8]: non-monotonic wrap
# STEP TRIMMED_CURVE: trim with PARAMETER_VALUE
trim_curve = f._emit_raw(
    f"TRIMMED_CURVE('periodic_wrap_straddle',#{circle2d.eid},"
    f"(PARAMETER_VALUE(5.5)),(PARAMETER_VALUE(0.8)),.T.,.PARAMETER.)"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_periodic_straddle',(#{trim_curve.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('periodic_range_semantics',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('sc_periodic',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('pcurve_straddle_2pi',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('gcs',(#{anchor.eid},#{edge.eid}))")
f.add_product_chain(gcs)
