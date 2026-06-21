"""N161 — tolerance_escalation unbounded multiplier.

Tolerance escalation during sewing lacks upper bound. Factor 1000× applied
without capping; initial 1e-7 becomes 1e-4. Tests BRepBuilderAPI_Sewing
escalation validation.

Geometry: edge with ultra-tight declared tolerance (1e-7) that would be
escalated 1000× to 1e-4 during sewing without a cap.

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N161",
    defect=(
        "tolerance_escalation unbounded_multiplier: initial tol 1e-7; "
        "1000x factor applied without cap; becomes 1e-4; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
edge = f.edge_curve(v_start, v_end, f.line(p_start, f.vector(d, 1.0)), name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('escalation_input',(#{edge.eid}))")

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N161','N161','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Initial tolerance 1e-7 — escalated 1000× to 1e-4 without cap.
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},'distance_accuracy_value','initial_tol')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
