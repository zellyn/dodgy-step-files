"""N144 — ShapeUpgrade_UnifySameDomain.UnionPCurves vertex_tolerance_mismatch.

Vertex tolerance tracking fails when concatenating PCurves from edges with
divergent tolerances. Shared vertex V1(tol=1e-3) and V2(tol=1e-2) at junction;
max_tolerance_tracking inconsistent. Concatenated PCurve has mismatched
tolerance across chain.

Geometry: two edges meeting at shared vertex V1 (tight tol 1e-3) and outer
vertices V0, V2 with coarser tolerance 1e-2.

(No byte assertions; kernel-test-pair — defect requires UnionPCurves runtime
invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N144",
    defect=(
        "UnionPCurves vertex_tolerance_mismatch: 2-edge chain; "
        "shared V1 tol=1e-3; outer V0/V2 tol=1e-2; "
        "max_tolerance_tracking inconsistent across concatenated PCurve; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two-edge chain: V0 — e0 — V1(tight) — e1 — V2(coarse).
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p_v0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p_v1_tight")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="p_v2_coarse")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_tight")
v2 = f.vertex_point(p2, name="v2_coarse")

d = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d, 1.0)), name="e0")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d, 1.0)), name="e1")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('pcurve_chain',(#{e0.eid},#{e1.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N144','N144','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Tight tolerance for shared vertex V1.
unc_tight = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','v1_tight_tol')"
)
# Coarse tolerance for outer vertices.
unc_coarse = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','v0v2_coarse_tol')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_tight.eid},#{unc_coarse.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
