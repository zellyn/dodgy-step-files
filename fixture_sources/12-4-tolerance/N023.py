"""N023 — EDGE_CURVE based on LINE displaced from true vertex position.

An EDGE_CURVE's underlying LINE is parallel-displaced from the line that
actually passes through both vertex points. Direction is correct; position is
offset by 0.001 mm. VERTEX_POINT A at (0,0,0), B at (10,0,0), but the LINE
starts at (0, 0.001, 0) — a 1.0E-3 mm offset in Y.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 1
  count_entity_def(b'LINE') == 1
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N023",
    defect=(
        "EDGE_CURVE LINE starts at (0,0.001,0) not (0,0,0); vertex A at (0,0,0), "
        "B at (10,0,0); LINE direction correct but position offset 1.0E-3 mm in Y; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Vertices at correct positions.
p_vtx_a = f.cartesian_point((0.0, 0.0, 0.0), name="vtx_a")
p_vtx_b = f.cartesian_point((10.0, 0.0, 0.0), name="vtx_b")
v_a = f.vertex_point(p_vtx_a, name="v_a")
v_b = f.vertex_point(p_vtx_b, name="v_b")

# LINE starts at displaced origin (0, 0.001, 0) — the defect.
p_line_start = f.cartesian_point((0.0, 0.001, 0.0), name="line_start_displaced")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p_line_start, vec, name="displaced_line")
edge = f.edge_curve(v_a, v_b, line, name="edge_displaced_line")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N023','N023','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-6 — byte assertion.
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
