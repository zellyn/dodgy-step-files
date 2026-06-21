"""N006 — Pcurve drifts out of sync with 3D-curve parameterisation (geometric flavour).

A pcurve was reprojected at non-uniform sampling without rebasing its parameter
range, so parameter-by-parameter evaluation against the 3D curve drifts. Some
receivers compensate by silently inflating edge tolerance to 1.0E-3 to cover
the residual deviation — the edge shows up as "hot" on a tolerance-summary check.

Two B_SPLINE_CURVE_WITH_KNOTS: one 3D curve and one pcurve (2D). The pcurve
knot spacing is non-uniform relative to the 3D curve, encoding the drift.
The SURFACE_CURVE links them; the edge tolerance 1.0E-3 is larger than any
declared model tolerance.

Byte assertions:
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 2
  contains(b'PCURVE') and contains(b'SURFACE_CURVE')
  contains(b'1.0E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N006",
    defect=(
        "pcurve B_SPLINE_CURVE_WITH_KNOTS has non-uniform knots vs 3D curve; "
        "parameter-by-parameter sampling drifts; edge tolerance silently inflated "
        "to 1.0E-3; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# 3D B-spline curve: degree 1, 2 control points (degenerate line from 0 to 10 on X).
# Using degree-1 B-spline with uniform knots as the 3D curve.
p0_3d = f.cartesian_point((0.0, 0.0, 0.0), name="bs3d_p0")
p1_3d = f.cartesian_point((10.0, 0.0, 0.0), name="bs3d_p1")
# B_SPLINE_CURVE_WITH_KNOTS for 3D: degree=1, 2 ctrl pts, knots (0.0, 1.0), mults (2, 2)
bspline3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspline3d',1,"
    f"(#{p0_3d.eid},#{p1_3d.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)

v0 = f.vertex_point(p0_3d, name="v0")
v1 = f.vertex_point(p1_3d, name="v1")

# Host surface: a plane for the pcurve to live on.
ax_orig = f.cartesian_point((0.0, 0.0, 0.0), name="plane_orig")
plane_norm = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, plane_norm, plane_xdir)
plane = f.plane(plc, name="host_plane")

# 2D pcurve B-spline: degree 1, 2 ctrl pts with NON-UNIFORM knots.
# The 3D curve uses (0.0, 1.0) uniformly. The pcurve uses (0.0, 1.5) —
# wrong range, causing parameter drift vs 3D curve at sampled interior points.
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv_ctx','2D'))"
)
pc_p0 = f.cartesian_point((0.0, 0.0), name="pc_p0")
pc_p1 = f.cartesian_point((10.0, 0.0), name="pc_p1")
# Non-uniform knots: end knot at 1.5 instead of 1.0 — encodes the drift.
bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bspline_pc',1,"
    f"(#{pc_p0.eid},#{pc_p1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.5),.UNSPECIFIED.)"
)
pdef = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pdef',(#{bspline_pc.eid}),#{uv_ctx.eid})"
)
pcurve = f._emit_raw(f"PCURVE('pc_drift',#{plane.eid},#{pdef.eid})")

# SURFACE_CURVE linking 3D B-spline and drifted pcurve.
sc = f._emit_raw(
    f"SURFACE_CURVE('sc_drift',#{bspline3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# SameParameter=.T. (claimed, but violated due to knot mismatch drift)
edge = f.edge_curve(v0, v1, sc, True, name="edge_drift")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('drift_set',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N006','N006','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Hot edge tolerance 1.0E-3 — silently inflated to cover drift.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','silently_inflated_hot_edge_tol')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
