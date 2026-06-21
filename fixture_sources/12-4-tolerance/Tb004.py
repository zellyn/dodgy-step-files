"""Tb004 — Vertex-edge-face hierarchy holds in mm but inverts when scaled to inches.

Variant of Tb003 with a non-decimal scale factor. Three UNCERTAINTY values at
1.000e-6, 1.001e-6, 1.002e-6 mm. The ordering is preserved by 1e-9 margins.
After mm->inch conversion (factor 25.4), values become 2.54e-5, 2.5425e-5,
2.5450e-5; a kernel that round-trips any field through float32 (~7 sig digits)
collapses all three to ~2.54e-5, violating the strict ordering. Hierarchy holds
at one precision policy and fails at another.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 3
  contains(b'1.000E-6') and contains(b'1.001E-6') and contains(b'1.002E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb004",
    defect=(
        "three UNCERTAINTY_MEASURE_WITH_UNIT at 1.000E-6/1.001E-6/1.002E-6 mm; "
        "hierarchy barely holds (1e-9 margin); mm->inch conversion (factor 25.4) "
        "plus float32 round-trip collapses all three, inverting strict ordering; "
        "OCC yields empty"
    ),
)

# Minimal wire geometry.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec)
edge = f.edge_curve(v0, v1, line)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('wire_set',(#{edge.eid}))")

# Manual PRODUCT chain.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb004','Tb004','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# ULP-margin hierarchy: 1.000E-6 < 1.001E-6 < 1.002E-6 (4-digit precision).
unc_v = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.000E-6),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol_at_ULP_floor')"
)
unc_e = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.001E-6),#{lu.eid},"
    f"'distance_accuracy_value','edge_tol_one_ULP_higher')"
)
unc_f = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.002E-6),#{lu.eid},"
    f"'distance_accuracy_value','face_tol_two_ULP_higher')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_v.eid},#{unc_e.eid},#{unc_f.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx_mm','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
