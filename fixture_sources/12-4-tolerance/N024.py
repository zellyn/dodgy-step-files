"""N024 — EDGE_CURVE 3D LINE stale relative to translated host PLANE (rebuild-edge case).

After face translation, an edge's 3D curve no longer matches the geometric
intersection of its two host PLANEs. Two PLANE instances exist — original at
z=0 and edited at z=0.01 — but the EDGE_CURVE still references a 3D LINE at
z=0 (the pre-edit plane position). The edge survives as topology but its curve
is stale, leading to large tolerances or visible cracks.

Byte assertions:
  count_entity_def(b'PLANE') == 2
  count_entity_def(b'EDGE_CURVE') == 1
  contains(b'1.0E-5')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N024",
    defect=(
        "EDGE_CURVE 3D LINE at z=0 (pre-edit); one PLANE at z=0, one translated "
        "to z=0.01; edge curve stale — doesn't match the new plane intersection; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Plane 1: original at z=0 (XY plane, normal +Z)
p1_orig = f.cartesian_point((0.0, 0.0, 0.0), name="plane1_orig")
p1_zdir = f.direction((0.0, 0.0, 1.0))
p1_xdir = f.direction((1.0, 0.0, 0.0))
plc1 = f.axis2_placement_3d(p1_orig, p1_zdir, p1_xdir)
plane1 = f.plane(plc1, name="plane_original_z0")

# Plane 2: translated to z=0.01 (after face-translate edit)
p2_orig = f.cartesian_point((0.0, 0.0, 0.01), name="plane2_orig_z_0.01")
p2_zdir = f.direction((0.0, 0.0, 1.0))
p2_xdir = f.direction((1.0, 0.0, 0.0))
plc2 = f.axis2_placement_3d(p2_orig, p2_zdir, p2_xdir)
plane2 = f.plane(plc2, name="plane_translated_z_0.01")

# Stale EDGE_CURVE: 3D LINE at z=0 — should be at z=0.01 after the edit.
p_line_start = f.cartesian_point((0.0, 0.0, 0.0), name="stale_line_start")
p_line_end = f.cartesian_point((10.0, 0.0, 0.0), name="stale_line_end")
v_start = f.vertex_point(p_line_start, name="v_start")
v_end = f.vertex_point(p_line_end, name="v_end")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
stale_line = f.line(p_line_start, vec, name="stale_line_at_z0")
edge = f.edge_curve(v_start, v_end, stale_line, name="stale_edge")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('planes_edge',(#{plane1.eid},#{plane2.eid},#{edge.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N024','N024','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-5 — byte assertion.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','rebuild_edge_threshold')"
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
