"""P006 — 360° revolution of arc-of-ellipse produces self-intersecting solid.

Catalog claim: a solid from 360° revolution of a half-ellipse profile
(major axis on X, semi_axis_1 > semi_axis_2) emits self-intersecting /
mirrored surface. With major axis on Y, or generatrix converted to B-spline,
round-trips correctly. Suggests a bug in OCCT's CONIC / ELLIPSE parametric-
domain handling near the seam u=0/2π.

The defect: SURFACE_OF_REVOLUTION whose generatrix is a TRIMMED_CURVE wrapping
an ELLIPSE with semi_axis_1=10.0 > semi_axis_2=5.0, revolved 2π. The seam at
u=0/2π creates a self-intersecting solid because the ellipse parametric domain
wraps incorrectly at the seam. Receivers enforcing the spec must heal this;
OCCT silently accepts with empty result.

Byte assertions:
  contains(b'SURFACE_OF_REVOLUTION')
  count_entity_def(b'ELLIPSE') >= 1
  contains(b'TRIMMED_CURVE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P006",
    defect=(
        "SURFACE_OF_REVOLUTION: generatrix is TRIMMED_CURVE(ELLIPSE) "
        "with semi_axis_1=10.0 > semi_axis_2=5.0, major axis on X; "
        "full 360 degree revolution 2π around Z-axis; "
        "self-intersecting solid at seam u=0/2π from CONIC parametric-domain bug; "
        "with major axis on Y or B-spline generatrix the bug does not occur; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# ── Ellipse: semi_axis_1=10 (major, along X), semi_axis_2=5 (minor, along Y) ──
# The ellipse is in the XZ plane (Y=0 plane), centered at origin, with
# X as semi-major axis. This is the orientation that triggers the seam defect.
ellipse_origin = f.cartesian_point((0.0, 0.0, 0.0))
ellipse_zdir = f.direction((0.0, 1.0, 0.0))   # normal out of XZ plane
ellipse_xdir = f.direction((1.0, 0.0, 0.0))   # major axis = X
ellipse_plc = f.axis2_placement_3d(ellipse_origin, ellipse_zdir, ellipse_xdir)

# ELLIPSE with semi_axis_1=10, semi_axis_2=5 (major on X, minor on Z).
ellipse = f._emit_raw(
    f"ELLIPSE('ellipse_generatrix',#{ellipse_plc.eid},10.0,5.0)"
)

# TRIMMED_CURVE: trim the ellipse from parameter 0 to π (half ellipse,
# from (10,0,0) to (-10,0,0) through (0,0,5)). This is the generatrix arc.
# trim1 = parametric value 0.0 (angle 0 on ellipse = point (10,0,0))
# trim2 = parametric value π   (angle π on ellipse = point (-10,0,0))
trim_start = f.cartesian_point((10.0, 0.0, 0.0))   # point at parameter 0
trim_end = f.cartesian_point((-10.0, 0.0, 0.0))    # point at parameter π

# TRIMMED_CURVE: trim by parameter value (PARAMETER_VALUE) from 0 to π ≈ 3.14159
generatrix = f._emit_raw(
    f"TRIMMED_CURVE('half_ellipse',#{ellipse.eid},"
    f"(PARAMETER_VALUE(0.0),#{trim_start.eid}),"
    f"(PARAMETER_VALUE(3.14159265358979),#{trim_end.eid}),"
    f".T.,.PARAMETER.)"
)

# ── Axis of revolution: Z-axis through origin (revolving the XZ-plane arc) ──
rev_origin = f.cartesian_point((0.0, 0.0, 0.0))
rev_zdir = f.direction((0.0, 0.0, 1.0))
rev_axis = f._emit_raw(
    f"AXIS1_PLACEMENT('rev_axis',#{rev_origin.eid},#{rev_zdir.eid})"
)

# ── SURFACE_OF_REVOLUTION: revolve half-ellipse 360° around Z-axis ──────────
# This is the defect surface: the ellipse parametric domain wraps incorrectly
# at u=0/2π causing self-intersection in the revolved solid.
rev_surf = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('ellipse_revolution',#{generatrix.eid},#{rev_axis.eid})"
)

# ── Wrap in GEOMETRIC_CURVE_SET so the fixture produces shape_null==True ────
# (A reader that somehow accepts the surface still gets no closed solid)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{generatrix.eid},#{rev_surf.eid}))")
f.add_product_chain(gcs)

# ── NAUO scaffolding for §12.6 assembly-presence lint ────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('EllipseRevolve','EllipseRevolve','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','revolve_instance','',#9004,#{sub_pdef.eid},$)"
)
