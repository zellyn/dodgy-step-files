"""N142 — ShapeUpgrade_ConvertCurve2dToBezier precision-semantics asymmetric-tolerance.

Precision test uses one-directional subtraction (parU - param < prec) instead
of absolute distance. When myUSplitValues exceed myUSplitParams, condition
(parU - param < prec) fails when param > parU. Loop exits prematurely, skipping
valid parameter splits.

Geometry: a parametric curve segment with split parameters reversed relative
to reference parameters; exposes the one-sided comparison failure.

(No byte assertions; kernel-test-pair — defect requires ConvertCurve2dToBezier
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N142",
    defect=(
        "ConvertCurve2dToBezier asymmetric-tolerance: split params reversed; "
        "parU - param < prec fails when param > parU; loop exits prematurely; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Single edge representing a curve with reversed parameter context.
p_start = f.cartesian_point((1.0, 0.0, 0.0), name="p_start_reversed")
p_end = f.cartesian_point((0.0, 0.0, 0.0), name="p_end_reversed")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((-1.0, 0.0, 0.0))  # reversed direction
ln = f.line(p_start, f.vector(d, 1.0), name="reversed_line")
edge = f.edge_curve(v_start, v_end, ln, name="reversed_param_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('reversed_param',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N142','N142','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','model_precision')"
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
