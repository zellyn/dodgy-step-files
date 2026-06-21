"""N049 — Reading structurally valid STEP produces invalid TopoDS_Shape.

A STEP file imports without diagnostic but BRepCheck_Analyzer returns
BRepCheck_InvalidPointOnCurve. The EDGE_CURVE end-vertex CARTESIAN_POINT
lies 2e-6 mm from the curve at its parametric endpoint; the receiver's edge
tolerance is 1e-7. The file is structurally legal but geometrically marginal.

Byte assertions:
  contains(b'EDGE_CURVE')
  contains(b'VERTEX_POINT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N049",
    defect=(
        "EDGE_CURVE end-VERTEX_POINT displaced 2.0E-6 mm from curve endpoint; "
        "receiver edge tol 1.0E-7; structurally valid but BRepCheck fails; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# LINE from (0,0,0) to (10,0,0). End vertex at (10, 2e-6, 0) — displaced 2e-6.
p_curve_start = f.cartesian_point((0.0, 0.0, 0.0), name="curve_start")
p_curve_end = f.cartesian_point((10.0, 0.0, 0.0), name="curve_end")
# End vertex displaced 2e-6 off-curve.
p_vtx_end = f.cartesian_point((10.0, 2.0E-6, 0.0), name="vtx_end_off_curve")

v_start = f.vertex_point(p_curve_start, name="v_start")
v_end = f.vertex_point(p_vtx_end, name="v_end_displaced")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p_curve_start, vec, name="line")
edge = f.edge_curve(v_start, v_end, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N049','N049','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Receiver edge tolerance 1.0E-7; vertex displacement 2.0E-6 >> this.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','receiver_edge_tolerance')"
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
