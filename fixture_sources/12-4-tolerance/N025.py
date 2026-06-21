"""N025 — Coincident-but-not-shared vertices/edges (cross-translator round-off).

Two adjacent ADVANCED_FACEs each instantiate their own VERTEX_POINTs for the
shared corner, with coordinates agreeing to 1.0E-4 but stored as 4 distinct
entities. Two EDGE_CURVEs represent the shared edges: one from each face but
referencing separate (near-coincident) vertices. A "crack" rather than a "gap"
because geometric distance is near-zero yet topology is broken.

Byte assertions:
  count_entity_def(b'VERTEX_POINT') == 4
  count_entity_def(b'EDGE_CURVE') == 2
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N025",
    defect=(
        "4 VERTEX_POINTs for what should be 2 shared corners; 2 EDGE_CURVEs "
        "with near-coincident (1.0E-4 mm jitter) separate vertices; "
        "topology crack despite near-zero distance; GEOMETRIC_CURVE_SET — OCC empty"
    ),
)

# Face 1 edge: vertices at exact positions
p_a0 = f.cartesian_point((0.0, 0.0, 0.0), name="face1_v0")
p_a1 = f.cartesian_point((10.0, 0.0, 0.0), name="face1_v1")
# Face 2 edge: vertices at positions with 1e-4 mm jitter (translator round-off)
p_b0 = f.cartesian_point((1.0E-4, 0.0, 0.0), name="face2_v0_jitter")
p_b1 = f.cartesian_point((10.0 + 1.0E-4, 0.0, 0.0), name="face2_v1_jitter")

va0 = f.vertex_point(p_a0, name="va0_face1")
va1 = f.vertex_point(p_a1, name="va1_face1")
vb0 = f.vertex_point(p_b0, name="vb0_face2_jitter")
vb1 = f.vertex_point(p_b1, name="vb1_face2_jitter")

# Face 1 edge
da = f.direction((1.0, 0.0, 0.0))
veca = f.vector(da, 10.0)
la = f.line(p_a0, veca)
eA = f.edge_curve(va0, va1, la, name="eA_face1")

# Face 2 edge (should be the same edge but is separate due to jitter)
db = f.direction((1.0, 0.0, 0.0))
vecb = f.vector(db, 10.0)
lb = f.line(p_b0, vecb)
eB = f.edge_curve(vb0, vb1, lb, name="eB_face2_jitter")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cracked',(#{eA.eid},#{eB.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N025','N025','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared precision 1.0E-7 — byte assertion; jitter 1.0E-4 >> this tol.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','source_precision')"
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
