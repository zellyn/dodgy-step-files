"""N009 — Vertex 3D point lies far from incident-edge curve endpoints.

A vertex's stored 3D point is displaced 0.001 mm from the curve endpoint:
EDGE_CURVE with LINE from (0,0,0) to (1,0,0), but start VERTEX_POINT at
(0, 0.001, 0). Declared tolerance is 1.0E-4; the 1.0E-3 mm displacement
exceeds it 10×. The vertex tolerance disc would need to span the displacement
to reconcile with the edge curve, violating the tolerance hierarchy.

Byte assertions:
  contains(b'1.0E-4')
  count_entity_def(b'VERTEX_POINT') == 2 and count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N009",
    defect=(
        "VERTEX_POINT at (0,0.001,0) displaced 1.0E-3 mm from LINE start (0,0,0); "
        "declared tol 1.0E-4; displacement 10x tol; vertex disc spans whole feature; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# EDGE_CURVE: LINE (0,0,0) -> (1,0,0)
p_line_start = f.cartesian_point((0.0, 0.0, 0.0), name="line_start")
p_line_end = f.cartesian_point((1.0, 0.0, 0.0), name="line_end")
# Start vertex displaced 1e-3 in Y from the actual curve start.
p_vtx_start = f.cartesian_point((0.0, 0.001, 0.0), name="vtx_start_far")

v_start = f.vertex_point(p_vtx_start, name="v_start_displaced")
v_end = f.vertex_point(p_line_end, name="v_end")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
line = f.line(p_line_start, vec, name="line")
edge = f.edge_curve(v_start, v_end, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N009','N009','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-4 — byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-4),#{lu.eid},"
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
