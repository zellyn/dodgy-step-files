"""N037 — Curve gaps between adjacent B-spline segments after format conversion.

After format conversion the endpoints of adjacent 3D curve segments along a
wire no longer meet within geometric tolerance. Two B_SPLINE_CURVE_WITH_KNOTS
segments where the end control point of segment 1 (at 10.0+1e-4) does not
equal the start control point of segment 2 (at 10.0), leaving a gap of 1.0E-4
that exceeds the declared tolerance 1.0E-5.

Byte assertions:
  count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 2
  count_entity_def(b'EDGE_CURVE') == 2
  contains(b'1.0E-5')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N037",
    defect=(
        "2 B_SPLINE_CURVE_WITH_KNOTS segments; end of seg1 at x=10.0001, "
        "start of seg2 at x=10.0; gap 1.0E-4 > declared tol 1.0E-5; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Segment 1: degree-1 B-spline from x=0 to x=10.0001 (slightly overshoots).
bs1_p0 = f.cartesian_point((0.0, 0.0, 0.0), name="bs1_start")
bs1_p1 = f.cartesian_point((10.0001, 0.0, 0.0), name="bs1_end_overshoot")
bspline1 = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('seg1',1,"
    f"(#{bs1_p0.eid},#{bs1_p1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(2,2),(0.0,1.0),.UNSPECIFIED.)"
)
v1s = f.vertex_point(bs1_p0, name="v1s")
v1e = f.vertex_point(bs1_p1, name="v1e")
e1 = f.edge_curve(v1s, v1e, bspline1, name="edge1")

# Segment 2: degree-1 B-spline from x=10.0 to x=20.0 (starts at nominal position).
bs2_p0 = f.cartesian_point((10.0, 0.0, 0.0), name="bs2_start_nominal")
bs2_p1 = f.cartesian_point((20.0, 0.0, 0.0), name="bs2_end")
bspline2 = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('seg2',1,"
    f"(#{bs2_p0.eid},#{bs2_p1.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(2,2),(0.0,1.0),.UNSPECIFIED.)"
)
v2s = f.vertex_point(bs2_p0, name="v2s")
v2e = f.vertex_point(bs2_p1, name="v2e")
e2 = f.edge_curve(v2s, v2e, bspline2, name="edge2")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('seg_gap',(#{e1.eid},#{e2.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N037','N037','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-5; segment gap 1.0E-4 exceeds it.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','lotar_exchange_precision')"
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
