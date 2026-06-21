"""N005 — Splitting a closed periodic face leaves new edges with reversed pcurve vs 3D curve.

Splitting a full CYLINDRICAL_SURFACE along its seam produces a new seam edge
whose 3D LINE runs from z=0 to z=10 in the +Z direction (sense .T.), but whose
pcurve on the cylinder runs from v=10 down to v=0 (inverted V direction, .F.)
— so the pcurve and 3D curve have opposite parameterisations.

A topology checker reports invalid edges; a follow-up same-parameter
recomputation would be needed to fix it.

Byte assertions:
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'PCURVE') and contains(b'SURFACE_CURVE')
  contains(b'1.0E-7')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N005",
    defect=(
        "seam edge on CYLINDRICAL_SURFACE: 3D LINE +Z sense but pcurve in -V "
        "direction (inverted); pcurve and 3D curve parameterisations opposite; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylinder: radius 1.0, axis along Z, origin at (0,0,0)
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cyl_orig")
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},1.0)")

# Seam edge: 3D LINE from (1,0,0) to (1,0,10) along +Z
p_seam_bot = f.cartesian_point((1.0, 0.0, 0.0), name="p_seam_bot")
p_seam_top = f.cartesian_point((1.0, 0.0, 10.0), name="p_seam_top")
v_seam_bot = f.vertex_point(p_seam_bot, name="v_bot")
v_seam_top = f.vertex_point(p_seam_top, name="v_top")

# 3D line in +Z direction (sense .T.)
d_plus_z = f.direction((0.0, 0.0, 1.0))
vec_z = f.vector(d_plus_z, 10.0)
line3d = f.line(p_seam_bot, vec_z, name="seam_line3d_plus_z")

# 2D pcurve context
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv_ctx','2D'))"
)

# Pcurve: on cylinder, U=0 fixed (seam), V from 10 down to 0 (-V direction).
# Start at (u=0, v=10), direction (0,-1) — inverted vs 3D +Z sense.
pc_start_uv = f.cartesian_point((0.0, 10.0), name="pc_start_v10")
pc_dir_neg_v = f.direction((0.0, -1.0))
pc_vec = f.vector(pc_dir_neg_v, 10.0)
pc_line = f.line(pc_start_uv, pc_vec, name="pc_line_neg_v")
pdef = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pdef',(#{pc_line.eid}),#{uv_ctx.eid})"
)
pcurve = f._emit_raw(f"PCURVE('pc_inverted',#{cyl.eid},#{pdef.eid})")

# SURFACE_CURVE: 3D line + inverted pcurve — the mismatch
sc = f._emit_raw(
    f"SURFACE_CURVE('sc_seam',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# SameParameter=.T. (the asserted-but-broken flag)
edge = f.edge_curve(v_seam_bot, v_seam_top, sc, True, name="seam_edge_inverted")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('seam',(#{edge.eid},#{cyl.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N005','N005','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tight tolerance 1.0E-7 — byte assertion value.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),#{lu.eid},"
    f"'distance_accuracy_value','model_precision')"
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
