"""N076 — ShapeAnalysis_ShapeTolerance.AddTolerance cumulative-mode state leakage.

AddTolerance with mode=true (cumulative) exhibits state leakage across multiple
invocations. The internal accumulator uses += without resetting, causing
tolerances from prior calls to contaminate current aggregation. A shape
processed twice accumulates 2x the expected tolerance delta.

Geometry: multi-edge wire (3 connected line segments) with distinct
edge-level tolerance declarations (5.0e-6, 8.0e-6, 3.0e-6 mm).

(No byte assertions; kernel-test-pair — defect requires two AddTolerance
runtime invocations.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N076",
    defect=(
        "AddTolerance cumulative-mode state leakage: 3-segment wire; "
        "tolerances 5.0e-6, 8.0e-6, 3.0e-6 mm per edge; "
        "double-call accumulates 2x; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# 3 connected line segments.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="p2")
p3 = f.cartesian_point((3.0, 0.0, 0.0), name="p3")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3")

d = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d, 1.0)), name="e0_tol5e6")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d, 1.0)), name="e1_tol8e6")
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(d, 1.0)), name="e2_tol3e6")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cumulative_wire',(#{e0.eid},#{e1.eid},#{e2.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N076','N076','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Geometric mean of the three edge tolerances as file context.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','edge_tol_nominal')"
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
