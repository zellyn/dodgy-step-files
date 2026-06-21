"""N013 — Boolean cascade vertex deviation (independently computed pairwise intersections).

When three surfaces meet at one mathematical vertex, OCCT computes each pairwise
edge-edge intersection independently. Floating-point error makes the three
candidate vertex coordinates disagree by 1.0E-9, so the boolean output emits
three almost-coincident VERTEX_POINTs and three short EDGE_CURVEs in place of
one shared vertex.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 3
  count_entity_def(b'VERTEX_POINT') == 3
  contains(b'1.0E-9')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N013",
    defect=(
        "boolean cascade: three pairwise intersections produce three near-coincident "
        "VERTEX_POINTs offset by ~1.0E-9; three EDGE_CURVEs instead of one vertex; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Three vertices that should be one shared vertex but diverge by ~1e-9.
# A correct vertex is at (0,0,0); three computed candidates jitter around it.
eps = 1.0E-9
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="vtx_A")
p1 = f.cartesian_point((eps, 0.0, 0.0), name="vtx_B_jitter_x")
p2 = f.cartesian_point((0.0, eps, 0.0), name="vtx_C_jitter_y")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

# Three short edges forming a tiny spurious triangle.
# Edge A-B
d_ab = f.direction((1.0, 0.0, 0.0))
vec_ab = f.vector(d_ab, eps)
line_ab = f.line(p0, vec_ab, name="line_AB")
eAB = f.edge_curve(v0, v1, line_ab, name="eAB")

# Edge B-C
d_bc = f.direction((-1.0, 1.0, 0.0))
vec_bc = f.vector(d_bc, eps)
line_bc = f.line(p1, vec_bc, name="line_BC")
eBC = f.edge_curve(v1, v2, line_bc, name="eBC")

# Edge C-A
d_ca = f.direction((0.0, -1.0, 0.0))
vec_ca = f.vector(d_ca, eps)
line_ca = f.line(p2, vec_ca, name="line_CA")
eCA = f.edge_curve(v2, v0, line_ca, name="eCA")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cascade',(#{eAB.eid},#{eBC.eid},#{eCA.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N013','N013','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance at jitter scale 1.0E-9 — byte assertion.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-9),#{lu.eid},"
    f"'distance_accuracy_value','boolean_cascade_jitter')"
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
