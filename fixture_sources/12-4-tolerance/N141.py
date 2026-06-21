"""N141 — ShapeFix_IntersectionTool.FixIntEdges tolerance_selection.

Vertex tolerance initialized from V1 without considering V2 tolerance level.
When V1 tol=0.001 and V2 tol=0.01 and the intersection is near V2, the
intersection result uses insufficient tolerance for the high-tolerance vertex.

Geometry: two edges meeting at a junction; V1 has tight tolerance (0.001 mm)
and V2 has coarse tolerance (0.01 mm); intersection near V2.

(No byte assertions; kernel-test-pair — defect requires FixIntEdges runtime
invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N141",
    defect=(
        "FixIntEdges tolerance_selection: V1 tol=0.001, V2 tol=0.01; "
        "intersection near V2 uses V1 tol — insufficient for high-tol vertex; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# V1 (tight tol) at origin; V2 (coarse tol) at (10,0,0).
# Intersection: edge A from (-1,0,0) to (11,0,0); edge B from (10,-1,0) to (10,1,0).
p_v1 = f.cartesian_point((0.0, 0.0, 0.0), name="p_v1_tight")
p_v2 = f.cartesian_point((10.0, 0.0, 0.0), name="p_v2_coarse")
p_a_start = f.cartesian_point((-1.0, 0.0, 0.0), name="p_a_start")
p_b_start = f.cartesian_point((10.0, -1.0, 0.0), name="p_b_start")
p_b_end = f.cartesian_point((10.0, 1.0, 0.0), name="p_b_end")

vv1 = f.vertex_point(p_v1, name="v1_tight")
vv2 = f.vertex_point(p_v2, name="v2_coarse")
va_start = f.vertex_point(p_a_start, name="va_start")
vb_start = f.vertex_point(p_b_start, name="vb_start")
vb_end = f.vertex_point(p_b_end, name="vb_end")

d_x = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(va_start, vv2, f.line(p_a_start, f.vector(d_x, 11.0)), name="eA_thru_v1v2")
d_y = f.direction((0.0, 1.0, 0.0))
eB = f.edge_curve(vb_start, vb_end, f.line(p_b_start, f.vector(d_y, 2.0)), name="eB_thru_v2")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('int_tol',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N141','N141','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Two tolerance levels: tight (V1) and coarse (V2).
unc_v1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','v1_tight_tol')"
)
unc_v2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','v2_coarse_tol')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_v1.eid},#{unc_v2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
