"""N018 — GEOMETRIC_REPRESENTATION_CONTEXT missing GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT leaf.

When a STEP file's GEOMETRIC_REPRESENTATION_CONTEXT lacks the
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT leaf — carrying only
GLOBAL_UNIT_ASSIGNED_CONTEXT with no UNCERTAINTY_MEASURE_WITH_UNIT — OCCT
silently falls back to the read.precision.val parameter. No diagnostic is
emitted; any model read under this path shares whatever precision the user
configured.

Byte assertions:
  not_contains(b'UNCERTAINTY_MEASURE_WITH_UNIT(')
  contains(b'GEOMETRIC_REPRESENTATION_CONTEXT')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N018",
    defect=(
        "GEOMETRIC_REPRESENTATION_CONTEXT with GLOBAL_UNIT_ASSIGNED_CONTEXT only; "
        "no UNCERTAINTY_MEASURE_WITH_UNIT; OCCT silently falls back to "
        "read.precision.val; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Single edge.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((10.0, 0.0, 0.0), name="p1")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N018','N018','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Context WITHOUT GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT — just units.
# This is the defect: no UNCERTAINTY_MEASURE_WITH_UNIT at all.
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
