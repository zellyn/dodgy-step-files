"""Tb011 — Periodic-surface seam matching requires period-relative tolerance.

CYLINDRICAL_SURFACE radius 1.0e6 mm has period 2*pi*R ~= 6.28e6. A wire's
pcurve U-coordinates differ by 2*pi + 1.0e-3 between adjacent edges (one full
period plus drift). Receiver using fixed parametric tolerance (1.0e-7 rad) sees
2*pi + 1.0e-3 != 0 and rejects the seam. Receiver using fmod(diff, 2*pi)
absorbs the period and accepts the seam within 1.0e-3. Same wire, two outcomes.

Byte assertions:
  contains(b'CYLINDRICAL_SURFACE')
  count_entity_def(b'PCURVE') == 2
  contains(b'1.0E-3')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tb011",
    defect=(
        "CYLINDRICAL_SURFACE R=1.0E6; pcurve U-coords differ by 2*pi+1.0E-3 "
        "(one period plus drift); fixed 1.0E-7 rad tolerance rejects seam; "
        "fmod(diff,2*pi) policy accepts it; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylinder axis origin and orientation.
axis_origin = f.cartesian_point((0.0, 0.0, 0.0), name="axis_origin")
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(axis_origin, zdir, xdir, name="axis")
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('huge_cyl',#{plc.eid},1.0E6)")

# 3D points on the cylinder surface.
p0 = f.cartesian_point((1.0e6, 0.0, 0.0), name="p0_at_u0")
p1 = f.cartesian_point((1.0e6, 1.0e3, 0.0), name="p1_at_u_2pi_plus_1e-3")
p2 = f.cartesian_point((1.0e6, 0.0, 1000.0), name="p2_continuation")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1_seam_drift")
v2 = f.vertex_point(p2, name="v2")

# 3D curves (line placeholders; the time bomb is in pcurve U-coordinates).
d01 = f.direction((0.0, 1.0, 0.0))
vec01 = f.vector(d01, 1.0e3)
l01 = f.line(p0, vec01)

d12 = f.direction((0.0, -1.0, 0.0))
vec12 = f.vector(d12, 1.0)
l12 = f.line(p1, vec12)

# UV context (2D) for pcurves.
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv_ctx','2D'))"
)

# PCURVE 1: U from 0 to 2*pi + 1.0e-3 (one full period plus drift).
two_pi_plus = 2.0 * math.pi + 1.0e-3
uv0 = f.cartesian_point((0.0, 0.0), name="uv0")
uv_dir = f.direction((1.0, 0.0))
uv_vec1 = f.vector(uv_dir, two_pi_plus)
uv_line1 = f.line(uv0, uv_vec1, name="uv_line1")
pdef1 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('def1',(#{uv_line1.eid}),#{uv_ctx.eid})"
)
pc1 = f._emit_raw(f"PCURVE('pc1',#{cyl.eid},#{pdef1.eid})")
sc1 = f._emit_raw(
    f"SURFACE_CURVE('sc1',#{l01.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e0 = f.edge_curve(v0, v1, sc1, name="e_period_plus_1e-3")

# PCURVE 2: back from 2*pi + 1.0e-3 to 1.0e-3 (delta = -2*pi).
uv1 = f.cartesian_point((two_pi_plus, 0.0), name="uv1")
uv_dir2 = f.direction((-1.0, 0.0))
uv_vec2 = f.vector(uv_dir2, 2.0 * math.pi)
uv_line2 = f.line(uv1, uv_vec2, name="uv_line2")
pdef2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('def2',(#{uv_line2.eid}),#{uv_ctx.eid})"
)
pc2 = f._emit_raw(f"PCURVE('pc2',#{cyl.eid},#{pdef2.eid})")
sc2 = f._emit_raw(
    f"SURFACE_CURVE('sc2',#{l12.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e1 = f.edge_curve(v1, v2, sc2, name="e_back_to_seam")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('cs',(#{e0.eid},#{e1.eid},#{cyl.eid}))"
)

# Manual PRODUCT chain with declared tolerance 1.0E-3 (byte assertion).
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('Tb011','Tb011','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-3),#{lu.eid},"
    f"'distance_accuracy_value','tol_below_seam_drift')"
)
ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('ctx_3d','3D'))"
)
wfr = f._emit_raw(
    f"GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION('',(#{gcs.eid}),#{ctx.eid})"
)
f._emit_raw(f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{wfr.eid})")
