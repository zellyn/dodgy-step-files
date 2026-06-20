"""Gp031 — Cylinder represented twice as duplicate CYLINDRICAL_SURFACE instances.

Catalog claim (05-occt-shapefix.md F063, ShapeBuild_Edge.cxx:647): After an
IGES BRep round-trip, a cylindrical face appears with two distinct but
identically-defined CYLINDRICAL_SURFACE instances (e.g. #20 and #21) where
different ADVANCED_FACEs use different copies. A single 3D edge then has two
pcurves stored on these supposedly-same surfaces; pcurves on the second copy
disagree with those on the first (same UV path, different surface handle). The
kernel must canonicalize duplicate analytic surfaces and re-bind pcurves.

Fixture: Two ADVANCED_FACEs forming a split cylinder (front half and back half),
each on its own distinct but geometrically identical CYLINDRICAL_SURFACE instance.
The shared split edge (at u=0/u=pi) has a SURFACE_CURVE listing TWO pcurves:
one pcurve on surface-1 (at u=0) and one on surface-2 (at u=pi). Because the
two surface instances are not recognized as identical, the pcurves appear to
reference different surfaces even though they're geometrically the same cylinder
— this is exactly the catalog defect (aliased pcurves across duplicate surfaces).

Both faces share one open shell so the topology is clearly connected; the defect
is at the geometry identity level, not connectivity.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp031",
    defect=(
        "Two ADVANCED_FACEs on distinct but identically-defined CYLINDRICAL_SURFACE "
        "instances (sor1, sor2); shared split edge SURFACE_CURVE has pcurve on sor1 "
        "(u=0) and pcurve on sor2 (u=pi); duplicate analytic surface identity lost "
        "after IGES BRep round-trip; kernel must canonicalize and rebind pcurves"
    ),
)

# Two identically-defined CYLINDRICAL_SURFACE instances (the defect: two copies).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc1  = f.axis2_placement_3d(orig, zdir, xdir)
cyl1  = f.cylindrical_surface(plc1, 1.0)  # instance 1

# Second identical placement and surface — this is the duplicate.
orig2 = f.cartesian_point((0.0, 0.0, 0.0))
zdir2 = f.direction((0.0, 0.0, 1.0))
xdir2 = f.direction((1.0, 0.0, 0.0))
plc2  = f.axis2_placement_3d(orig2, zdir2, xdir2)
cyl2  = f.cylindrical_surface(plc2, 1.0)  # instance 2 (geometrically identical)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices: the cylinder split edge at x=1 (u=0 on cyl1, u=pi on cyl2 if
# measuring from x=-1 on the back half). We use consistent 3D positions.
#   v_right_bot: (1, 0, 0) — at u=0 on cyl1, at u=pi on cyl2
#   v_right_top: (1, 0, 1)
#   v_left_bot:  (-1, 0, 0) — at u=pi on cyl1, at u=0 on cyl2
#   v_left_top:  (-1, 0, 1)

p_rb = f.cartesian_point(( 1.0, 0.0, 0.0))
p_rt = f.cartesian_point(( 1.0, 0.0, 1.0))
p_lb = f.cartesian_point((-1.0, 0.0, 0.0))
p_lt = f.cartesian_point((-1.0, 0.0, 1.0))
v_rb = f.vertex_point(p_rb)
v_rt = f.vertex_point(p_rt)
v_lb = f.vertex_point(p_lb)
v_lt = f.vertex_point(p_lt)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ============================================================
# THE DEFECT: the shared right split edge has ONE SURFACE_CURVE
# with TWO pcurves — one on cyl1, one on cyl2.
# After IGES round-trip, cyl1 and cyl2 are distinct handles even
# though geometrically identical; the reader cannot canonicalize.
# ============================================================
right_line_3d = f.line(p_rb, vec_up)

# pcurve on cyl1: at u=0 (the right edge is u=0 for the front half face on cyl1)
pc_r1_start = f.cartesian_point((0.0, 0.0))
pc_r1_dir   = f.direction((0.0, 1.0))
pc_r1_vec   = f.vector(pc_r1_dir, 1.0)
pc_r1_line  = f.line(pc_r1_start, pc_r1_vec)
pc_r1_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right_cyl1',(#{pc_r1_line.eid}),#{prc.eid})"
)
pcurve_r1 = f._emit_raw(f"PCURVE('right_on_cyl1',#{cyl1.eid},#{pc_r1_def.eid})")

# pcurve on cyl2: at u=pi (the right edge seen from back-half face on cyl2)
pc_r2_start = f.cartesian_point((math.pi, 0.0))
pc_r2_dir   = f.direction((0.0, 1.0))
pc_r2_vec   = f.vector(pc_r2_dir, 1.0)
pc_r2_line  = f.line(pc_r2_start, pc_r2_vec)
pc_r2_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right_cyl2',(#{pc_r2_line.eid}),#{prc.eid})"
)
pcurve_r2 = f._emit_raw(f"PCURVE('right_on_cyl2',#{cyl2.eid},#{pc_r2_def.eid})")

# SURFACE_CURVE with both pcurves — one per duplicate surface instance.
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_split',#{right_line_3d.eid},"
    f"(#{pcurve_r1.eid},#{pcurve_r2.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_split',#{v_rb.eid},#{v_rt.eid},#{sc_right.eid},.T.)"
)

# ============================================================
# Left split edge: shared edge at u=pi on cyl1, u=0 on cyl2
# Same defect pattern: two pcurves, one per surface instance.
# ============================================================
left_line_3d = f.line(p_lb, vec_up)

pc_l1_start = f.cartesian_point((math.pi, 0.0))
pc_l1_dir   = f.direction((0.0, 1.0))
pc_l1_vec   = f.vector(pc_l1_dir, 1.0)
pc_l1_line  = f.line(pc_l1_start, pc_l1_vec)
pc_l1_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left_cyl1',(#{pc_l1_line.eid}),#{prc.eid})"
)
pcurve_l1 = f._emit_raw(f"PCURVE('left_on_cyl1',#{cyl1.eid},#{pc_l1_def.eid})")

pc_l2_start = f.cartesian_point((0.0, 0.0))
pc_l2_dir   = f.direction((0.0, 1.0))
pc_l2_vec   = f.vector(pc_l2_dir, 1.0)
pc_l2_line  = f.line(pc_l2_start, pc_l2_vec)
pc_l2_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left_cyl2',(#{pc_l2_line.eid}),#{prc.eid})"
)
pcurve_l2 = f._emit_raw(f"PCURVE('left_on_cyl2',#{cyl2.eid},#{pc_l2_def.eid})")

sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_split',#{left_line_3d.eid},"
    f"(#{pcurve_l1.eid},#{pcurve_l2.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_split',#{v_lb.eid},#{v_lt.eid},#{sc_left.eid},.T.)"
)

# ============================================================
# Front-half face on cyl1: u in [0, pi] (front of cylinder)
# Edges: right_split(fwd), top_front(rev), left_split(rev), bot_front(fwd)
# ============================================================
# Bottom front arc: half-circle at z=0 from v_rb to v_lb, u: 0->pi
bot_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
bot_zd    = f.direction((0.0, 0.0, 1.0))
bot_xd    = f.direction((1.0, 0.0, 0.0))
bot_axis  = f.axis2_placement_3d(bot_ctr, bot_zd, bot_xd)
bot_front_circle = f.circle(bot_axis, 1.0)
pc_bf_start = f.cartesian_point((0.0, 0.0))
pc_bf_dir   = f.direction((1.0, 0.0))
pc_bf_vec   = f.vector(pc_bf_dir, math.pi)
pc_bf_line  = f.line(pc_bf_start, pc_bf_vec)
pc_bf_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_front',(#{pc_bf_line.eid}),#{prc.eid})"
)
pcurve_bf = f._emit_raw(f"PCURVE('bot_front',#{cyl1.eid},#{pc_bf_def.eid})")
sc_bf = f._emit_raw(
    f"SURFACE_CURVE('bot_front',#{bot_front_circle.eid},(#{pcurve_bf.eid}),.PCURVE_S1.)"
)
edge_bf = f._emit_raw(
    f"EDGE_CURVE('bot_front',#{v_rb.eid},#{v_lb.eid},#{sc_bf.eid},.T.)"
)

# Top front arc: half-circle at z=1 from v_rt to v_lt, u: 0->pi
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, bot_zd, bot_xd)
top_front_circle = f.circle(top_axis, 1.0)
pc_tf_start = f.cartesian_point((0.0, 1.0))
pc_tf_dir   = f.direction((1.0, 0.0))
pc_tf_vec   = f.vector(pc_tf_dir, math.pi)
pc_tf_line  = f.line(pc_tf_start, pc_tf_vec)
pc_tf_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_front',(#{pc_tf_line.eid}),#{prc.eid})"
)
pcurve_tf = f._emit_raw(f"PCURVE('top_front',#{cyl1.eid},#{pc_tf_def.eid})")
sc_tf = f._emit_raw(
    f"SURFACE_CURVE('top_front',#{top_front_circle.eid},(#{pcurve_tf.eid}),.PCURVE_S1.)"
)
edge_tf = f._emit_raw(
    f"EDGE_CURVE('top_front',#{v_rt.eid},#{v_lt.eid},#{sc_tf.eid},.T.)"
)

# Front face loop: bot_front(fwd) -> left_split(fwd) -> top_front(rev) -> right_split(rev)
# Traversal: v_rb->v_lb, v_lb->v_lt, v_lt->v_rt, v_rt->v_rb
loop_front = f.edge_loop([
    f.oriented_edge(edge_bf,    True),   # v_rb->v_lb
    f.oriented_edge(edge_left,  True),   # v_lb->v_lt
    f.oriented_edge(edge_tf,    False),  # v_lt->v_rt (reversed)
    f.oriented_edge(edge_right, False),  # v_rt->v_rb (reversed)
])
face_front = f.advanced_face([f.face_outer_bound(loop_front)], cyl1)

# ============================================================
# Back-half face on cyl2: u in [0, pi] (back half, on duplicate surface)
# ============================================================
bot_back_circle = f.circle(bot_axis, 1.0)  # same 3D circle geometry
pc_bb_start = f.cartesian_point((0.0, 0.0))
pc_bb_dir   = f.direction((1.0, 0.0))
pc_bb_vec   = f.vector(pc_bb_dir, math.pi)
pc_bb_line  = f.line(pc_bb_start, pc_bb_vec)
pc_bb_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_back',(#{pc_bb_line.eid}),#{prc.eid})"
)
pcurve_bb = f._emit_raw(f"PCURVE('bot_back',#{cyl2.eid},#{pc_bb_def.eid})")
sc_bb = f._emit_raw(
    f"SURFACE_CURVE('bot_back',#{bot_back_circle.eid},(#{pcurve_bb.eid}),.PCURVE_S1.)"
)
edge_bb = f._emit_raw(
    f"EDGE_CURVE('bot_back',#{v_lb.eid},#{v_rb.eid},#{sc_bb.eid},.T.)"
)

top_back_circle = f.circle(top_axis, 1.0)
pc_tb_start = f.cartesian_point((0.0, 1.0))
pc_tb_dir   = f.direction((1.0, 0.0))
pc_tb_vec   = f.vector(pc_tb_dir, math.pi)
pc_tb_line  = f.line(pc_tb_start, pc_tb_vec)
pc_tb_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_back',(#{pc_tb_line.eid}),#{prc.eid})"
)
pcurve_tb = f._emit_raw(f"PCURVE('top_back',#{cyl2.eid},#{pc_tb_def.eid})")
sc_tb = f._emit_raw(
    f"SURFACE_CURVE('top_back',#{top_back_circle.eid},(#{pcurve_tb.eid}),.PCURVE_S1.)"
)
edge_tb = f._emit_raw(
    f"EDGE_CURVE('top_back',#{v_lt.eid},#{v_rt.eid},#{sc_tb.eid},.T.)"
)

# Back face loop: bot_back(fwd) -> right_split(fwd) -> top_back(rev) -> left_split(rev)
# Traversal: v_lb->v_rb, v_rb->v_rt, v_rt->v_lt, v_lt->v_lb
loop_back = f.edge_loop([
    f.oriented_edge(edge_bb,    True),   # v_lb->v_rb
    f.oriented_edge(edge_right, True),   # v_rb->v_rt
    f.oriented_edge(edge_tb,    False),  # v_rt->v_lt (reversed)
    f.oriented_edge(edge_left,  False),  # v_lt->v_lb (reversed)
])
face_back = f.advanced_face([f.face_outer_bound(loop_back)], cyl2)

shell = f.open_shell([face_front, face_back])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
