"""N077 — BRepLib.BuildCurves3d batch-batch failure.

BuildCurves3d called on multiple edges fails atomically when any member fails.
One edge's 3D curve construction failure causes the batch return false, but
successful edges aren't reported. Downstream code assumes all edges failed and
may skip valid geometries or perform redundant repairs.

Geometry: three-edge polyline; edge 1 and 2 have valid LINE curves; edge 3
has no curve_3d (parametric-only edge), triggering failure.

(No byte assertions; kernel-test-pair — defect requires BuildCurves3d batch
invocation with mixed valid/invalid edges.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N077",
    defect=(
        "BuildCurves3d batch: 3 edges; edge3 has no 3D curve; "
        "atomic failure hides edges 1+2 success; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge 1 and 2: valid LINE curves.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="p2")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

d = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d, 1.0)), name="e0_valid")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d, 1.0)), name="e1_valid")

# Edge 3: EDGE_CURVE with no_geometry — uses a degenerate line of zero length
# that causes 3D curve construction to fail on empty parametric context.
p3 = f.cartesian_point((2.0, 0.0, 0.0), name="p3_degen")
p4 = f.cartesian_point((2.0, 0.0, 0.0), name="p4_degen")
v3 = f.vertex_point(p3, name="v3_degen")
v4 = f.vertex_point(p4, name="v4_degen")
# Zero-length line — degenerate, no valid 3D curve can be built.
d_zero = f.direction((1.0, 0.0, 0.0))
# Length 0.0 — degenerate geometry triggering BuildCurves3d failure.
degen_vec = f.vector(d_zero, 0.0)
degen_line = f.line(p3, degen_vec, name="degen_line_zero_length")
e2_fail = f.edge_curve(v3, v4, degen_line, name="e2_no_curve_fails")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('batch_edges',(#{e0.eid},#{e1.eid},#{e2_fail.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N077','N077','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
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
