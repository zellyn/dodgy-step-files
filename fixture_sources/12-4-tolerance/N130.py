"""N130 — ShapeFix_ShapeTolerance.SetTolerance recursive-double-mutation-shared-vertex.

SetTolerance(WIRE, tmin, tmax, TopAbs_VERTEX) recursively processes each
edge's start/end vertices without tracking shared vertices. When two edges
share a vertex, that vertex's tolerance is overwritten twice (first to tmin,
then to tmax); last write wins, violating determinism.

Geometry: two-edge wire with a shared middle vertex; each edge references
the same vertex object, triggering double mutation.

(No byte assertions; kernel-test-pair — defect requires SetTolerance runtime
invocation on WIRE topology.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N130",
    defect=(
        "SetTolerance recursive-double-mutation-shared-vertex: 2-edge wire; "
        "shared vertex mutated twice (tmin then tmax); last write wins; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two-edge wire with shared middle vertex.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1_shared")
p2 = f.cartesian_point((2.0, 0.0, 0.0), name="p2")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_shared")  # shared by both edges
v2 = f.vertex_point(p2, name="v2")

d = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(d, 1.0)), name="e0")
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(d, 1.0)), name="e1")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('shared_vtx_wire',(#{e0.eid},#{e1.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N130','N130','',(#{prod_ctx.eid}))")
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
