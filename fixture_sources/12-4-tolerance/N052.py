"""N052 — BRepBuilderAPI_Sewing.SameParameterEdge SetMaxTolerance bypass.

Direct BRep_TEdge::Tolerance() write bypasses the SetMaxTolerance API cap.
When computed sewing tolerance (0.05) exceeds the user cap (0.01), the raw
TShape mutation creates an edge with 0.05 tolerance, bypassing the cap.

Input geometry: two faces meeting at a shared edge with non-trivial
discretized-curve tolerance path (edge gap 0.05 mm).

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation with SetMaxTolerance(0.01).)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N052",
    defect=(
        "sewing input: two faces with 0.05 mm edge gap; SetMaxTolerance(0.01) "
        "is bypassed by raw TShape mutation at line 1168; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two faces meeting at a shared edge with a 0.05 mm gap.
# Face 1: square at z=0.
p00 = f.cartesian_point((0.0, 0.0, 0.0), name="f1_p00")
p10 = f.cartesian_point((10.0, 0.0, 0.0), name="f1_p10")
p11 = f.cartesian_point((10.0, 10.0, 0.0), name="f1_p11")
p01 = f.cartesian_point((0.0, 10.0, 0.0), name="f1_p01")
# Face 2: square at z=0.05 (gap on shared edge).
q00 = f.cartesian_point((0.0, 0.0, 0.05), name="f2_p00_gap")
q10 = f.cartesian_point((10.0, 0.0, 0.05), name="f2_p10_gap")

v00 = f.vertex_point(p00, name="v00")
v10 = f.vertex_point(p10, name="v10")
v11 = f.vertex_point(p11, name="v11")
v01 = f.vertex_point(p01, name="v01")
vq00 = f.vertex_point(q00, name="vq00")
vq10 = f.vertex_point(q10, name="vq10")

# Edge from face 1 (shared edge at z=0)
d_x = f.direction((1.0, 0.0, 0.0))
vec_x = f.vector(d_x, 10.0)
shared_e_f1 = f.edge_curve(v00, v10, f.line(p00, vec_x), name="shared_e_f1")

# Edge from face 2 (counterpart at z=0.05 — the gap)
d_x2 = f.direction((1.0, 0.0, 0.0))
vec_x2 = f.vector(d_x2, 10.0)
shared_e_f2 = f.edge_curve(vq00, vq10, f.line(q00, vec_x2), name="shared_e_f2_gap")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('sewing_input',(#{shared_e_f1.eid},#{shared_e_f2.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N052','N052','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
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
