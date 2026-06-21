"""Tb021 — Multiple UNCERTAINTY entries with conflicting values, no labels.

A GEOMETRIC_REPRESENTATION_CONTEXT lists three UNCERTAINTY_MEASURE_WITH_UNIT
entries with values 1.0e-3, 1.0e-6, 1.0e-9 and no distinguishing name field.
Receiver-A picks min (1.0e-9 — strict). Receiver-B picks max (1.0e-3 — lax).
Receiver-C picks first (1.0e-3). Receiver-D picks last (1.0e-9). Same file,
four different working tolerances depending on receiver policy.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'1.0E-3') and contains(b'1.0E-6') and contains(b'1.0E-9')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb021",
    defect=(
        "three unlabelled UNCERTAINTY_MEASURE_WITH_UNIT (1.0E-3/1.0E-6/1.0E-9); "
        "min/max/first/last policies give four different working tolerances; "
        "ambiguous which applies; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Simple edge.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="e")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with three unlabelled uncertainty values.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb021','Tb021','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Three unlabelled uncertainties spanning 6 orders of magnitude.
unc1 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},'','')"
)
unc2 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},'','')"
)
unc3 = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-9),#{lu.eid},'','')"
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
