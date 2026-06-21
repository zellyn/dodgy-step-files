"""N126 — ShapeAnalysis_ShapeTolerance.InTolerance vertex-filtering-inverted.

InTolerance filters vertices by tolerance range but uses inverted comparison
(tol >= valmax) vs FACE/EDGE which uses (tol <= valmax). Query for vertices
with tolerance in [0.001, 0.002] returns only those >= 0.002, reversing the
range semantics.

Geometry: three edges with vertex tolerances at 0.0015 (in-range), 0.005
(out-of-range above), and 0.0008 (out-of-range below). InTolerance([0.001,
0.002]) should return only the 0.0015 vertex; buggy code returns only 0.005.

(No byte assertions; kernel-test-pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N126",
    defect=(
        "InTolerance vertex-filtering-inverted: 3 edges; vertex tols 0.0015/0.005/0.0008; "
        "query [0.001,0.002] returns 0.005 vertex (>= valmax) not 0.0015 (in-range); "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Three separate edges, each with a distinct vertex tolerance.
pts = [
    (0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0), (1.0, 1.0, 0.0),
    (0.0, 2.0, 0.0), (1.0, 2.0, 0.0),
]
ps = [f.cartesian_point(p) for p in pts]
vs = [f.vertex_point(p) for p in ps]
d = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(vs[0], vs[1], f.line(ps[0], f.vector(d, 1.0)), name="e0_inrange")
e1 = f.edge_curve(vs[2], vs[3], f.line(ps[2], f.vector(d, 1.0)), name="e1_above")
e2 = f.edge_curve(vs[4], vs[5], f.line(ps[4], f.vector(d, 1.0)), name="e2_below")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('vertex_filter',(#{e0.eid},#{e1.eid},#{e2.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N126','N126','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Three tolerance levels: in-range (0.0015), above (0.005), below (0.0008).
unc1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.5E-3),#{lu.eid},"
    f"'distance_accuracy_value','tol_inrange')"
)
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','tol_above_range')"
)
unc3 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(8.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','tol_below_range')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc1.eid},#{unc2.eid},#{unc3.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
