"""N080 — ShapeFix_ShapeTolerance.LimitTolerance recursive-only-vertex.

LimitTolerance(shape, tmin, tmax, TopAbs_VERTEX) with shape_type=VERTEX should
descend through faces/edges to reach vertices, apply limits to vertices only,
then skip modifying faces/edges. Instead, recursion halts at the first face,
leaving vertices in that face and all other faces untouched.

Geometry: two edges forming a right-angle junction with vertices at
(0,0,0), (5,0,0), (5,5,0); vertices have loose tolerances 2.0e-5 and 3.0e-5.

(No byte assertions; kernel-test-pair — defect requires LimitTolerance runtime
invocation with TopAbs_VERTEX type selector.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N080",
    defect=(
        "LimitTolerance recursive-only-vertex: 2-edge L-shape; vertices at "
        "(0,0,0),(5,0,0),(5,5,0); loose vertex tol 2e-5/3e-5; "
        "recursion halts at face, leaves vertices un-limited; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# L-shaped two-edge wire.
pO = f.cartesian_point((0.0, 0.0, 0.0), name="pO")
pX = f.cartesian_point((5.0, 0.0, 0.0), name="pX")
pY = f.cartesian_point((5.0, 5.0, 0.0), name="pY")
vO = f.vertex_point(pO, name="vO")
vX = f.vertex_point(pX, name="vX")
vY = f.vertex_point(pY, name="vY")

dX = f.direction((1.0, 0.0, 0.0))
eOX = f.edge_curve(vO, vX, f.line(pO, f.vector(dX, 5.0)), name="eOX")
dY = f.direction((0.0, 1.0, 0.0))
eXY = f.edge_curve(vX, vY, f.line(pX, f.vector(dY, 5.0)), name="eXY")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('L_wire',(#{eOX.eid},#{eXY.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N080','N080','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Vertex tolerances: 2.0e-5 and 3.0e-5 (file context uses worst-case).
unc_v1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol_1')"
)
unc_v2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(3.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol_2')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_v1.eid},#{unc_v2.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
