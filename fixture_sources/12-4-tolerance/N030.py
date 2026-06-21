"""N030 — Quarter CYLINDRICAL_SURFACE stored as B_SPLINE_SURFACE_WITH_KNOTS.

A surface that mathematically is a CYLINDRICAL_SURFACE is stored as a generic
B_SPLINE_SURFACE_WITH_KNOTS. Shape: a quarter-cylinder approximation modelled
as a degree-3-by-1 B-spline with a 4×2 control net (8 CARTESIAN_POINTs), with
declared canonicalisation tolerance 1.0E-6. Feature recognition tools fail
because they cannot query the surface for its radius or axis.

Byte assertions:
  contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  count_entity_def(b'CARTESIAN_POINT') == 8
  contains(b'1.0E-6')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N030",
    defect=(
        "quarter cylinder approximation as B_SPLINE_SURFACE_WITH_KNOTS deg 3x1; "
        "4x2 control net = 8 CARTESIAN_POINTs; canonical recognition fails; "
        "tol 1.0E-6; GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
)

# Quarter cylinder: r=1, axis Z, from theta=0 to theta=pi/2, h from 0 to 1.
# 4 u-direction control points at angles 0, pi/6, pi/3, pi/2 (quarter arc).
# 2 v-direction levels at z=0 and z=1.
angles = [0.0, math.pi / 6, math.pi / 3, math.pi / 2]
z_vals = [0.0, 1.0]
ctrl_pts = []
for z in z_vals:
    for a in angles:
        cp = f.cartesian_point((math.cos(a), math.sin(a), z))
        ctrl_pts.append(cp)

# ctrl_pts layout: [row0_col0..col3, row1_col0..col3] = 8 points total.
# B_SPLINE_SURFACE_WITH_KNOTS:
# name, u_degree, v_degree, control_points_list (2D: rows of col refs),
# surface_form, u_closed, v_closed, self_intersect,
# u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec
row0_refs = ",".join(cp.ref() for cp in ctrl_pts[0:4])
row1_refs = ",".join(cp.ref() for cp in ctrl_pts[4:8])

bspline_surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('qtr_cyl_bspline',3,1,"
    f"(({row0_refs}),({row1_refs})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(2,2),(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('bspline_set',(#{bspline_surf.eid}))")

# Product chain
app_ctx = f._emit_raw("APPLICATION_CONTEXT('automotive_design')")
prod_ctx = f._emit_raw(f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')")
product = f._emit_raw(f"PRODUCT('N030','N030','',(#{prod_ctx.eid}))")
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
    f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#{lu.eid},"
    f"'distance_accuracy_value','canonical_recognition_tolerance')"
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
