"""Twi290 — Non-closed arc whose two DISTINCT vertices project to the SAME
curve parameter (null arc length) -> straight-line substitution fallback.
Twi018 covers the identical-vertices subvariant (edge dropped); this fixture
is the distinct-vertices subvariant (curve replaced by a Geom_Line).

Catalog claim: An edge's 3D curve cannot be validly trimmed between its two
vertex parameters (a "different points on closed curve" construction error)
even though the curve itself is not closed and the two declared vertices are
distinct points — indicating a near-zero-length or otherwise malformed arc.
OCCT discards the STEP-specified curve for this edge and substitutes a
straight line segment built directly between the two vertex points, because
V1 != V2 ("this edge has null arc length" -> Geom_Line fallback,
StepToTopoDS_TranslateEdge::MakeFromCurve3D, StepToTopoDS_TranslateEdge.cxx:
459-481). If the two vertices were instead identical, the edge would be
dropped entirely (Twi018's "NULL EDGE, SKIPPED" branch) — this fixture
targets the sibling V1!=V2 branch.

Mechanism IS the "right" edge of an otherwise-ordinary 4-edge square wire,
replaced by an EDGE_CURVE whose curve is a LINE — genuinely open/non-closed,
infinite parameter domain, never a periodic or full-period curve — anchored
at (10,5,0) (the edge's own midpoint) and running along +Z, PERPENDICULAR to
the square's plane. The two VERTEX_POINTs are the square's own corners,
(10,0,0) and (10,10,0): distinct 3D points, but each one's orthogonal
projection onto this perpendicular LINE lands at the SAME point (10,5,0) —
both compute to curve parameter w=0. Two genuinely distinct 3D points that
project to the identical parameter on a genuinely open (non-closed) curve ->
the trim between them collapses to null arc length. Confirmed live via
direct OCP testing: BRepBuilderAPI_MakeEdge(line, v1, v2, w1=0.0, w2=0.0)
raises BRepBuilderAPI_LineThroughIdenticPoints for exactly this
configuration — the same "different points on closed curve"-flavoured
construction failure the catalog's evidence describes, on a curve that is
provably NOT closed.

The malformed-arc EDGE_CURVE IS one of the four edges of the square's own
EDGE_LOOP, which IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in
an OPEN_SHELL; never orphaned — no extra dangling edges, no second face.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') == 4
  - count_entity_def(b'EDGE_CURVE') == 4
  - contains(b'(10.0,5.0,0.0)')
  - contains(b'(10.0,0.0,0.0)')
  - contains(b'(10.0,10.0,0.0)')

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi290",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP of four edges forming a "
        "10x10 square; the 'right' edge (from (10,0,0) to (10,10,0)) is "
        "replaced by an EDGE_CURVE whose curve is a LINE anchored at "
        "(10,5,0) running along +Z, PERPENDICULAR to the square's own plane "
        "— genuinely open/non-closed, never a periodic curve; "
        "both (10,0,0) and (10,10,0) are DISTINCT 3D points whose orthogonal "
        "projection onto this perpendicular LINE lands at the SAME point "
        "(10,5,0) — identical curve parameter w=0 for both — so the trim "
        "between them collapses to null arc length despite the curve being "
        "open and the vertices genuinely distinct — this IS the mechanism; "
        "OCCT's non-closed-curve branch must discard the STEP LINE for "
        "this edge and substitute a straight Geom_Line directly between the "
        "two vertex points (V1 != V2 -> fallback line, not edge drop); "
        "the defect edge IS one of the square's own four EDGE_LOOP members, "
        "wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL — never "
        "orphaned, no extra dangling edges"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def mk_line_edge(pa, pb, va, vb):
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, mag)
    ln  = f.line(f.cartesian_point((pa[0], pa[1], 0.0)), vec)
    return f.edge_curve(va, vb, ln)

# ── Square corners ─────────────────────────────────────────────────────────
v_00 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_10 = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))
v_11 = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))
v_01 = f.vertex_point(f.cartesian_point((0.0, 10.0, 0.0)))

e_bot  = mk_line_edge((0.0, 0.0), (10.0, 0.0), v_00, v_10)

# ── Malformed-arc "right" edge: LINE anchored at the edge's own midpoint,
# running PERPENDICULAR to the square's plane (+Z). Both distinct corner
# vertices project orthogonally onto the SAME point on this line (w=0) —
# null arc length trim, genuinely non-closed curve. IS the mechanism. ────────
line_anchor = f.cartesian_point((10.0, 5.0, 0.0))
line_dir    = f.direction((0.0, 0.0, 1.0))
line_vec    = f.vector(line_dir, 1.0)
perp_line   = f.line(line_anchor, line_vec)
e_right = f._emit_raw(
    f"EDGE_CURVE('',#{v_10.eid},#{v_11.eid},#{perp_line.eid},.T.)"
)

e_top  = mk_line_edge((10.0, 10.0), (0.0, 10.0), v_11, v_01)
e_left = mk_line_edge((0.0, 10.0), (0.0, 0.0), v_01, v_00)

oe_bot    = f.oriented_edge(e_bot, True)
oe_right  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_right.eid},.T.)")
oe_top    = f.oriented_edge(e_top, True)
oe_left   = f.oriented_edge(e_left, True)

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot.eid},#{oe_right.eid},#{oe_top.eid},#{oe_left.eid}))"
)

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
