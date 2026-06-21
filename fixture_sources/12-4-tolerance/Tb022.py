"""Tb022 — Tolerance declared in different units than coordinates.

A file's LENGTH_UNIT in GEOMETRIC_REPRESENTATION_CONTEXT is .MILLI.METRE. (mm).
The UNCERTAINTY_MEASURE_WITH_UNIT uses a separate inline LENGTH_UNIT of .METRE.
(m) with value 1.0E-6. A kernel interpreting in context units (mm) reads "1e-6
mm = 1 nm — hyper-precise". A kernel following the uncertainty's own attached
unit (m) reads "1e-6 m = 1 um = 1.0e-3 mm — 1000x looser". Same file, 1000x
difference in working tolerance.

Byte assertions:
  contains(b'1.0E-6')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb022",
    defect=(
        "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6)) bound to .METRE. unit "
        "while context length unit is .MILLI.METRE.; kernel reading in context mm: 1e-6 mm "
        "hyper-precise; kernel following own unit binding: 1e-6 m = 1 um — 1000x looser; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Simple edge with coordinates in mm.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line, name="e")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")

# Manual PRODUCT chain with unit-binding mismatch.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb022','Tb022','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# Context units: mm.
lu_mm = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Uncertainty's own unit: separate LENGTH_UNIT in .METRE. (m, not mm).
lu_m = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT($,.METRE.))")

# Uncertainty value 1.0E-6 bound to the METRE unit (not the context mm unit).
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu_m.eid},"
    f"'distance_accuracy_value','tolerance_in_metres_not_context_mm')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu_mm.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx_mm_with_metre_uncertainty','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
