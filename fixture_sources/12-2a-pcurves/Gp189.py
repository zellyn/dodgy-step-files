"""Gp189 — EDGE_CURVE's associated_geometry lists a PCURVE entity that
itself fails to translate (malformed PCURVE, not a null `$` slot),
exercising the "listed pcurve fails to translate" mode of
stp-missing-pcurve-projection (PARTIAL, missing 1 of 2 -- the no-
pcurve->projection mode is already solid via Gp001/Gp035/Gp042; this
fixture targets the other trigger mode).

Work packet D2, item `stp-missing-pcurve-projection` (PARTIAL, missing 1
of 2), problem_id `stp-missing-pcurve-projection`: "the listed pcurve(s)
fail to translate ... rather than leaving the edge without any 2D trim,
OCCT defers and computes the pcurve later by projecting the already-
built 3D edge onto the face's surface."
(StepToTopoDS_TranslateEdgeLoop::Init, StepToTopoDS_TranslateEdgeLoop.
cxx:475-479,539-557 -- pcurve in the associated_geometry list fails to
translate -> hasPcurve=False, aTool.ComputePCurve(True) defers to
projection; :690-708 -- ShapeFix_EdgeProjAux projects; if projection
fails the pcurve is removed.)

Distinctness from Gp012 (struck as a bogus citation for this class):
Gp012's SEAM_CURVE associated_geometry contains `(#pc,$)` -- one slot is
a NULL `$`, which is the "no pcurve entity at all" mode already covered
by Gp001/Gp035/Gp042. This fixture instead lists a REAL, non-null PCURVE
entity reference whose OWN internal structure is malformed, so the
translator must actually attempt and fail the pcurve-specific
conversion (not just see an absent slot).

Mechanism: A half-cylinder face (u in [0,pi], v in [0,1]), the same
4-edge idiom as Gp035. The left seam edge's SURFACE_CURVE carries a
genuine 3D LINE (correct) and an associated_geometry list containing ONE
real, non-null PCURVE entity -- but that PCURVE's DEFINITIONAL_
REPRESENTATION `items` list references a LINE built from 3-coordinate
(3D) CARTESIAN_POINT/DIRECTION entities instead of the 2-coordinate ones
a pcurve's UV-space LINE must use -- a wrong-dimensionality item, the
kind of bug a producer's export code genuinely commits when it
accidentally wires a 3D curve builder into a 2D pcurve slot. The other
three edges (bottom arc, right seam, top arc) are correct SURFACE_
CURVEs, matching Gp035's structure so the face is well-formed except for
this one malformed pcurve.

Empirical note (evidence-based, not spec-literal): the packet's obvious
first attempt -- a DEFINITIONAL_REPRESENTATION item that is a totally
wrong entity TYPE (a bare CARTESIAN_POINT standing in for a curve) --
was built and tested first. It reads and even transfers-roots without a
caught Python exception, but SEGFAULTS OCCT 7.8.1 (OCP) during the
ADVANCED_FACE's wire-fixing pass once that malformed edge sits inside a
closed 4-edge loop next to other pcurve'd edges (confirmed reproducible:
a single-edge, non-looped minimal repro of the SAME item does NOT crash,
but the identical item inside a 4-edge closed loop crashes 100% of the
time under both healing=True and healing=False). A segfault is not a
Python-catchable "except" outcome -- it kills the interpreter -- so that
construction was DISCARDED as unsafe for this corpus's live harness/CI,
not shipped. The wrong-dimensionality LINE used below was verified live
via `BRep_Tool.CurveOnSurface` on the translated shape: the left seam
edge's own malformed PCURVE item is silently dropped, and OCCT instead
supplies a fresh pcurve computed via projection (u constant at 0, v
running 0->1 -- exactly the correct projected result for that physical
edge) -- a clean, decisive, non-crashing demonstration of the "listed
pcurve fails to translate -> defer to projection" mechanism.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp189",
    defect=(
        "Left seam EDGE_CURVE on CYLINDRICAL_SURFACE: SURFACE_CURVE wraps a "
        "correct 3D LINE plus a real (non-null) PCURVE in associated_geometry, "
        "but that PCURVE's DEFINITIONAL_REPRESENTATION items list references a "
        "LINE built from 3-coordinate (3D) point/direction entities -- wrong "
        "dimensionality for a 2D pcurve item -- so OCCT's pcurve-specific "
        "conversion fails and drops it while the 3D LINE stays intact; verified "
        "live that OCCT then supplies a projected pcurve instead (u=0 constant, "
        "v: 0->1) -- 'listed pcurve fails to translate' mode (contrast Gp012's "
        "null $ slot and Gp035's fully absent pcurve)"
    ),
)

# Cylindrical surface: radius 1, axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D vertices (same layout as Gp035).
p_a = f.cartesian_point((1.0, 0.0, 0.0))
p_b = f.cartesian_point((-1.0, 0.0, 0.0))
p_a_top = f.cartesian_point((1.0, 0.0, 1.0))
p_b_top = f.cartesian_point((-1.0, 0.0, 1.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_a_top = f.vertex_point(p_a_top)
v_b_top = f.vertex_point(p_b_top)

d_up = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- THE DEFECT: left seam edge -- correct 3D LINE, but a real PCURVE
# entity whose DEFINITIONAL_REPRESENTATION item is a LINE built from
# 3-coordinate (3D) point/direction entities -- wrong dimensionality for
# a 2D pcurve item, so its own conversion fails while the 3D LINE is fine.
left_line_3d = f.line(p_a, vec_up)
bad_3d_pt = f.cartesian_point((0.3, 0.0, 0.0))
bad_3d_dir = f.direction((0.0, 1.0, 0.0))
bad_3d_vec = f.vector(bad_3d_dir, 1.0)
bad_line = f._emit_raw(
    f"LINE('wrong_dim_pcurve_item',#{bad_3d_pt.eid},#{bad_3d_vec.eid})"
)
bad_pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bad_def',(#{bad_line.eid}),#{prc.eid})"
)
bad_pcurve = f._emit_raw(f"PCURVE('left_bad_pc',#{cyl.eid},#{bad_pc_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_seam_malformed_pc',#{left_line_3d.eid},"
    f"(#{bad_pcurve.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_malformed_pc',#{v_a.eid},#{v_a_top.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam at u=pi: correct SURFACE_CURVE with PCURVE ----
right_line_3d = f.line(p_b, vec_up)
pc_right_start = f.cartesian_point((math.pi, 0.0))
pc_right_dir = f.direction((0.0, 1.0))
pc_right_vec = f.vector(pc_right_dir, 1.0)
pc_right_line = f.line(pc_right_start, pc_right_vec)
pc_right_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_seam',#{cyl.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_seam',#{right_line_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_seam',#{v_b.eid},#{v_b_top.eid},#{sc_right.eid},.T.)"
)

# ---- Bottom arc: half-circle from A to B at z=0, u: 0->pi ----
arc_ctr = f.cartesian_point((0.0, 0.0, 0.0))
arc_zaxis = f.direction((0.0, 0.0, 1.0))
arc_xaxis = f.direction((1.0, 0.0, 0.0))
arc_axis = f.axis2_placement_3d(arc_ctr, arc_zaxis, arc_xaxis)
circle_bot_3d = f.circle(arc_axis, 1.0)
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, math.pi)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{circle_bot_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Top arc: half-circle from A_top to B_top at z=1 ----
top_ctr = f.cartesian_point((0.0, 0.0, 1.0))
top_axis = f.axis2_placement_3d(top_ctr, arc_zaxis, arc_xaxis)
circle_top_3d = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir = f.direction((1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, math.pi)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{circle_top_3d.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_a_top.eid},#{v_b_top.eid},#{sc_top.eid},.T.)"
)

# Loop: bot_arc(fwd) -> right(fwd) -> top(rev) -> left(rev)
loop = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top, False),
    f.oriented_edge(edge_left, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
