"""Twi018 — Edge with start==end vertex but open curve (zero arc length).

Catalog claim: EDGE_CURVE references the same VERTEX_POINT for start and end
but the underlying curve is open (a LINE); the arc length is zero because both
endpoints collapse to the same point.

Mechanism IS the EDGE_CURVE referencing one VERTEX_POINT twice on an open LINE
geometry: the LINE's direction is valid but both #v and #v (same entity) serve
as start and end. The defect EDGE_CURVE IS referenced in an EDGE_LOOP which IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL that also
has a proper outer square; the degenerate edge IS wired as one slot of the loop.
Translator must drop the collapsed edge or synthesise a tiny line; if V1==V2
the edge contributes zero length and must not cause traversal to fail.

Reproducer: EDGE_CURVE('',#v,#v,#line,.T.) where #line is an open LINE segment
and both endpoints reference the same VERTEX_POINT entity.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') >= 4
  - contains(b'LINE')

Tier-3 assertions:
  - face[0].sliver_aspect_max_min > 1e6
  - face[0].surface_type == "plane"
  - n_edges_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi018",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with 5 ORIENTED_EDGEs; "
        "four edges form a 1×1 square with a sliver notch; "
        "one ORIENTED_EDGE wraps an EDGE_CURVE whose start and end both reference "
        "the same VERTEX_POINT entity at (1,1,0) on an open LINE — arc length zero; "
        "same-vertex-on-open-LINE EDGE_CURVE IS the mechanism; "
        "translator must drop collapsed edge or synthesise tiny line; "
        "defect edge IS wired into EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def mk_line_edge(pa, pb, va, vb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    if mag == 0.0:
        mag = 1.0
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point(pa), vec)
    return f.edge_curve(va, vb, ln)

# ── 1×1 square vertices ───────────────────────────────────────────────────────
v_00  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_10  = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
# v_11 used TWICE as start and end of the collapsed edge — IS the defect
v_11  = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
v_01  = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))

# ── Collapsed LINE edge: same VERTEX_POINT on both ends — IS the mechanism ────
# Direction is nominally +X, but both ends are identical so length = 0.
degenerate_dir = f.direction((1.0, 0.0, 0.0))
degenerate_vec = f.vector(degenerate_dir, 0.0)
degenerate_line_pt = f.cartesian_point((1.0, 1.0, 0.0))
degenerate_line = f.line(degenerate_line_pt, degenerate_vec)
# Both start and end reference v_11 — same entity, open LINE, zero arc length.
edge_collapsed = f._emit_raw(
    f"EDGE_CURVE('',#{v_11.eid},#{v_11.eid},#{degenerate_line.eid},.T.)"
)

# Four normal square edges
e_bot   = mk_line_edge((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), v_00, v_10)
e_right = mk_line_edge((1.0, 0.0, 0.0), (1.0, 1.0, 0.0), v_10, v_11)
e_top   = mk_line_edge((1.0, 1.0, 0.0), (0.0, 1.0, 0.0), v_11, v_01)
e_left  = mk_line_edge((0.0, 1.0, 0.0), (0.0, 0.0, 0.0), v_01, v_00)

# EDGE_LOOP wiring the collapsed edge in the middle of the square loop
oe_bot       = f.oriented_edge(e_bot,   True)
oe_right     = f.oriented_edge(e_right, True)
# Collapsed edge inserted between right and top:
oe_collapsed = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge_collapsed.eid},.T.)")
oe_top       = f.oriented_edge(e_top,   True)
oe_left      = f.oriented_edge(e_left,  True)

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_right.eid},"
    f"#{oe_collapsed.eid},#{oe_top.eid},#{oe_left.eid}))"
)

# Wire defect loop into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
