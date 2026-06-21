"""N157 — distance_tolerance_filter_second_pass bypass.

BRepBuilderAPI_Sewing omits distance threshold check in second pass;
out-of-tolerance candidates (tabDst=0.8 exceeding myTolerance=0.1) included
in comparison via bypassed filter.

Geometry: two edges 0.8 mm apart — distance exceeds sewing tolerance 0.1 mm;
second-pass filter bypass allows out-of-tolerance candidate to proceed.

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N157",
    defect=(
        "distance_tolerance_filter_second_pass bypass: 2 edges 0.8mm apart; "
        "myTolerance=0.1; second-pass filter absent; out-of-tol candidate accepted; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two parallel edges 0.8 mm apart.
p0a = f.cartesian_point((0.0, 0.0, 0.0), name="p0a")
p1a = f.cartesian_point((1.0, 0.0, 0.0), name="p1a")
p0b = f.cartesian_point((0.0, 0.8, 0.0), name="p0b_far")
p1b = f.cartesian_point((1.0, 0.8, 0.0), name="p1b_far")

v0a = f.vertex_point(p0a, name="v0a")
v1a = f.vertex_point(p1a, name="v1a")
v0b = f.vertex_point(p0b, name="v0b")
v1b = f.vertex_point(p1b, name="v1b")

d = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(d, 1.0)), name="eA")
eB = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(d, 1.0)), name="eB_far")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('dist_filter_bypass',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N157','N157','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-1),#{lu.eid},"
    f"'distance_accuracy_value','sewing_tol')"
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
