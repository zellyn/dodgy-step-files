"""N147 — FindCandidates.acceptance_criteria_composite_filter.

Composite AND condition omitted: candidates exceeding myTolerance (0.15 > 0.1)
with undersized coverage falsely accepted. Full condition (aMaxDist<=tol AND
arrLen>minTol) required but first clause alone applied.

Geometry: two edges separated by 0.15 mm — beyond the 0.1 mm sewing tolerance;
the first-clause-only filter accepts them as candidates when the AND condition
would reject them.

(No byte assertions; kernel-test-pair — defect requires FindCandidates runtime
invocation with myTolerance=0.1.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N147",
    defect=(
        "FindCandidates composite_filter: 2 edges 0.15mm apart; "
        "myTolerance=0.1; first clause only accepts (0.15 > 0.1 not checked); "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two parallel edges 0.15 mm apart.
p0_a = f.cartesian_point((0.0, 0.0, 0.0), name="p0a")
p1_a = f.cartesian_point((1.0, 0.0, 0.0), name="p1a")
p0_b = f.cartesian_point((0.0, 0.15, 0.0), name="p0b")
p1_b = f.cartesian_point((1.0, 0.15, 0.0), name="p1b")

v0a = f.vertex_point(p0_a, name="v0a")
v1a = f.vertex_point(p1_a, name="v1a")
v0b = f.vertex_point(p0_b, name="v0b")
v1b = f.vertex_point(p1_b, name="v1b")

d = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(v0a, v1a, f.line(p0_a, f.vector(d, 1.0)), name="eA")
eB = f.edge_curve(v0b, v1b, f.line(p0_b, f.vector(d, 1.0)), name="eB_offset")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('candidates',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N147','N147','',(#{prod_ctx.eid}))")
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
