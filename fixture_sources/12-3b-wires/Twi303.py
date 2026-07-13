"""Twi303 — Small edge at a sharp corner (non-collinear neighbors on both
sides): cannot be merged into either neighbor, must be dropped with a
connectivity re-check (tkshh-wire-small-edge, PARTIAL, missing subvariant
"small edge that cannot be merged and is dropped (drop mode), with
connectivity re-check").

Catalog claim: ShapeFix_Wireframe::MergeSmallEdges (ShapeFix_Wireframe.cxx
:590 method) tries to fold a small edge into a neighbor sharing the same
face set; when the merge-eligibility guards reject BOTH neighbors (angle
limit -- the small edge is not roughly collinear with either straight
neighbor, so absorbing it would require re-typing the neighbor's own
curve rather than a simple extension), the healer falls back to "drop
mode" (:927 `else if(aModeDrop)`): remove the small edge outright and
reconnect its two neighbors directly to each other, adjusting the shared
vertex (a connectivity re-check), rather than extending either curve.
Distinct from Twi013/N010/N014/Twi138/Twi237/Twi184, whose sliver always
sits collinear with (or between colinear-compatible) straight neighbors
and is mergeable by simple extension.

Mechanism: a pentagon-ish planar face on a PLANE (z=0). Four of the five
wire edges form a near-square (bottom, right, top, left); the fifth is a
tiny DIAGONAL notch edge inserted at the top-right corner, between the
(near-vertical) right edge and the (near-horizontal) top edge -- so the
notch is emphatically NOT collinear with either neighbor (their tangent
directions differ from the notch's by ~45 degrees on each side, vs. the
~180-degree collinear continuation Twi013's sliver has with its straight
run). A healer that tries to "extend" either straight neighbor to absorb
the diagonal notch would have to change that neighbor's curve direction,
violating the angle-limit merge-eligibility guard -- forcing drop mode:
delete the notch, snap the right edge's and top edge's now-disconnected
endpoints together into one shared corner vertex.

EDGE_LOOP (5 edges): bottom(A->B) -> right(B->C) -> notch(C->D, SMALL
DIAGONAL) -> top(D->E) -> left(E->A).
  A=(0,0,0) B=(1,0,0) C=(1,1-eps,0) D=(1-eps,1,0) E=(0,1,0), eps=1e-6.

Byte assertions:
  - contains(b'sharp_corner_notch_edge')
  - count_entity_def(b'EDGE_CURVE') == 5
  - count_entity_def(b'PLANE') == 1

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 4
  - brepcheck.valid == True

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi303",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references a 5-edge EDGE_LOOP: bottom(A->B), "
        "right(B->C, near-vertical), sharp_corner_notch_edge(C->D, tiny "
        "DIAGONAL, length ~1.414e-6, NOT collinear with either neighbor), "
        "top(D->E, near-horizontal), left(E->A); A=(0,0,0) B=(1,0,0) "
        "C=(1,1-1e-6,0) D=(1-1e-6,1,0) E=(0,1,0); the notch's non-collinear "
        "geometry on both sides forces ShapeFix_Wireframe::MergeSmallEdges' "
        "drop-mode branch (angle-limit merge guard rejects extension into "
        "either neighbor) rather than a simple collinear-extension merge; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL; never orphaned"
    ),
)

EPS = 1e-6

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)


def mk_edge(pa, pb, va, vb, name=""):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln = f._emit_raw(f"LINE('{name}',#{f.cartesian_point(pa).eid},#{vec.eid})")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{va.eid},#{vb.eid},#{ln.eid},.T.)")


A = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
B = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
C = f.vertex_point(f.cartesian_point((1.0, 1.0 - EPS, 0.0)))
D = f.vertex_point(f.cartesian_point((1.0 - EPS, 1.0, 0.0)))
E = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

e_bottom = mk_edge((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), A, B, "bottom_edge")
e_right  = mk_edge((1.0, 0.0, 0.0), (1.0, 1.0 - EPS, 0.0), B, C, "right_edge")
e_notch  = mk_edge((1.0, 1.0 - EPS, 0.0), (1.0 - EPS, 1.0, 0.0), C, D, "sharp_corner_notch_edge")
e_top    = mk_edge((1.0 - EPS, 1.0, 0.0), (0.0, 1.0, 0.0), D, E, "top_edge")
e_left   = mk_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), E, A, "left_edge")

loop = f.edge_loop([
    f.oriented_edge(e_bottom, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_notch,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])

face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
