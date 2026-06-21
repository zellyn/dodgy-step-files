"""N027 — Small CYLINDRICAL_SURFACE with gmsh OCCTargetUnit silently ignored.

gmsh sets OCCTargetUnit="M" but a STEP CYLINDRICAL_SURFACE of r=1 h=10 in
MILLI-METRE units gets imported as r=1000 h=10000 (x1000 applied unexpectedly).
The setting is honored via importShapes but skipped via importShapesNativePointer.
Declared precision 1.0E-6 mm is at the working-tolerance boundary, so any
unit conversion glitch is immediately visible.

Byte assertions:
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'.MILLI.')
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N027",
    defect=(
        "small CYLINDRICAL_SURFACE r=1 h=10 mm; unit .MILLI.; OCCTargetUnit=M "
        "path skips conversion giving r=1000 instead of 0.001; tol 1.0E-6; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Small cylinder: r=1 mm, axis Z, height edges at z=0 and z=10.
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cyl_orig")
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('small_cyl',#{cyl_plc.eid},1.0)")

# Seam-line at r=1, running from z=0 to z=10.
p0 = f.cartesian_point((1.0, 0.0, 0.0), name="p0_seam_bot")
p1 = f.cartesian_point((1.0, 0.0, 10.0), name="p1_seam_top")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((0.0, 0.0, 1.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec, name="seam_line")
edge = f.edge_curve(v0, v1, line, name="seam_edge")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('cyl_set',(#{cyl.eid},#{edge.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N027','N027','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

# Explicitly using .MILLI. — byte assertion value.
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','precision_at_working_tol_boundary')"
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
