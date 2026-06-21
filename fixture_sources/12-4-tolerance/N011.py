"""N011 — Seam edge inserted inside existing vertex tolerance ball (zero-length edge).

A periodic CYLINDRICAL_SURFACE needs a seam edge, but the seam falls entirely
inside an existing vertex tolerance ball (1.0E-3 mm). Inserting the seam anyway
creates a real EDGE_CURVE of essentially zero length whose endpoints are
tolerance-equivalent — violating the invariant that no real edge fits inside a
vertex tolerance disc.

Byte assertions:
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'1.0E-3')
  count_entity_def(b'EDGE_CURVE') == 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N011",
    defect=(
        "seam EDGE_CURVE on CYLINDRICAL_SURFACE: length 5.0E-5 mm inside vertex "
        "tol ball 1.0E-3 mm; seam insertion creates zero-length edge; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylinder: radius 1.0, axis along Z.
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cyl_orig")
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},1.0)")

# Seam "edge": nearly zero length — both vertices within the 1.0E-3 tolerance ball.
# Vertices at (1,0,0) and (1,0,5e-5) — 5e-5 mm apart (inside 1e-3 ball).
p_seam_bot = f.cartesian_point((1.0, 0.0, 0.0), name="p_seam_bot")
p_seam_top = f.cartesian_point((1.0, 0.0, 5.0E-5), name="p_seam_top_inside_tol")
v_bot = f.vertex_point(p_seam_bot, name="v_bot")
v_top = f.vertex_point(p_seam_top, name="v_top_inside_tol")

d = f.direction((0.0, 0.0, 1.0))
vec = f.vector(d, 5.0E-5)
seam_line = f.line(p_seam_bot, vec, name="seam_line_zero_length")
seam_edge = f.edge_curve(v_bot, v_top, seam_line, name="seam_edge_inside_tol")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('seam_set',(#{seam_edge.eid},#{cyl.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N011','N011','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Vertex tolerance ball 1.0E-3 — byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','vertex_tol_ball_covers_seam')"
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
