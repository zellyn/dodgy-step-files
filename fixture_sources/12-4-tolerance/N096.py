"""N096 — BRepLib.UpdateInnerTolerances cone-apex-singularity.

Edge passes through cone apex where curvature → ∞; UpdateInnerTolerances
samples near singularity, Epsilon(aDist) diverges, producing unbounded
tolerance. Algorithm lacks guard against singular points.

Geometry: CONICAL_SURFACE (half-angle 30°) with edge crossing apex from
base circle through origin. Sampling at apex causes curvature singularity;
tolerance escalates beyond control.

(No byte assertions; kernel-test-pair — defect requires UpdateInnerTolerances
runtime invocation.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N096",
    defect=(
        "UpdateInnerTolerances cone-apex-singularity: CONICAL_SURFACE 30-deg; "
        "edge from base (5,0,0) through apex (0,0,0); curvature→inf at apex; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Conical surface: apex at origin, half-angle 30°, axis Z.
cone_orig = f.cartesian_point((0.0, 0.0, 0.0), name="cone_orig")
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
# CONICAL_SURFACE: placement, semi-angle (radians).
half_angle = math.radians(30.0)
cone = f._emit_raw(
    f"CONICAL_SURFACE('cone',#{cone_plc.eid},{half_angle:.10f})"
)

# Edge from base point (5,0,0) toward apex (0,0,0).
p_base = f.cartesian_point((5.0, 0.0, 0.0), name="p_base")
p_apex = f.cartesian_point((0.0, 0.0, 0.0), name="p_apex")
v_base = f.vertex_point(p_base, name="v_base")
v_apex = f.vertex_point(p_apex, name="v_apex")

d_toward_apex = f.direction((-1.0, 0.0, 0.0))
vec_to_apex = f.vector(d_toward_apex, 5.0)
line_to_apex = f.line(p_base, vec_to_apex, name="line_to_apex")
edge_apex = f.edge_curve(v_base, v_apex, line_to_apex, name="edge_through_apex")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cone_apex',(#{cone.eid},#{edge_apex.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N096','N096','',(#{prod_ctx.eid}))")
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
