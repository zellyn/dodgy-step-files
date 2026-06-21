"""Tb019 — UNCERTAINTY value of 1.0E-30 — below any sane working precision.

UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-30)) declares a tolerance
below any reasonable kernel's working precision. A kernel respecting the value
tries to compare features at 1e-30 and rejects everything as having gaps. A
kernel flooring at Precision::Confusion (~1e-7) silently substitutes a non-zero
working tolerance — producer and receiver silently disagree about precision.

Byte assertions:
  contains(b'1.0E-30')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb019",
    defect=(
        "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-30)) — sub-machine-precision; "
        "kernel flooring to 1.0E-7 silently violates declared tolerance; "
        "one EDGE_CURVE; GEOMETRIC_CURVE_SET — OCC yields empty"
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

# Manual PRODUCT chain with 1.0E-30 declared tolerance.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb019','Tb019','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# 1.0E-30 — emit raw to preserve exact byte sequence.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-30),#{lu.eid},"
    f"'distance_accuracy_value','sub_machine_precision_request')"
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
