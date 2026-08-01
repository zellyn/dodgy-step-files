"""Gp196 — Seam edge whose two banks are declared as 2D CIRCLEs: the forward
pcurve is indeterminate and the edge translation hard-fails
(stp-seam-pcurve-selection, PARTIAL, missing subvariant: "forward pcurve
indeterminate -> edge translation hard-fails").

Catalog claim: StepToTopoDS_TranslateEdgeLoop::Init
(StepToTopoDS_TranslateEdgeLoop.cxx:518-633) must decide, for a seam edge
carrying two pcurves, WHICH of the two is the forward one for this
edge/wire/face orientation combination. It delegates that decision to
`ShapeAnalysis_Curve::SelectForwardSeam(C2d1, C2d2)`; when that returns 0
the edge is NOT guessed at -- it is hard-failed with
`TP->AddFail(EC, " Seam curve not mapped")`, `done = Standard_False`
(:596-601), which then sinks the whole wire (:680-683 "At least one edge
failed : wire not done") and with it the face.

Every prior fixture in this class (Gs193, Gp013, Gp011, Gs028, Twi022,
Gp190) succeeds with shape(1); none of them reaches the hard-fail branch.

Mechanism: `SelectForwardSeam` can only reason about pcurves it can reduce
to a 2D line -- it downcasts each pcurve to `Geom2d_Line`, and failing
that to `Geom2d_BoundedCurve` (from whose start/end points it synthesises a
line). A `Geom2d_Circle` is NEITHER: it derives from `Geom2d_Conic`, not
from `Geom2d_BoundedCurve`. So a seam whose two banks are declared as 2D
CIRCLEs rather than 2D LINEs makes both downcasts fail and the selector
returns its initial 0 -- the "cannot decide" value.

This fixture is the canonical closed-cylinder face (bottom circle, seam up,
top circle reversed, seam down -- the seam EDGE_CURVE referenced TWICE in
the one EDGE_LOOP, the formal-seam encoding this class already covers)
whose seam geometry is a SEAM_CURVE carrying two DISTINCT pcurves, one per
bank at u=0 and u=2*pi -- and each of those two pcurves' definitional
representation holds a 2D CIRCLE ('seam_bank_u0_circle_pcurve',
'seam_bank_u2pi_circle_pcurve') instead of the usual 2D LINE. Both circles
genuinely pass through their bank's two seam endpoints (centre (u_bank,0.5),
radius 0.5, endpoints (u_bank,0) and (u_bank,1)), so the bytes describe a
coherent, merely-curved pcurve, not nonsense.

The seam edge's start and end vertices are deliberately DISTINCT
(v_seam_bottom at z=0, v_seam_top at z=1). That matters: :667-675 swallows
a failed edge and resets `done` back to true when the edge's STEP start and
end vertex entities are the same object, so a full-circle seam (Gp011's
shape) would hide this very failure.

Byte assertions:
  - contains(b'seam_bank_u0_circle_pcurve')
  - contains(b'seam_bank_u2pi_circle_pcurve')
  - contains(b'SEAM_CURVE')
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 1

Tier-3 assertions:
  - shape_null == False
  - n_faces_total == 1
  - n_edges_total == 0
  - n_vertices_total == 0
  - face[0].surface_type == "cylinder"

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1): see the catalog
entry's Expected-validation line. Live-verified: the transfer check list
carries the FAIL " Seam curve not mapped" TWICE (once per traversal of the
twice-referenced seam edge), followed by "At least one edge failed : wire
not done", " EdgeLoop not mapped to TopoDS" and "No Outer Bound : Face not
done" -- the exact cascade the cited lines predict. The transferred shape
is therefore the cylinder face with NO wire at all: n_edges_total == 0,
n_vertices_total == 0, face area 8e+100 (the unbounded natural-surface
placeholder). That placeholder IS the claim here, exactly as for Tfa252,
so this fixture is listed in `_tier3_lint.EXEMPT_PLACEHOLDER`.

Perturbation control (byte-level A/B): replacing each pcurve's 2D CIRCLE
with a 2D LINE spanning the same two bank endpoints -- changing nothing
else -- makes all six check messages vanish and the face translate
normally (1 wire, 4 edges, 8 vertices, zero FAILs). The observable is
caused by the pcurve's 2D curve TYPE, exactly as the SelectForwardSeam
downcast chain predicts.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp196",
    defect=(
        "ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, axis +Z) whose "
        "single EDGE_LOOP is the canonical closed-cylinder boundary "
        "(bottom CIRCLE, seam forward, top CIRCLE reversed, seam reversed) "
        "-- so the seam EDGE_CURVE 'indeterminate_seam_edge' is referenced "
        "TWICE within the one wire, the formal-seam encoding. Its geometry "
        "is a SEAM_CURVE carrying two DISTINCT PCURVEs, one per bank "
        "(u=0 and u=2*pi), but each pcurve's definitional representation "
        "holds a 2D CIRCLE ('seam_bank_u0_circle_pcurve', "
        "'seam_bank_u2pi_circle_pcurve') rather than the usual 2D LINE. "
        "A Geom2d_Circle is neither a Geom2d_Line nor a Geom2d_BoundedCurve, "
        "so the forward-seam selector cannot reduce either bank to a "
        "direction and returns its cannot-decide value; the reader then "
        "hard-fails the seam edge rather than guessing, sinking the wire "
        "and the face. Seam edge IS wired into the EDGE_LOOP, "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)

R = 1.0
TWO_PI = 2.0 * math.pi

# ── Host surface: closed cylinder (NOT a plane -- a plane would make the
#    reader discard pcurves outright before the seam branch is reached) ─────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl = f.cylindrical_surface(cyl_plc, R)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Seam endpoints: DISTINCT vertices (see docstring: equal start/end
#    vertex entities would let :667-675 swallow the failure) ───────────────
p_bottom = f.cartesian_point((R, 0.0, 0.0))
p_top = f.cartesian_point((R, 0.0, 1.0))
v_bottom = f.vertex_point(p_bottom)
v_top = f.vertex_point(p_top)

# ── Seam 3D geometry: the vertical line at u=0, z: 0 -> 1 ─────────────────
seam_line3d = f.line(p_bottom, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0))


def circle_pcurve(u_bank: float, name: str):
    """2D CIRCLE pcurve through (u_bank, 0) and (u_bank, 1): centre
    (u_bank, 0.5), radius 0.5. Coherent geometry -- merely curved, and
    of a 2D curve TYPE the forward-seam selector cannot interpret."""
    c2d = f.cartesian_point((u_bank, 0.5))
    d2d = f.direction((1.0, 0.0))
    plc2d = f._emit_raw(f"AXIS2_PLACEMENT_2D('',#{c2d.eid},#{d2d.eid})")
    circ2d = f._emit_raw(f"CIRCLE('{name}',#{plc2d.eid},0.5)")
    drep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{circ2d.eid}),#{prc.eid})"
    )
    return f._emit_raw(f"PCURVE('',#{cyl.eid},#{drep.eid})")


pc_bank_u0 = circle_pcurve(0.0, "seam_bank_u0_circle_pcurve")
pc_bank_u2pi = circle_pcurve(TWO_PI, "seam_bank_u2pi_circle_pcurve")

seam_curve = f._emit_raw(
    f"SEAM_CURVE('',#{seam_line3d.eid},"
    f"(#{pc_bank_u0.eid},#{pc_bank_u2pi.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('indeterminate_seam_edge',#{v_bottom.eid},#{v_top.eid},"
    f"#{seam_curve.eid},.T.)"
)

# ── Bottom and top boundary circles (ordinary 3D-only edges) ──────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)), cyl_zdir, cyl_xdir)
bot_circle = f.circle(bot_plc, R)
e_bottom = f.edge_curve(v_bottom, v_bottom, bot_circle, name="cyl_bottom_edge")

top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 1.0)), cyl_zdir, cyl_xdir)
top_circle = f.circle(top_plc, R)
e_top = f.edge_curve(v_top, v_top, top_circle, name="cyl_top_edge")

# ── Canonical closed-cylinder loop: the seam edge appears TWICE ───────────
loop = f.edge_loop([
    f.oriented_edge(e_bottom, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
