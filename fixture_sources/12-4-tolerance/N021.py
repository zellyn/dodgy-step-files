"""N021 — VRML/STEP origin convention mismatch within same producer.

KiCad VRML export places Z=0 at board center; STEP export places Z=0 at board
bottom. For a 1.6 mm board, the two origins differ by 0.8 mm. The STEP file
carries the board model at its true geometric position, but downstream tools
mixing the two formats see components shifted by half-board-thickness.

A single EDGE_CURVE at z=0.8 (board center height) demonstrates the geometry
is registered to the board-bottom origin.

Byte assertions:
  contains(b'1.0E-5')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N021",
    defect=(
        "VRML Z=0 at board center; STEP Z=0 at board bottom; 1.6 mm board means "
        "0.8 mm shift; EDGE_CURVE at z=0.8 encodes board-bottom-origin convention; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Board thickness 1.6 mm; STEP uses board-bottom origin, VRML uses board-center.
# Edge at z=0.8 (board center in STEP coords) representing the mismatch.
p0 = f.cartesian_point((0.0, 0.0, 0.8), name="p0_board_center_z")
p1 = f.cartesian_point((10.0, 0.0, 0.8), name="p1_board_center_z")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec, name="edge_at_board_center")
edge = f.edge_curve(v0, v1, line, name="edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('board_conv',(#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N021','N021','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Byte assertion: 1.0E-5 tolerance.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','kicad_step_precision')"
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
