"""Gp030 — Bent / polyline-form B_SPLINE pcurve from PRO/E IGES.

Catalog claim (05-occt-shapefix.md F061, ShapeFix_Wire.cxx): PRO/E exports
contain pcurves with sharp bends, authored as degree-1 B_SPLINE_CURVE_WITH_KNOTS
in .POLYLINE_FORM. with vendor-specific interior knot multiplicities. These
polyline-form pcurves must be protected from generic intersection-fix routines
that would otherwise corrupt them.

Fixture: A face on a CYLINDRICAL_SURFACE whose seam edge carries a pcurve that
is a degree-1 B_SPLINE_CURVE_WITH_KNOTS in .POLYLINE_FORM. (the PRO/E idiom).
The pcurve has 3 control points forming an L-shape in UV — a deliberate sharp
bend at the midpoint — with knot multiplicity 2 at the interior knot (degree 1,
so multiplicity = degree means C-1, i.e. a genuine breakpoint). A generic
intersection-fix routine, not recognising the PRO/E idiom, would alter the
interior vertex to remove the bend. The byte assertions require SURFACE_CURVE,
EDGE_CURVE, and at least one PCURVE entity.

The four-edge face loop is: left_seam (u=0) -> bot_arc -> right_seam (u=2pi) ->
top_arc (reversed). The defect is on the left seam edge pcurve only.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp030",
    defect=(
        "PRO/E STEP: seam edge pcurve is degree-1 B_SPLINE_CURVE_WITH_KNOTS in "
        ".POLYLINE_FORM. with 3 control points forming an L-bend in UV; interior "
        "knot multiplicity=2=degree makes it C-1 (true breakpoint); generic "
        "ShapeFix_Wire intersection-fix would corrupt this vendor pcurve"
    ),
)

# Override FILE_NAME header to carry the 'Pro/ENGINEER' originating_system
# fingerprint — the catalog says PRO/E files are identifiable by that field
# and downstream ShapeFix_Wire branches on it.
def _render_header():
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
        f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
        f"'cad-research-suite','Pro/ENGINEER','');\n"
        f"FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 3 1 1 }}'));\n"
        "ENDSEC;"
    )
f._render_header = _render_header  # type: ignore[method-assign]

# Cylindrical surface: radius 1, axis Z, height 1.
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
cyl   = f.cylindrical_surface(plc, 1.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices at the two seam locations:
#   seam at u=0   -> 3D (1, 0, *)
#   seam at u=2pi -> 3D (1, 0, *)  (same physical position, opposite UV band)
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- Left seam edge at u=0: 3D vertical line ----
# THE DEFECT: pcurve is a degree-1 B_SPLINE in .POLYLINE_FORM. with a bend.
# Control points in UV:
#   cp0 = (0.0, 0.0)  — correct start
#   cp1 = (0.3, 0.5)  — bent midpoint (off the straight line u=0)
#   cp2 = (0.0, 1.0)  — correct end
# This L-bend is the PRO/E signature. Knot vector: (0, 0, 0.5, 0.5, 1.0, 1.0)
# => interior knot at 0.5 with multiplicity 2 = degree+1 for C-1 (true kink).
# In .POLYLINE_FORM., degree=1 means each segment is linear between control points.
left_line_3d = f.line(p_bot, vec_up)

cp0 = f.cartesian_point((0.0, 0.0))
cp1 = f.cartesian_point((0.3, 0.5))
cp2 = f.cartesian_point((0.0, 1.0))

# Degree-1 B_SPLINE_CURVE_WITH_KNOTS, .POLYLINE_FORM., 3 poles:
# knots=(0.0, 0.5, 1.0), multiplicities=(2,2,2) => C-1 at interior knot
pc_left_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('proe_polyline',1,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),.POLYLINE_FORM.,.F.,.F.,"
    f"(2,2,2),(0.0,0.5,1.0),.UNSPECIFIED.)"
)
pc_left_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left_bend',(#{pc_left_bspline.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(
    f"PCURVE('proe_bent_pcurve',#{cyl.eid},#{pc_left_def.eid})"
)
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_seam',#{left_line_3d.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_seam',#{v_bot.eid},#{v_top.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam edge at u=2pi: correct straight pcurve LINE ----
right_line_3d  = f.line(p_bot, vec_up)
pc_right_start = f.cartesian_point((2.0 * math.pi, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_seam',#{cyl.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_seam',#{right_line_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_seam',#{v_bot.eid},#{v_top.eid},#{sc_right.eid},.T.)"
)

# ---- Bottom arc: full circle at z=0, u: 0->2pi ----
bot_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
bot_zd    = f.direction((0.0, 0.0, 1.0))
bot_xd    = f.direction((1.0, 0.0, 0.0))
bot_axis  = f.axis2_placement_3d(bot_ctr, bot_zd, bot_xd)
bot_circle = f.circle(bot_axis, 1.0)
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 2.0 * math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{sc_bot.eid},.T.)"
)

# ---- Top arc: full circle at z=1, u: 0->2pi ----
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, bot_zd, bot_xd)
top_circle = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, 2.0 * math.pi)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{sc_top.eid},.T.)"
)

# Loop: bot(fwd) -> right(fwd) -> top(rev) -> left(rev)
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # v_bot->v_bot (full circle)
    f.oriented_edge(edge_right, True),   # v_bot->v_top at u=2pi
    f.oriented_edge(edge_top,   False),  # v_top->v_top (reversed)
    f.oriented_edge(edge_left,  False),  # v_top->v_bot at u=0 (DEFECT pcurve)
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
