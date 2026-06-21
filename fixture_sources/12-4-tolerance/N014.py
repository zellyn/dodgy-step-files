"""N014 — Spurious tiny EDGE_CURVE that should have collapsed: vertex separation below declared tolerance.

An intersection edge persists because the topological filter treats nearly-
coincident vertices as distinct. Both endpoints lie within tolerance of one
corrected position: vertices at (2e-8,0,0) and (-2e-8,0,0) — length 4e-8 mm —
with declared distance_accuracy 1.0E-7 mm. The two vertices are several times
closer than the tolerance and the edge should collapse to a single vertex.

Byte assertions:
  contains(b'1.0E-7')
  count_entity_def(b'VERTEX_POINT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N014",
    defect=(
        "EDGE_CURVE between vtx at (2e-8,0,0) and (-2e-8,0,0); length 4.0E-8 mm "
        "< declared tol 1.0E-7; both vertices within tol of one corrected position; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Two vertices nearly coincident; should collapse to one.
p0 = f.cartesian_point((2.0E-8, 0.0, 0.0), name="vtx_pos")
p1 = f.cartesian_point((-2.0E-8, 0.0, 0.0), name="vtx_neg")
v0 = f.vertex_point(p0, name="v_pos")
v1 = f.vertex_point(p1, name="v_neg")

# Tiny edge between them: length 4e-8 < tol 1e-7.
d = f.direction((-1.0, 0.0, 0.0))
vec = f.vector(d, 4.0E-8)
line = f.line(p0, vec, name="tiny_line")
edge = f.edge_curve(v0, v1, line, name="should_have_collapsed")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N014','N014','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-7 — byte assertion; edge length 4e-8 < tol.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','tol_covers_edge')"
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
