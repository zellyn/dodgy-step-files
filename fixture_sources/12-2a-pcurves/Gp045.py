"""Gp045 — Edge copy during SameParameter recomputation inherits stale parameter range.

Catalog defect: PLANE host; 3D B-spline degree 2, knots (0.0, 0.333, 0.667, 1.0);
matching PCURVE B-spline. Defect: FixSameParameter copies EDGE_CURVE to new TEdge
but preserves old range bounds. New BSpline's actual knot domain differs from
preserved bounds, causing parameter mismatch between 3D and 2D curves.

Fixture: rectangular PLANE face. Bottom edge has a degree-2 B-spline 3D curve with
4 inner knot spans (knots [0.0, 0.333, 0.667, 1.0]) that correctly spans [0,1], plus
a PCURVE B-spline with the same knot structure. The defect is expressed by having
the PCURVE's parameter domain [0,1] mismatched against the 3D curve's effective
domain — the PCURVE starts at t=0.05 and ends at t=0.95 (stale copied bounds),
but the 3D curve spans [0.0, 1.0]. After edge-copy, the retained bounds [0.05, 0.95]
no longer cover the actual knot domain, causing SameParameter recomputation failure.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp045",
    defect=(
        "PLANE face bottom edge: 3D B-spline degree 2 knots [0.0,0.333,0.667,1.0]; "
        "PCURVE B-spline same knot structure but parameter range inherited as stale "
        "[0.05,0.95] after EDGE_CURVE copy — does not cover full knot domain [0,1]; "
        "FixSameParameter edge-copy trap: stale bounds cause 3D/2D parameter mismatch"
    ),
)

# Planar surface in the XY plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle corners: (0,0,0), (10,0,0), (10,5,0), (0,5,0)
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0, 0.0))
p11 = f.cartesian_point((10.0, 5.0, 0.0))
p01 = f.cartesian_point((0.0, 5.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# THE DEFECT: bottom edge 3D B-spline with 4 spans.
# degree=2, knots [0.0, 0.333, 0.667, 1.0], mults [3,1,1,3] => sum=8 = 5+2+1
# Control points: 5 points tracing (0,0,0)->(2.5,0,0)->(5,0,0)->(7.5,0,0)->(10,0,0)
# This is a uniform B-spline on the x-axis — correct 3D geometry.
cp0_3d = f.cartesian_point((0.0,  0.0, 0.0))
cp1_3d = f.cartesian_point((2.5,  0.0, 0.0))
cp2_3d = f.cartesian_point((5.0,  0.0, 0.0))
cp3_3d = f.cartesian_point((7.5,  0.0, 0.0))
cp4_3d = f.cartesian_point((10.0, 0.0, 0.0))
bspline_3d = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0_3d, cp1_3d, cp2_3d, cp3_3d, cp4_3d],
    knot_multiplicities=[3, 1, 1, 3],   # sum=8 = 5+2+1
    knots=[0.0, 0.333, 0.667, 1.0],
)

# PCURVE B-spline: same knot structure in UV (U maps 0->10, V stays at 0).
# degree=2, 5 control points in UV, same knots.
# The stale parameter range [0.05, 0.95] is encoded via PCURVE trim below the
# 3D curve's knot domain [0.0, 1.0] — the edge_curve vertex parameters differ.
pc0 = f.cartesian_point((0.0,  0.0))
pc1 = f.cartesian_point((2.5,  0.0))
pc2 = f.cartesian_point((5.0,  0.0))
pc3 = f.cartesian_point((7.5,  0.0))
pc4 = f.cartesian_point((10.0, 0.0))
pc_bspline = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[pc0, pc1, pc2, pc3, pc4],
    knot_multiplicities=[3, 1, 1, 3],   # sum=8 = 5+2+1
    knots=[0.0, 0.333, 0.667, 1.0],
)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{surf.eid},#{pc_bot_def.eid})")

# SURFACE_CURVE: 3D B-spline + PCURVE. Then EDGE_CURVE vertex parameters encode
# the stale range [0.05, 0.95] instead of [0.0, 1.0].
# The stale bounds are expressed by using VERTEX_POINT coordinates that do NOT
# lie exactly at t=0.0 and t=1.0 of the B-spline — they come from old pre-copy
# range values. The vertex positions (0,0,0) and (10,0,0) correspond to t=0 and t=1,
# but the stale edge record "thinks" the trimming is at t=0.05..0.95.
# We represent this by placing the 3D B-spline range trim in the TRIMMED_CURVE
# — the edge's 3D and 2D parameter ranges are [0.05, 0.95] on the pcurve even
# though the B-spline's knot domain goes [0.0, 1.0]. This is the stale-copy defect.
# We encode it in SURFACE_CURVE with a trimmed 3D curve that only covers [0.05,0.95]:
tc_3d = f._emit_raw(
    f"TRIMMED_CURVE('stale_trim',#{bspline_3d.eid},"
    f"(PARAMETER_VALUE(0.05)),(PARAMETER_VALUE(0.95)),.T.,.PARAMETER.)"
)
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom',#{tc_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_edge',#{v00.eid},#{v10.eid},#{sc_bot.eid},.T.)"
)

# Correct right edge: (10,0,0) -> (10,5,0)
d_y   = f.direction((0.0, 1.0, 0.0))
vec_y = f.vector(d_y, 5.0)
line_right_3d = f.line(p10, vec_y)
pc_r_start = f.cartesian_point((10.0, 0.0))
pc_r_dir   = f.direction((0.0, 1.0))
pc_r_vec   = f.vector(pc_r_dir, 5.0)
pc_r_line  = f.line(pc_r_start, pc_r_vec)
pc_r_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_r_line.eid}),#{prc.eid})"
)
pcurve_r = f._emit_raw(f"PCURVE('right_pc',#{surf.eid},#{pc_r_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right',#{line_right_3d.eid},(#{pcurve_r.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_edge',#{v10.eid},#{v11.eid},#{sc_right.eid},.T.)"
)

# Correct top edge: (10,5,0) -> (0,5,0)
line_top_3d = f.line(p11, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0))
pc_t_start = f.cartesian_point((10.0, 5.0))
pc_t_dir   = f.direction((-1.0, 0.0))
pc_t_vec   = f.vector(pc_t_dir, 10.0)
pc_t_line  = f.line(pc_t_start, pc_t_vec)
pc_t_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_t_line.eid}),#{prc.eid})"
)
pcurve_t = f._emit_raw(f"PCURVE('top_pc',#{surf.eid},#{pc_t_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top',#{line_top_3d.eid},(#{pcurve_t.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v11.eid},#{v01.eid},#{sc_top.eid},.T.)"
)

# Correct left edge: (0,5,0) -> (0,0,0)
line_left_3d = f.line(p01, f.vector(f.direction((0.0, -1.0, 0.0)), 5.0))
pc_l_start = f.cartesian_point((0.0, 5.0))
pc_l_dir   = f.direction((0.0, -1.0))
pc_l_vec   = f.vector(pc_l_dir, 5.0)
pc_l_line  = f.line(pc_l_start, pc_l_vec)
pc_l_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_l_line.eid}),#{prc.eid})"
)
pcurve_l = f._emit_raw(f"PCURVE('left_pc',#{surf.eid},#{pc_l_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left',#{line_left_3d.eid},(#{pcurve_l.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_edge',#{v01.eid},#{v00.eid},#{sc_left.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top,   True),
    f.oriented_edge(edge_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
