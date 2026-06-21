"""N019 — OFFSET_SURFACE with sub-tolerance offset (fixed-tolerance importer hard-codes 1e-3).

An OFFSET_SURFACE built on a PLANE whose offset distance (5.0E-5 mm) is below
the importer's hard-coded working tolerance of 1.0E-3 mm. BRL-CAD's step-g
importer ignores the file's UNCERTAINTY_MEASURE_WITH_UNIT (1.0E-6) and
hard-codes 1e-3, crushing the tiny offset surface back onto its base plane.

Byte assertions:
  contains(b'OFFSET_SURFACE')
  contains(b'PLANE')
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N019",
    defect=(
        "OFFSET_SURFACE on PLANE with offset 5.0E-5 mm; file tol 1.0E-6; "
        "hard-coded 1.0E-3 importer tolerance crushes offset back to base; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Base PLANE at z=0
plane_orig = f.cartesian_point((0.0, 0.0, 0.0), name="plane_orig")
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
base_plane = f.plane(plc, name="base_plane")

# OFFSET_SURFACE 5e-5 mm above base plane.
# OFFSET_SURFACE(<basis_surface>, <distance>, <self_intersect>)
offset_surf = f._emit_raw(
    f"OFFSET_SURFACE('',#{base_plane.eid},5.0E-5,.F.)"
)

# Edges lying at z=5e-5 (on the offset surface).
p0 = f.cartesian_point((0.0, 0.0, 5.0E-5), name="p0_on_offset")
p1 = f.cartesian_point((10.0, 0.0, 5.0E-5), name="p1_on_offset")
v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 10.0)
line = f.line(p0, vec, name="line_on_offset")
edge = f.edge_curve(v0, v1, line, name="edge_at_offset")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('offset_set',(#{edge.eid},#{offset_surf.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N019','N019','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# File declares 1.0E-6 precision — byte assertion; importer ignores and uses 1e-3.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','file_precision_ignored_by_importer')"
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
