"""Twi302 — Small SEAM edge on a periodic face, adjacent to another seam
segment: requires seam-with-seam merge (tkshh-wire-small-edge, PARTIAL,
missing subvariant "small seam edge on a periodic face, seam-with-seam
merge only").

Catalog claim: ShapeFix_Wireframe::MergeSmallEdges must merge a small edge
below tolerance into a neighbor (ShapeFix_Wireframe.cxx:590 method,
:816 ReplaceFirst=JoinEdges, :887 re-check merged result); when BOTH the
small edge and its neighbor are themselves seam edges on a periodic
surface (each individually recognized via IsSeamCurve's "referenced twice
in one EdgeLoop" branch), the merge must special-case: replace TWO seam
segments with ONE, re-deriving the surviving edge's pcurve to span the
full combined parameter range, rather than merging a small seam into an
ordinary neighbor (which Twi013/N010/N014/Twi138/Twi237/Twi184 already
cover).

Mechanism: a full-360 CYLINDRICAL_SURFACE (radius 1, axis +Z) face whose
U=0 boundary — normally a SINGLE seam EDGE_CURVE spanning the whole height
H=2 (Gp013's pattern, one physical line used twice in the wire, once per
traversal direction) — is split into TWO consecutive seam segments:
seam_lower_segment (z: 0 -> H-eps, real length ~2.0) and
seam_upper_small_segment (z: H-eps -> H, length eps=1e-6, below the
survival-margin threshold live-tested below). Each is an ordinary LINE-geometry EDGE_CURVE (pcurve
auto-derived by StepToTopoDS, same convention as Twi013/Twi021's edges);
what makes EACH one a seam is IsSeamCurve's "EDGE_CURVE referenced twice
within the same EdgeLoop on the given surface" branch — both seam_lower
and seam_upper are referenced TWICE in the one FACE_OUTER_BOUND EDGE_LOOP
(once per traversal direction). seam_upper's small length is directly
ADJACENT, on both sides of the wire traversal, to seam_lower's two seam
references — not to any ordinary edge — isolating the seam-with-seam
merge path in ShapeFix_Wireframe::MergeSmallEdges specifically (distinct
from Twi013/N010/N014/Twi138/Twi237/Twi184, which all merge a small edge
into an ordinary neighbor).

EDGE_LOOP (6 ORIENTED_EDGEs, 4 distinct EDGE_CURVEs):
  bot_arc(v_b->v_b, full circle, z=0)
  -> seam_lower fwd (v_b->v_mid)
  -> seam_upper fwd (v_mid->v_t, SMALL)
  -> top_arc(v_t->v_t, full circle, reversed, z=H)
  -> seam_upper rev (v_t->v_mid, SMALL)
  -> seam_lower rev (v_mid->v_b)
FACE_OUTER_BOUND -> ADVANCED_FACE -> OPEN_SHELL -> SHELL_BASED_SURFACE_MODEL
-> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'seam_lower_segment')
  - contains(b'seam_upper_small_segment')
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 4

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - brepcheck.valid == True

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi302",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a full-360 CYLINDRICAL_SURFACE "
        "(radius 1, axis +Z, height 2); the U=0 boundary is split into TWO "
        "consecutive plain-LINE seam segments instead of Gp013's single "
        "one: seam_lower_segment (z:0->1.999999, real length) and "
        "seam_upper_small_segment (z:1.999999->2, length 1e-6); each is an "
        "ordinary EDGE_CURVE (pcurve auto-derived) referenced TWICE in the "
        "FACE_OUTER_BOUND EDGE_LOOP (formal seam per IsSeamCurve's "
        "twice-in-one-wire branch); seam_upper_small_segment's smallness is "
        "adjacent ON BOTH SIDES to seam_lower_segment's two seam "
        "references (not to any ordinary edge) -- isolates the "
        "seam-with-seam merge path in ShapeFix_Wireframe::MergeSmallEdges; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL; never orphaned"
    ),
)

R = 1.0
H = 2.0
EPS = 1e-6  # live-tested: below ~1e-7 the double-seam wire is rejected
            # outright by StepToTopoDS/ShapeFix (whole wire dropped, face
            # left with 0 edges) rather than merged -- 1e-6 sits safely
            # above that platform-risky boundary while still being a
            # genuine sliver (ratio 5e-7 of the H=2 seam height)
H_MID = H - EPS

# ── CYLINDRICAL_SURFACE: axis +Z, radius 1, placement at origin ──────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R:.10f})")

# ── Vertices: bottom (z=0), mid (z=H-eps), top (z=H), all at angle theta=0 ────
v_b   = f.vertex_point(f.cartesian_point((R, 0.0, 0.0)))
v_mid = f.vertex_point(f.cartesian_point((R, 0.0, H_MID)))
v_t   = f.vertex_point(f.cartesian_point((R, 0.0, H)))

# NOTE (live-tested 2026-07-13): an earlier version of this fixture built
# each seam segment as a SURFACE_CURVE with two explicit PCURVE banks
# (u=0 / u=2*pi), mirroring Gp013's formal-seam encoding exactly. That
# construction loaded (occt=shape(1)) but StepToTopoDS/ShapeFix silently
# DROPPED the entire wire (0 wires/edges/vertices survived, face left with
# no bound at all) rather than merging — a genuine but undesired failure
# mode, not the seam-merge behavior under test. Per IsSeamCurve's OTHER
# detection branch ("or an EDGE_CURVE referenced twice within the same
# EdgeLoop on the given surface" — no explicit dual-pcurve SURFACE_CURVE
# required), a PLAIN EDGE_CURVE (ordinary LINE, pcurve auto-derived by
# StepToTopoDS like Twi013/Twi021's edges) referenced TWICE in one wire on
# this periodic CYLINDRICAL_SURFACE is sufficient to be recognized as a
# seam. This simpler encoding survives translation with the wire intact.


def _seam_edge(vlo, vhi, zlo, zhi, name):
    """A vertical seam EDGE_CURVE at theta=0 from z=zlo to z=zhi — ordinary
    LINE geometry, referenced TWICE in the wire (forward + reverse) is what
    makes it a seam (IsSeamCurve's twice-in-one-wire branch)."""
    d = f.direction((0.0, 0.0, 1.0))
    vec = f.vector(d, zhi - zlo)
    line3d = f._emit_raw(f"LINE('{name}',#{f.cartesian_point((R, 0.0, zlo)).eid},#{vec.eid})")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{vlo.eid},#{vhi.eid},#{line3d.eid},.T.)")


seam_lower = _seam_edge(v_b, v_mid, 0.0, H_MID, "seam_lower_segment")
seam_upper = _seam_edge(v_mid, v_t, H_MID, H, "seam_upper_small_segment")

# ── Bottom / top full-circle arcs (same vertex both ends, like Gp013) ────────
bot_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), cyl_zdir, cyl_xdir)
bot_circ = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},{R:.10f})")
bot_arc = f._emit_raw(f"EDGE_CURVE('',#{v_b.eid},#{v_b.eid},#{bot_circ.eid},.T.)")

top_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, H)), cyl_zdir, cyl_xdir)
top_circ = f._emit_raw(f"CIRCLE('',#{top_plc.eid},{R:.10f})")
top_arc = f._emit_raw(f"EDGE_CURVE('',#{v_t.eid},#{v_t.eid},#{top_circ.eid},.T.)")

# ── EDGE_LOOP: bot_arc -> seam_lower fwd -> seam_upper fwd -> top_arc(rev) ────
#    -> seam_upper rev -> seam_lower rev ─────────────────────────────────────
oe_bot        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_arc.eid},.T.)")
oe_lower_fwd  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_lower.eid},.T.)")
oe_upper_fwd  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_upper.eid},.T.)")
oe_top        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_arc.eid},.F.)")
oe_upper_rev  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_upper.eid},.F.)")
oe_lower_rev  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_lower.eid},.F.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_lower_fwd.eid},#{oe_upper_fwd.eid},"
    f"#{oe_top.eid},#{oe_upper_rev.eid},#{oe_lower_rev.eid}))"
)

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
