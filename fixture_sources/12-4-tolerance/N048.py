"""N048 — Walk-line initial step unrelated to tolerance during surface intersection.

A surface-surface intersection algorithm walks along the intersection curve in
fixed-size parameter steps, ignoring the surfaces' tolerances. Two
CYLINDRICAL_SURFACE instances (coarse tolerance 1e-3) intersect; the fixed
walk-step produces a coarse polyline accepted as the intersection curve.

Two PCURVE instances represent the intersection curve on each cylinder.
INTERSECTION_CURVE links the 3D result to both pcurves.

Byte assertions:
  contains(b'INTERSECTION_CURVE')
  count_entity_def(b'CYLINDRICAL_SURFACE') == 2
  count_entity_def(b'PCURVE') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N048",
    defect=(
        "surface-surface walk: 2 CYLINDRICAL_SURFACE at coarse tol 1e-3; "
        "fixed walk step ignores tol; INTERSECTION_CURVE with 2 PCURVE; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Cylinder 1: r=5, axis Z at origin
c1_orig = f.cartesian_point((0.0, 0.0, 0.0), name="c1_orig")
c1_zdir = f.direction((0.0, 0.0, 1.0))
c1_xdir = f.direction((1.0, 0.0, 0.0))
c1_plc = f.axis2_placement_3d(c1_orig, c1_zdir, c1_xdir)
cyl1 = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl1',#{c1_plc.eid},5.0)")

# Cylinder 2: r=5, axis X at (5,0,0)
c2_orig = f.cartesian_point((5.0, 0.0, 0.0), name="c2_orig")
c2_zdir = f.direction((1.0, 0.0, 0.0))
c2_xdir = f.direction((0.0, 1.0, 0.0))
c2_plc = f.axis2_placement_3d(c2_orig, c2_zdir, c2_xdir)
cyl2 = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl2',#{c2_plc.eid},5.0)")

# 2D parametric context
uv_ctx = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "GLOBAL_UNIT_ASSIGNED_CONTEXT($)"
    "REPRESENTATION_CONTEXT('uv_ctx','2D'))"
)

# PCURVE 1: on cyl1, a parametric line at u=pi/2 (the intersection)
pc1_start = f.cartesian_point((math.pi / 2, 0.0), name="pc1_start")
pc1_dir = f.direction((0.0, 1.0))
pc1_vec = f.vector(pc1_dir, 10.0)
pc1_line = f.line(pc1_start, pc1_vec, name="pc1_line")
pdef1 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pdef1',(#{pc1_line.eid}),#{uv_ctx.eid})")
pcurve1 = f._emit_raw(f"PCURVE('pc1',#{cyl1.eid},#{pdef1.eid})")

# PCURVE 2: on cyl2, a parametric line at u=0 (the intersection)
pc2_start = f.cartesian_point((0.0, 0.0), name="pc2_start")
pc2_dir = f.direction((0.0, 1.0))
pc2_vec = f.vector(pc2_dir, 10.0)
pc2_line = f.line(pc2_start, pc2_vec, name="pc2_line")
pdef2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pdef2',(#{pc2_line.eid}),#{uv_ctx.eid})")
pcurve2 = f._emit_raw(f"PCURVE('pc2',#{cyl2.eid},#{pdef2.eid})")

# 3D intersection curve: a line approximation (the walk produced a coarse polyline)
p3d_0 = f.cartesian_point((5.0, 0.0, 0.0), name="int_p0")
p3d_1 = f.cartesian_point((5.0, 0.0, 10.0), name="int_p1")
v3d_0 = f.vertex_point(p3d_0, name="v3d_0")
v3d_1 = f.vertex_point(p3d_1, name="v3d_1")
d3d = f.direction((0.0, 0.0, 1.0))
vec3d = f.vector(d3d, 10.0)
line3d = f.line(p3d_0, vec3d, name="int_line")

# INTERSECTION_CURVE: 3D line + two pcurves.
int_curve = f._emit_raw(
    f"INTERSECTION_CURVE('int_curve',#{line3d.eid},(#{pcurve1.eid},#{pcurve2.eid}),.PCURVE_S1.)"
)
edge = f.edge_curve(v3d_0, v3d_1, int_curve, name="int_edge")

gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('ints',(#{cyl1.eid},#{cyl2.eid},#{edge.eid}))"
)

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N048','N048','',(#{prod_ctx.eid}))")
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
    f"'distance_accuracy_value','coarse_walk_tolerance')"
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
