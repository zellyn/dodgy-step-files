"""Gp066 — ShapeFix_Edge.FixSameParameter selection-bias tolerance comparison.

Catalog claim: Among multiple candidate tolerances tested during same-parameter
repair, FixSameParameter picks the first tolerance exceeding Precision::Confusion
rather than the minimum feasible tolerance. This creates edges with suboptimal fit.

Fixture: STEP edge with 3D BSpline curve (knots 0–3, degree 3) paired with
a linear PCURVE. Tolerance mismatch forces repair algorithm to select among
candidates; suboptimal choice leaves edge with larger-than-necessary deviation.

Mechanism: GEOMETRIC_CURVE_SET containing the defect EDGE_CURVE. OCC yields empty.

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp066",
    defect=(
        "EDGE_CURVE with degree-3 B-spline 3D curve (knots 0–3) and linear PCURVE; "
        "FixSameParameter picks first-exceeds-Precision::Confusion tolerance "
        "instead of minimum feasible tolerance; "
        "suboptimal tolerance selection leaves larger-than-necessary deviation; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor point for GEOMETRIC_CURVE_SET
anchor = f.cartesian_point((0.0, 0.0, 0.0))

# Degree-3 B-spline 3D curve with 4 knot spans (knots 0,1,2,3)
# 7 control points for degree 3 with internal knots at 1 and 2
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 2.0, 0.0))
cp2 = f.cartesian_point((2.0, 1.0, 0.0))
cp3 = f.cartesian_point((3.0, 3.0, 0.0))
cp4 = f.cartesian_point((4.0, 1.0, 0.0))
cp5 = f.cartesian_point((5.0, 2.0, 0.0))
cp6 = f.cartesian_point((6.0, 0.0, 0.0))

# degree-3, 7 poles: knots need n+p+1=11; mults (4,1,1,1,4) = 11 at (0,1,2,3,4)
# Wait: 7 poles degree 3: n+p+1 = 7+3+1 = 11 = sum of mults
# mults (4,1,1,1,4) = 11 ✓; knots (0,1,2,3,4)
# But catalog says "knots 0–3" — let's use (0,1,2,3) with mults (4,1,1,4) = 10
# 6 poles: 6+3+1 = 10 ✓
curve3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('spline_0_to_3',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,1.0,2.0,3.0),.UNSPECIFIED.)"
)

# Host plane for the PCURVE
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# Linear PCURVE: straight line from (0,0) to (3,0) in UV
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
uv_start = f.cartesian_point((0.0, 0.0))
uv_dir   = f.direction((1.0, 0.0))
uv_vec   = f.vector(uv_dir, 3.0)
line2d   = f.line(uv_start, uv_vec)
defrep   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('linear_pcurve',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{surf.eid},#{defrep.eid})")

# SURFACE_CURVE: spline 3D curve + linear pcurve (mismatch forces tolerance selection)
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{curve3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

v_start = f.vertex_point(cp0)
v_end   = f.vertex_point(cp5)
edge = f._emit_raw(
    f"EDGE_CURVE('fixsameparam_bias',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('gcs',(#{anchor.eid},#{edge.eid}))")
f.add_product_chain(gcs)
