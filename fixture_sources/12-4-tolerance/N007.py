"""N007 — Vertex tolerance bump factor hard-coded 1.000001* on disagreement.

When the imported edge's 3D curve and its endpoint vertices disagree beyond a
precision threshold, a translator bumps the vertex tolerance by a constant
multiplier (slightly above 1.0x) of the deviation, just enough to make the
edge pass invariants. The VERTEX_POINT at (0, 0.001, 0) lies 1.0E-3 mm from
the LINE endpoint at (0,0,0); declared model uncertainty is 1.0E-6.

Byte assertions:
  contains(b'1.0E-6') and contains(b'EDGE_CURVE')
  count_entity_def(b'VERTEX_POINT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N007",
    defect=(
        "vertex at (0,0.001,0) displaced 1.0E-3 mm from LINE endpoint at (0,0,0); "
        "translator bumped vertex tol by 1.000001x; model uncertainty 1.0E-6; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Edge: LINE from (0,0,0) to (10,0,0)
# Start VERTEX_POINT at (0, 0.001, 0) — displaced 1e-3 from curve start.
p_curve_start = f.cartesian_point((0.0, 0.0, 0.0), name="curve_start")
p_curve_end = f.cartesian_point((10.0, 0.0, 0.0), name="curve_end")
p_vtx_displaced = f.cartesian_point((0.0, 0.001, 0.0), name="vtx_displaced_1e-3")

v_start = f.vertex_point(p_vtx_displaced, name="v_start_displaced")
v_end = f.vertex_point(p_curve_end, name="v_end")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p_curve_start, vec, name="line")
edge = f.edge_curve(v_start, v_end, line, name="edge_vtx_displaced")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N007','N007','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Model uncertainty 1.0E-6 — byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
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
