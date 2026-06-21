"""N160 — ComputeTol overflow_error tolerance corruption.

Mismatch between 3D and 2D curves (error 1e10+) accumulated into
SameParameter tolerance; no early abort causes corruption when degenerate
2D curve is paired with 3D line.

Geometry: single edge with extreme parameter-domain mismatch — 3D curve
parameterized over [0, 1e10] while the edge spans 1 mm.

(No byte assertions; kernel-test-pair — defect requires ComputeTol runtime
invocation on mismatched 3D/2D curve pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N160",
    defect=(
        "ComputeTol overflow_error: 3D line [0,1mm]; degenerate 2D params [0,1e10]; "
        "mismatch accumulated into SameParameter tol without early abort; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge with large parameter mismatch: 3D line of 1 mm, but vector magnitude 1e10.
p_start = f.cartesian_point((0.0, 0.0, 0.0), name="p_start")
p_end = f.cartesian_point((1.0, 0.0, 0.0), name="p_end")
v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

d = f.direction((1.0, 0.0, 0.0))
# Enormous magnitude to represent the degenerate 3D/2D domain mismatch.
vec_overflow = f.vector(d, 1.0e10, name="vec_overflow")
ln = f.line(p_start, vec_overflow, name="overflow_line")
edge = f.edge_curve(v_start, v_end, ln, name="overflow_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('overflow_tol',(#{edge.eid}))")

app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N160','N160','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')")
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},'distance_accuracy_value','model_precision')")
ctx = f._emit_raw(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))REPRESENTATION_CONTEXT('ctx','3D'))")
wfr = f._emit_raw(f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})")
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
