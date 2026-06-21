"""Tb013 — Coordinate at 1e-300 tests as "near zero" only under denormalized math.

A CARTESIAN_POINT has coordinate (1.0E-300, 0, 0) — a denormalized double.
Receiver A: |x| < 1e-7 -> "near zero". Receiver B with flush-to-zero math
treats 1e-300 as exactly 0. Receiver C without flush-to-zero keeps the value
alive and trips on 1.0/(1e-300) = 1e+300 overflow during normal-vector or
transform computation. Behavior depends on host floating-point environment.

Byte assertions:
  contains(b'1.0E-7')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb013",
    defect=(
        "CARTESIAN_POINT at (1.0E-300,0,0) — denormalized double; "
        "flush-to-zero math sees 0; exact math risks 1/1e-300=1e+300 overflow; "
        "declared 1.0E-7; one EDGE_CURVE; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Vertex at denormalized coordinate — emitted raw to preserve 1.0E-300 exactly
# (the builder would snap values < 1e-14 to 0.0).
p_denorm = f._emit_raw("CARTESIAN_POINT('p_denorm',(1.0E-300,0.0,0.0))")
p_normal = f.cartesian_point((1.0, 0.0, 0.0), name="p_normal")

v_denorm = f._emit_raw(f"VERTEX_POINT('v_denorm_x',#{p_denorm.eid})")
v_normal = f.vertex_point(p_normal, name="v_normal")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
line = f._emit_raw(f"LINE('',#{p_denorm.eid},#{vec.eid})")
edge = f._emit_raw(
    f"EDGE_CURVE('e_from_denorm_to_normal',#{v_denorm.eid},#{v_normal.eid},#{line.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cs',(#{edge.eid}))")


# Manual PRODUCT chain with declared tolerance 1.0E-7.
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb013','Tb013','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','tol_far_above_denormal')"
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
