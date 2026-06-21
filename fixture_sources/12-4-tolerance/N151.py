"""N151 — BRepBuilderAPI_Sewing.SameParameterEdge.recursive-tolerance-comparison.

Accept second recursive sewing attempt only if both SameParameter achieved AND
tolerance improved (tolReached_2 < tolReached). Missing check causes
worse-tolerance fallbacks. First attempt tol=0.08 (good), second attempt
tol=0.12 (worse). Without guard, worse result selected.

Geometry: two edges forming a near-closed gap requiring sewing tolerance
comparison across recursive attempts.

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N151",
    defect=(
        "SameParameterEdge recursive-tolerance-comparison: "
        "1st attempt tol=0.08, 2nd tol=0.12; missing monotonicity guard selects worse; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two edges with 0.08 mm gap — first sewing attempt achieves 0.08, second 0.12.
p0a = f.cartesian_point((0.0, 0.0, 0.0), name="p0a")
p1a = f.cartesian_point((5.0, 0.0, 0.0), name="p1a")
p0b = f.cartesian_point((0.0, 0.0, 0.08), name="p0b_gap")
p1b = f.cartesian_point((5.0, 0.0, 0.08), name="p1b_gap")

v0a = f.vertex_point(p0a, name="v0a")
v1a = f.vertex_point(p1a, name="v1a")
v0b = f.vertex_point(p0b, name="v0b")
v1b = f.vertex_point(p1b, name="v1b")

d = f.direction((1.0, 0.0, 0.0))
eA = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(d, 5.0)), name="eA")
eB = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(d, 5.0)), name="eB_gap")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('sewing_recursive',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N151','N151','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(8.0E-2),#{lu.eid},"
    f"'distance_accuracy_value','sewing_gap_first_attempt')"
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
