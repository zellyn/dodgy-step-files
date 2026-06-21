"""N149 — FindCandidates.equidistant_precision_test.

Precision-equality guard absent: candidates differing by 1e-11 inserted as
distinct despite Precision::Confusion (~1e-10) threshold. Tiebreaker logic
bypassed for numerically identical distances.

Geometry: two pairs of edges where each pair is 1e-11 mm apart (below
Precision::Confusion). FindCandidates treats them as distinct candidates.

(No byte assertions; kernel-test-pair — defect requires FindCandidates runtime
invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N149",
    defect=(
        "FindCandidates equidistant_precision: pairs 1e-11mm apart; "
        "Precision::Confusion ~1e-10; tiebreaker logic bypassed; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two edges separated by 1e-11 mm (below Precision::Confusion ~1e-10).
p0a = f.cartesian_point((0.0, 0.0, 0.0), name="p0a")
p1a = f.cartesian_point((1.0, 0.0, 0.0), name="p1a")
p0b = f.cartesian_point((0.0, 1.0e-11, 0.0), name="p0b_sub_confusion")
p1b = f.cartesian_point((1.0, 1.0e-11, 0.0), name="p1b_sub_confusion")

v0a = f.vertex_point(p0a, name="v0a")
v1a = f.vertex_point(p1a, name="v1a")
v0b = f.vertex_point(p0b, name="v0b")
v1b = f.vertex_point(p1b, name="v1b")

d = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(d, 1.0)), name="eA")
eB = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(d, 1.0)), name="eB_sub_confusion")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('equidist_precision',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N149','N149','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-10),#{lu.eid},"
    f"'distance_accuracy_value','confusion_threshold')"
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
