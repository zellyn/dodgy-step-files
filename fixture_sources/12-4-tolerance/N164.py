"""N164 — tolerance_closure EDGE_LOOP gap exceeds threshold.

Edge loop gap (0.05 mm) accepted despite closure tolerance (0.01 mm).
BRepBuilderAPI_Sewing skips gap validation. Tests loop closure enforcement.

Geometry: three edges forming an almost-closed triangle with a 0.05 mm gap
between the last edge's end vertex and the first edge's start vertex.

(No byte assertions; kernel-test-pair — defect requires BRepBuilderAPI_Sewing
runtime invocation with closure tolerance 0.01 mm.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N164",
    defect=(
        "tolerance_closure EDGE_LOOP gap: triangle with 0.05mm gap; "
        "closure tol=0.01; sewing skips gap validation; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Almost-closed triangle: (0,0,0)→(5,0,0)→(2.5,5,0)→(0.05,0,0) gap.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0_loop_start")
p1 = f.cartesian_point((5.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((2.5, 5.0, 0.0), name="p2")
p3 = f.cartesian_point((0.05, 0.0, 0.0), name="p3_gap")  # 0.05 mm from p0

v0 = f.vertex_point(p0, name="v0_loop_start")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")
v3 = f.vertex_point(p3, name="v3_gap")  # not closed

d01 = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d01, 5.0)), name="e0")
d12 = f.direction((-0.5, 1.0, 0.0))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d12, 5.0)), name="e1")
d23 = f.direction((-0.489, -1.0, 0.0))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(d23, 5.0)), name="e2_gap")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('unclosed_loop',(#{e0.eid},#{e1.eid},#{e2.eid}))"
)

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N164','N164','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Gap 0.05 mm; closure tolerance 0.01 mm.
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-2),#{lu.eid},'distance_accuracy_value','loop_closure_gap')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
