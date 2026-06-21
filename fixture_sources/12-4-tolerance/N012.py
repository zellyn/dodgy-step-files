"""N012 — Setting face tolerance to tiny value (1.0E-9) then ShapeFix produces vertex/vertex intersections.

Programmatically reducing a face tolerance to 1.0E-9 (below the actual edge gap
of 1.0E-5), then running ShapeFix, makes the algorithm interpret coincident
vertex tolerance balls as separate vertices — producing vertex/vertex intersection
diagnostics. Two VERTEX_POINTs at (0,0,0) and (0,1e-5,0) are within the normal
tolerance but appear separate at 1.0E-9.

Byte assertions:
  contains(b'1.0E-9')
  count_entity_def(b'VERTEX_POINT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N012",
    defect=(
        "face tol set to 1.0E-9 below actual gap 1.0E-5; two VERTEX_POINTs 1.0E-5 "
        "apart appear separate at sub-resolution tol; GEOMETRIC_CURVE_SET — OCC empty"
    ),
)

# Two vertices 1e-5 mm apart; at tolerance 1e-9 they appear separate.
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((0.0, 1.0E-5, 0.0), name="p1_1e-5_gap")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_near_coincident")

# Short edge connecting them so we have meaningful geometry.
d = f.direction((0.0, 1.0, 0.0))
vec = f.vector(d, 1.0E-5)
line = f.line(p0, vec, name="short_edge_line")
edge = f.edge_curve(v0, v1, line, name="edge_near_coincident")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('edges',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N012','N012','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Face tolerance set to 1.0E-9 — the triggering value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-9),#{lu.eid},"
    f"'distance_accuracy_value','face_tol_set_below_gap')"
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
