"""N145 — BRepBuilderAPI_Sewing.SameParameterEdge setMaxTolerance-bypass-raw-write.

Direct BRep_TEdge::Tolerance() write bypasses SetMaxTolerance() API cap
validation. MaxTolerance cap 0.01; computed tolerance 0.05; raw write at
line 1168 ignores cap. Edge tolerance exceeds API contract; cap enforcement
violated.

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation with SetMaxTolerance(0.01).)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N145",
    defect=(
        "SameParameterEdge setMaxTolerance-bypass-raw-write: "
        "MaxTol cap=0.01, computed tol=0.05; raw write ignores cap; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two faces with 0.05 mm gap — sewing input triggering the bypass.
p00 = f.cartesian_point((0.0, 0.0, 0.0), name="f1_p00")
p10 = f.cartesian_point((5.0, 0.0, 0.0), name="f1_p10")
q00 = f.cartesian_point((0.0, 0.0, 0.05), name="f2_p00_gap")
q10 = f.cartesian_point((5.0, 0.0, 0.05), name="f2_p10_gap")

v00 = f.vertex_point(p00, name="v00")
v10 = f.vertex_point(p10, name="v10")
vq00 = f.vertex_point(q00, name="vq00")
vq10 = f.vertex_point(q10, name="vq10")

d_x = f.direction((1.0, 0.0, 0.0))
e_f1 = f.edge_curve(v00, v10, f.line(p00, f.vector(d_x, 5.0)), name="shared_e_f1")
e_f2 = f.edge_curve(vq00, vq10, f.line(q00, f.vector(d_x, 5.0)), name="shared_e_f2_gap")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('sewing_input',(#{e_f1.eid},#{e_f2.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N145','N145','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','sewing_gap')"
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
