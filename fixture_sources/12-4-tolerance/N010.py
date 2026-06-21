"""N010 — EDGE_CURVE shorter than vertex tolerance (edge covered by vertex discs).

An EDGE_CURVE whose 3D length (5.0E-5 mm) is less than the declared global
distance_accuracy (1.0E-4 mm). The two VERTEX_POINTs at (0,0,0) and (5e-5,0,0)
already have their tolerance balls touching; the edge geometry adds nothing and
trips Boolean/mesh algorithms.

Byte assertions:
  contains(b'1.0E-4')
  count_entity_def(b'VERTEX_POINT') == 2 and count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N010",
    defect=(
        "EDGE_CURVE length 5.0E-5 mm < declared tol 1.0E-4 mm; vertex tolerance "
        "balls already cover the entire edge; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Very short edge: vertices at (0,0,0) and (5e-5, 0, 0) — length 5e-5 < tol 1e-4
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((5.0E-5, 0.0, 0.0), name="p1_5e-5_from_p0")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 5.0E-5)
line = f.line(p0, vec, name="short_line")
edge = f.edge_curve(v0, v1, line, name="tiny_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N010','N010','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','distance_accuracy_covers_edge')"
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
