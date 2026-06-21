"""Tb018 — UNCERTAINTY value of exactly zero — no fuzzy compare.

UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0)) declares zero tolerance.
A receiver that uses the declared value verbatim performs exact-equality
comparisons; any sub-bit drift is a "real" defect. A receiver that floors
the working tolerance at Precision::Confusion (~1e-7) silently substitutes
a non-zero value and behaves identically to a normal file. The zero
declaration is a producer's request for exact arithmetic that may or may
not be honoured.

Byte assertions:
  matches(rb'LENGTH_MEASURE\(\s*0\\.0\)')
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb018",
    defect=(
        "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0)) — zero tolerance; "
        "exact arithmetic requested; receiver silently flooring to 1e-7 violates contract; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Simple edge so context is exercised.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="e")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with zero declared tolerance.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb018','Tb018','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Zero tolerance — emit raw to preserve LENGTH_MEASURE(0.0) exactly.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0),#{lu.eid},"
    f"'distance_accuracy_value','exact_arithmetic_requested')"
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
