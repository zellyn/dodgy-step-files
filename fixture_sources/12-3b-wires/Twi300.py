"""Twi300 — Edge trimmed onto an unbounded LINE by a vertex placed
enormously far along the line's own direction, far outside the face's
otherwise normal 1-unit scale: projected point with an effectively
infinite curve parameter (stp-makeedge-validity-fallback, PARTIAL, missing
subvariant "a projected point has an infinite curve parameter").

Catalog claim: STEP's LINE entity is UNBOUNDED by definition -- OCCT
represents an untrimmed LINE's natural parameter domain using its own
"infinite" sentinel (Precision::Infinite(), 1e100) rather than a genuine
finite range. When BRepLib_MakeEdge (via StepToTopoDS_TranslateEdge::
MakeFromCurve3D) projects a vertex onto such a curve and the vertex sits
far enough from the "intended" local segment (here: 1e8 units along the
line's own direction, vs. the face's otherwise normal ~1-unit scale), the
computed/fallback parameter is effectively unbounded -- a distinct
DecodeMakeEdgeError classification (StepToTopoDS_TranslateEdge.cxx
:70-131) from Gs029's "trim parameter out of the curve's own declared
range" (that case has an explicit, finite, merely-wrong range; this case
has no meaningful finite parameter for the fallback to fall back TO,
because the curve itself is conceptually unbounded). MakeFromCurve3D still
force-builds the raw edge (:483-489) rather than aborting.

Mechanism: a triangular PLANE face (z=0) with vertices v0=(0,0,0),
v_far=(1e8,0,0), v2=(0,1,0). Edge e_far (v0 -> v_far) sits on a LINE
through the origin along +X -- unbounded by STEP's own LINE semantics --
trimmed at one end by a vertex 1e8 units out, one hundred million times
the face's other ~1-unit edges (e_far -> v2, v2 -> v0). ADVANCED_FACE ->
OPEN_SHELL -> SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'far_along_unbounded_line_vertex')
  - count_entity_def(b'EDGE_CURVE') == 3
  - count_entity_def(b'LINE') == 3

Tier-3 assertions:
  - face[0].surface_type == "plane"

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
(live-verified: reads without crashing, brepcheck.valid=True; edge e_far's
length reads back as exactly 1e8 -- confirming the enormous parameter was
successfully absorbed/force-built into a genuine (if extreme-aspect-ratio)
edge rather than causing the read to abort or the edge to be dropped,
matching the class's "force-build anyway, log a diagnostic instead of
failing" claim.)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi300",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references a 3-edge triangular EDGE_LOOP: "
        "e_far (v0(0,0,0) -> far_along_unbounded_line_vertex(1e8,0,0), a "
        "LINE along +X through the origin -- unbounded by STEP's own LINE "
        "semantics, trimmed by a vertex 1e8 units out, effectively an "
        "infinite curve parameter relative to the face's normal ~1-unit "
        "scale), e_diag (far_along_unbounded_line_vertex -> v2(0,1,0)), "
        "e_close (v2 -> v0); the enormous trim distance on e_far IS the "
        "mechanism (DecodeMakeEdgeError / MakeFromCurve3D fallback "
        "force-build, infinite-parameter classification); EDGE_LOOP IS "
        "wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never "
        "orphaned"
    ),
)

import math

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

FAR = 1.0e8

v0    = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_far = f.vertex_point(f.cartesian_point((FAR, 0.0, 0.0)), name="far_along_unbounded_line_vertex")
v2    = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))


def mk_edge(pa, pb, va, vb):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln = f.line(f.cartesian_point(pa), vec)
    return f.edge_curve(va, vb, ln)


e_far   = mk_edge((0.0, 0.0, 0.0), (FAR, 0.0, 0.0), v0, v_far)
e_diag  = mk_edge((FAR, 0.0, 0.0), (0.0, 1.0, 0.0), v_far, v2)
e_close = mk_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), v2, v0)

loop = f.edge_loop([
    f.oriented_edge(e_far, True),
    f.oriented_edge(e_diag, True),
    f.oriented_edge(e_close, True),
])

face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
