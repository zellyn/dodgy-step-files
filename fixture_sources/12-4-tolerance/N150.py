"""N150 — IsMergedClosed.v_overlap_negativity_test.

V-parameter gap detection missing: curves separated by 1.0 in V (gap beyond
overlap tolerance) proceed to distInner/distOuter logic. dist<0 check omitted;
non-overlapping geometries incorrectly merged on U-closed surfaces.

Geometry: two edges on a cylindrical surface separated by 1.0 in V-parameter
— beyond overlap tolerance; missing dist<0 guard allows incorrect merge.

(No byte assertions; kernel-test-pair — defect requires IsMergedClosed runtime
invocation on U-closed surface.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N150",
    defect=(
        "IsMergedClosed v_overlap_negativity_test: cylinder; "
        "2 edges separated 1.0 in V; dist<0 guard absent; "
        "non-overlapping merged on U-closed surface; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylindrical surface: radius 5, axis Z.
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cyl_orig")
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},5.0)")

# Two edges at different Z heights (V-param offset 1.0 mm).
p0a = f.cartesian_point((5.0, 0.0, 0.0), name="p0a_v0")
p1a = f.cartesian_point((5.0, 0.0, 1.0), name="p1a_v1")
p0b = f.cartesian_point((5.0, 0.0, 2.0), name="p0b_v2")  # V-gap = 1.0 between edges
p1b = f.cartesian_point((5.0, 0.0, 3.0), name="p1b_v3")

v0a = f.vertex_point(p0a, name="v0a")
v1a = f.vertex_point(p1a, name="v1a")
v0b = f.vertex_point(p0b, name="v0b")
v1b = f.vertex_point(p1b, name="v1b")

d_z = f.direction((0.0, 0.0, 1.0))
eA = f.edge_curve(v0a, v1a, f.line(p0a, f.vector(d_z, 1.0)), name="eA_v0_to_v1")
eB = f.edge_curve(v0b, v1b, f.line(p0b, f.vector(d_z, 1.0)), name="eB_v2_to_v3")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('v_gap_merged',(#{cyl.eid},#{eA.eid},#{eB.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N150','N150','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
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
