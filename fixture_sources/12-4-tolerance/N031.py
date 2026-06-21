"""N031 — Surface discontinuities introduced by translation (G0/G1/G2 break at shared edges).

G0/G1/G2 discontinuities introduced when neighbouring faces are re-parametrized
into different surface types during translation. Two B_SPLINE_SURFACE_WITH_KNOTS
patches whose tangent planes at their shared edge disagree by more than the
declared tolerance (1.0E-5). A Catia procedural blend became two NURBS patches
that lost tangent continuity.

Byte assertions:
  count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
  contains(b'1.0E-5')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N031",
    defect=(
        "two B_SPLINE_SURFACE_WITH_KNOTS patches; tangent planes at shared edge "
        "disagree after independent re-fit; G1 break > 1.0E-5; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Patch 1: flat patch in XY plane (z=0), 2x2 control net, degree 1x1.
p00 = f.cartesian_point((0.0, 0.0, 0.0), name="p00")
p10 = f.cartesian_point((5.0, 0.0, 0.0), name="p10")
p01 = f.cartesian_point((0.0, 5.0, 0.0), name="p01")
p11 = f.cartesian_point((5.0, 5.0, 0.0), name="p11")
surf1 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('patch1',1,1,"
    f"((#{p00.eid},#{p10.eid}),(#{p01.eid},#{p11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# Patch 2: slightly tilted patch — tangent at shared edge (u=1) differs.
# Control points introduce a tilt: the shared edge col has a z-offset of 1e-4
# relative to patch1, creating a tangent jump > 1e-5 at the seam.
q00 = f.cartesian_point((5.0, 0.0, 0.0), name="q00_shared")
q10 = f.cartesian_point((10.0, 0.0, 1.0E-4), name="q10_tilted")
q01 = f.cartesian_point((5.0, 5.0, 0.0), name="q01_shared")
q11 = f.cartesian_point((10.0, 5.0, 1.0E-4), name="q11_tilted")
surf2 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('patch2',1,1,"
    f"((#{q00.eid},#{q10.eid}),(#{q01.eid},#{q11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('g1_break',(#{surf1.eid},#{surf2.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N031','N031','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Declared tolerance 1.0E-5 — byte assertion; tangent gap > this.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','tangent_continuity_threshold')"
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
