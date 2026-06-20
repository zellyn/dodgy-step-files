"""Gp044 — Endpoint-bias projection picks wrong candidate when multiple equidistant points exist.

Catalog defect: PLANE host; 3D B-spline arc degree 2 with inflection at midspan;
PCURVE B-spline. Defect: both endpoints and interior point are equidistant from
probe point. Project's endpoint-bias returns endpoint distance even when interior
local-min is the true projection. PCURVE maps to wrong parameter bounds. Project
returns suboptimal projection result, causing downstream healers to misalign
PCURVE parameter mapping or report stale boundary conditions.

Fixture: rectangular PLANE face where the bottom edge uses a degree-2 B-spline
3D curve that bows upward (creating an inflection arc) while its PCURVE is a
straight LINE along U — the wrong parameter bounds arise because the projection
picks the wrong candidate point.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp044",
    defect=(
        "PLANE face bottom edge: 3D B-spline arc degree 2 bows above plane "
        "y=0 (inflection at midspan at (5,1,0)); PCURVE LINE maps [0,10] in U "
        "at V=0; endpoint-bias projection selects endpoint over interior local-min "
        "projection; PCURVE parameter bounds misaligned with actual 3D geometry"
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

# THE DEFECT: bottom edge 3D B-spline arc bows above plane.
# degree=2, 3 control points: (0,0,0), (5,2,0), (10,0,0) — a parabolic arc
# bowing upward to y=1 at midspan (Bezier midpoint = average of 3 poles = (5,0.666,0)).
# Actually for degree-2 Bezier: midpoint = 0.25*cp0 + 0.5*cp1 + 0.25*cp2
#   = (0.25*0+0.5*5+0.25*10, 0.25*0+0.5*2+0.25*0, 0) = (5, 1, 0).
# So the curve bows up to (5,1,0) at t=0.5. Both endpoints (0,0,0) and (10,0,0) are at y=0.
# An equidistant probe near (5,0,0) has local-min projection at (5,1,0) at interior t=0.5,
# but endpoint-bias returns endpoint t=0 or t=1 whose distance equals the y=0 probe
# distance. This exercises the endpoint-bias bug.
cp0_3d = f.cartesian_point((0.0, 0.0, 0.0))
cp1_3d = f.cartesian_point((5.0, 2.0, 0.0))
cp2_3d = f.cartesian_point((10.0, 0.0, 0.0))
bspline_3d = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0_3d, cp1_3d, cp2_3d],
    knot_multiplicities=[3, 3],   # sum=6 = 3+2+1
    knots=[0.0, 1.0],
)

# PCURVE: straight LINE in UV [0,10] at V=0.
# This is the WRONG pcurve: the 3D arc bows upward but the pcurve is flat at V=0.
# The endpoint-bias projection maps parameter t=0.5 to U=5 on the PCURVE,
# but the actual 3D point at t=0.5 is (5,1,0) not (5,0,0), so PCURVE is divergent.
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 10.0)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{surf.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom',#{bspline_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
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
