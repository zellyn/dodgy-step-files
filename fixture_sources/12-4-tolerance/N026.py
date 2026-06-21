"""N026 — Cross-kernel topology rejection: source-valid, target-invalid by tolerance bookkeeping.

ACIS exports a tolerant edge with tolerance 5.0E-4; Parasolid demands geometric
intersection within 1.0E-6 and would reject it. The file declares two
UNCERTAINTY_MEASURE_WITH_UNIT: the ACIS-source tolerance (5.0E-4) and the
Parasolid-target precision (1.0E-6). What was a single shared vertex in the
source becomes two vertices in the target due to differing snap rules.

Byte assertions:
  count_entity_def(b'UNCERTAINTY_MEASURE_WITH_UNIT') == 2
  contains(b'1.0E-6') and contains(b'5.0E-4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N026",
    defect=(
        "ACIS tolerant edge tol 5.0E-4 vs Parasolid demand 1.0E-6; "
        "2×UNCERTAINTY_MEASURE_WITH_UNIT encode both; shared vertex becomes two "
        "on import; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Tolerant edge: vertices at (0,0,0) and (5e-4, 0, 0) — shared within ACIS tolerance
# but Parasolid would see two separate vertices at 5e-4 separation.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((5.0E-4, 0.0, 0.0), name="p1_within_acis_tol")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_would_split_in_parasolid")

d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 5.0E-4)
line = f.line(p0, vec, name="tolerant_edge_line")
edge = f.edge_curve(v0, v1, line, name="tolerant_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cross_kernel',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N026','N026','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")

# Two UNCERTAINTY_MEASURE_WITH_UNIT: ACIS-source tol and Parasolid-target precision.
unc_acis = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-4),#{lu.eid},"
    f"'distance_accuracy_value','acis_tolerant_edge_tol')"
)
unc_para = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','parasolid_required_precision')"
)

ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc_acis.eid},#{unc_para.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
