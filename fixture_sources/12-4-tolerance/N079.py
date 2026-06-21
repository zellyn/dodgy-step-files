"""N079 — ShapeAnalysis_Edge.CheckPointsAreOnEdges sphere-pole.

CheckPointsAreOnEdges verifies vertex-on-edge by comparing parameter values.
At a sphere pole (north/south), the U parameter is singular (any U maps to
the same physical location). The check fails because the pole's indeterminate
U doesn't match the computed parameter, incorrectly marking the vertex as NOT
on the edge.

Geometry: sphere (radius 10 mm) with edge connecting pole endpoint (0,0,10)
to nearby point (0.1,0,9.99). Pole singularity makes U-parameter comparison
nondeterministic.

(No byte assertions; kernel-test-pair.)

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="N079",
    defect=(
        "CheckPointsAreOnEdges sphere-pole: edge from north pole (0,0,10) "
        "to (0.1,0,9.99); singular U at pole causes false-negative on-edge check; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Sphere of radius 10 at origin.
sph_orig = f.cartesian_point((0.0, 0.0, 0.0), name="sph_orig")
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_plc = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('sphere',#{sph_plc.eid},10.0)")

# Edge from pole (0,0,10) to (0.1, 0, 9.99).
p_pole = f.cartesian_point((0.0, 0.0, 10.0), name="p_north_pole")
p_near = f.cartesian_point((0.1, 0.0, 9.99), name="p_near_pole")
v_pole = f.vertex_point(p_pole, name="v_north_pole")
v_near = f.vertex_point(p_near, name="v_near")

# Approximate the edge as a short line segment near the pole.
d = f.direction((1.0, 0.0, -0.1))  # direction from pole toward near point
vec = f.vector(d, 0.1005)  # approx distance sqrt(0.01+0.0001)
ln = f.line(p_pole, vec, name="pole_edge_approx")
edge = f.edge_curve(v_pole, v_near, ln, name="pole_edge")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('sphere_pole',(#{sphere.eid},#{edge.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N079','N079','',(#{prod_ctx.eid}))")
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
