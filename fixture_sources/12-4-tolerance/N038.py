"""N038 — Patrikalakis interval-solid violation: face-pair gap exceeds bound.

Adjacent B_SPLINE_SURFACE_WITH_KNOTS patches along their shared edge have a
maximum Hausdorff distance of 5×ε where ε = 1.0E-5 mm (declared tolerance).
The maximum gap 5.0E-5 mm exceeds the interval radius, so the model is not
provably gap-free for any tolerance below that gap.

Byte assertions:
  count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 2
  contains(b'1.0E-5')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N038",
    defect=(
        "two B_SPLINE_SURFACE_WITH_KNOTS patches; shared-edge max gap 5.0E-5 = "
        "5×ε where ε=1.0E-5; interval-solid condition violated; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Patch 1: flat 2x2 patch at z=0.
p00 = f.cartesian_point((0.0, 0.0, 0.0), name="p00")
p10 = f.cartesian_point((5.0, 0.0, 0.0), name="p10")
p01 = f.cartesian_point((0.0, 5.0, 0.0), name="p01")
p11 = f.cartesian_point((5.0, 5.0, 0.0), name="p11")
surf1 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('patch1',1,1,"
    f"((#{p00.eid},#{p10.eid}),(#{p01.eid},#{p11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

# Patch 2: adjacent patch with shared edge at x=5, but z-offset 5e-5 (gap > ε).
q00 = f.cartesian_point((5.0, 0.0, 5.0E-5), name="q00_gap_5e-5")
q10 = f.cartesian_point((10.0, 0.0, 0.0), name="q10")
q01 = f.cartesian_point((5.0, 5.0, 5.0E-5), name="q01_gap_5e-5")
q11 = f.cartesian_point((10.0, 5.0, 0.0), name="q11")
surf2 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('patch2',1,1,"
    f"((#{q00.eid},#{q10.eid}),(#{q01.eid},#{q11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,(2,2),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('interval',(#{surf1.eid},#{surf2.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N038','N038','',(#{prod_ctx.eid}))")
pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{product.eid})")
pdc = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
pd = f._emit_raw(f"PRODUCT_DEFINITION('','',#{pdf.eid},#{pdc.eid})")
pds = f._emit_raw(f"PRODUCT_DEFINITION_SHAPE('','',#{pd.eid})")

lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
# Interval radius ε = 1.0E-5; shared-edge gap 5.0E-5 > ε.
unc = f._emit_raw(
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-5),#{lu.eid},"
    f"'distance_accuracy_value','interval_solid_radius')"
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
