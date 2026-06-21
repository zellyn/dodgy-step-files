"""Gp108 — CheckPCurveRange B-spline-out-of-knot.

Catalog claim: Pcurve B-spline with knot range [0,5] used on edge parametrized
[-1,6]. CheckPCurveRange fails to detect and report that pcurve evaluation falls
outside valid knot domain.

Mechanism: EDGE_CURVE whose 3D curve spans parameter [-1, 6] but the PCURVE
B-spline has knot domain [0, 5]. Evaluation at t=-1 or t=6 is outside the
valid domain — CheckPCurveRange should flag this. GEOMETRIC_CURVE_SET root.

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp108",
    defect=(
        "EDGE_CURVE with 3D LINE spanning parameter [-1, 6] (via oversized vector); "
        "PCURVE B-spline knot domain [0, 5]; "
        "edge parametrization [-1, 6] extends outside pcurve's valid domain; "
        "CheckPCurveRange must detect and report out-of-domain evaluation; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

anchor = f.cartesian_point((0.0, 0.0, 0.0))

# Host plane for pcurve
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# 3D LINE: starts at (-1, 0, 0), direction +x, magnitude 7 → spans parameter [0, 7]
# But we treat the edge as having 3D parameter range covering [-1, 6] by starting
# the line at the extended start and using length 7.
# The EDGE_CURVE runs from v_start at param 0 to v_end at param 7 on this line.
# The pcurve domain [0, 5] is shorter — so at 3D param 0 (edge start) and 7 (edge end),
# the pcurve evaluation falls outside [0, 5].
p_3d_start = f.cartesian_point((-1.0, 0.0, 0.0), name="edge_start_at_neg1")
p_3d_end   = f.cartesian_point(( 6.0, 0.0, 0.0), name="edge_end_at_6")
v_start = f.vertex_point(p_3d_start)
v_end   = f.vertex_point(p_3d_end)

d_x    = f.direction((1.0, 0.0, 0.0))
vec_7  = f.vector(d_x, 7.0)  # magnitude 7 → 3D parameter range [0, 7]
line3d = f.line(p_3d_start, vec_7)

# PCURVE B-spline: knot domain [0, 5] — shorter than the edge's 3D range
# Degree 3, 6 poles: knots (4,1,1,4) at (0,1.667,3.333,5.0) — valid domain [0,5]
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)"
    "PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)

pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((1.0, 1.0))
pc2 = f.cartesian_point((2.5, 0.5))
pc3 = f.cartesian_point((3.5, 1.5))
pc4 = f.cartesian_point((4.5, 0.5))
pc5 = f.cartesian_point((5.0, 0.0))

pcurve_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pcurve_knots_0_to_5',3,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,1.667,3.333,5.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcurve_domain_0_5',(#{pcurve_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('pcurve_knot_range_0_5',#{surf.eid},#{defrep.eid})")

# SURFACE_CURVE: 3D range [0,7] but pcurve domain [0,5]
# Edge param -1 to 6: pcurve evaluation at t<0 and t>5 is out-of-domain
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('out_of_knot',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('edge_param_outside_pcurve_domain',"
    f"#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('gcs',(#{anchor.eid},#{edge.eid}))")
f.add_product_chain(gcs)
