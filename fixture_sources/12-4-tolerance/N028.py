"""N028 — GEOMETRIC_REPRESENTATION_CONTEXT missing LENGTH_UNIT (only angle units).

When the STEP model's GEOMETRIC_REPRESENTATION_CONTEXT carries no LENGTH_UNIT
in its GLOBAL_UNIT_ASSIGNED_CONTEXT — only PLANE_ANGLE_UNIT and SOLID_ANGLE_UNIT
are present, and no UNCERTAINTY_MEASURE_WITH_UNIT is attached — the user-
configured xstep.cascade.unit is silently ignored. The reader uses an internal
default and the model arrives at unexpected scale.

Byte assertions:
  not_contains(b'LENGTH_UNIT()')
  contains(b'PLANE_ANGLE_UNIT') and contains(b'SOLID_ANGLE_UNIT')
  not_contains(b'UNCERTAINTY_MEASURE_WITH_UNIT(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N028",
    defect=(
        "GEOMETRIC_REPRESENTATION_CONTEXT with only PLANE_ANGLE_UNIT + "
        "SOLID_ANGLE_UNIT; no LENGTH_UNIT, no UNCERTAINTY_MEASURE_WITH_UNIT; "
        "cascade.unit ignored; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Simple edge for geometry.
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
product = f._emit_raw(f"PRODUCT('N028','N028','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# Only angle units — no LENGTH_UNIT, no UNCERTAINTY_MEASURE_WITH_UNIT.
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Context with only angle units and no uncertainty leaf.
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
