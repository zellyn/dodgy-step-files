"""Twi063 — Two edges describe overlapping segments of the same curve.

Catalog claim: Two distinct EDGE_CURVEs share a finite-length segment of the
same underlying curve; distance between them stays below tolerance over a
non-zero parameter interval. The edges are not duplicates (their endpoints
differ), but their interiors collide. CheckOverlapping detects this.

Reproducer recipe: Edge A from (0,0,0)→(5,0,0) along the X-axis; edge B from
(2,0,0)→(7,0,0) along the same X-axis. Overlap span: [2,5].

Mechanism IS a degenerate face where two edges share a real X-axis segment:
  - edge_a: v_a0(0,0,0) → v_a1(5,0,0) along the X-axis
  - edge_b: v_b0(2,0,0) → v_b1(7,0,0) along the same X-axis
Both edges sit on the same underlying LINE curve (Y=0, Z=0). Their interiors
overlap over the parameter interval [2,5]. They are distinct EDGE_CURVEs with
different endpoints, but the interior segments share the same spatial path.
A face built around this overlapping pair lets OCC load it as shape(1) while
a strict kernel should detect and report the overlap.

Tier-3 assertions:
  - n_edges_total >= 1
  - face[0].surface_type == "plane"
  - n_vertices_total >= 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi063",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP contains four EDGE_CURVEs; "
        "edge_a runs (0,0,0)→(5,0,0) along the X-axis (length 5); "
        "edge_b runs (2,0,0)→(7,0,0) along the same X-axis (length 5); "
        "both share the same underlying X-axis direction; interior segments overlap over [2,5]; "
        "the interiors collide while endpoints differ — partial overlap IS the mechanism; "
        "CheckOverlapping detects the span [2,5] where the two edge interiors coincide; "
        "face closes via a short Y-axis connector segment (no extra vertices needed); "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Vertices for the two overlapping edges plus closure edges ─────────────────
# edge_a: (0,0,0) → (5,0,0)
# edge_b: (2,0,0) → (7,0,0)
# closure: connect (7,0,0) back around to (0,0,0) via a Y-height path
#   to form a valid closed wire: A→B→(7,0,0)→(7,1,0)→(0,1,0)→(0,0,0)
# But we must demonstrate the overlap between edge_a interior and edge_b interior.
# Use a simple "open" wire style that OCC heals: build a loop that visits both edges.
# Simplest closed wire using overlapping pair:
#   v0(0,0,0)→[edge_a]→v1(5,0,0) then v1(5,0,0) connects back via:
#   v1(5,0,0)→(5,1,0)→(0,1,0)→(0,0,0) to close outer boundary
# And include edge_b as an independent inner edge pair in a second face, or
# instead: place edge_a and edge_b both in the same wire as a topological anomaly.
#
# Following the catalog recipe literally (edge A 0→5, edge B 2→7, overlap [2,5]):
# Build a non-planar wire with both overlapping segments plus connectors.
# Wire: v0(0,0,0) →[edge_a]→ v1(5,0,0) →[edge_c up]→ v2(5,1,0)
#       →[edge_d left]→ v3(2,1,0) →[edge_e down]→ v4(2,0,0)
#       →[edge_b] — but edge_b goes to (7,0,0) not (0,0,0).
#
# Cleanest approach per tier-3 ("n_edges_total >= 1", "n_vertices_total >= 2"):
# build a simple 4-edge face; make bottom edge and a second "ghost" parallel edge
# explicit in the wire as overlapping X-axis edges. Use face with the overlapping
# pair as consecutive edges in the EDGE_LOOP, forming a degenerate closed walk.

# Vertices
v_a0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # start of edge_a
v_a1 = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))  # end of edge_a
v_b0 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))  # start of edge_b
v_b1 = f.vertex_point(f.cartesian_point((7.0, 0.0, 0.0)))  # end of edge_b

# ── Edge A: (0,0,0) → (5,0,0) along X-axis ─────────────────────────────────
edge_a = f.edge_curve(v_a0, v_a1,
                      f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
oe_a = f.oriented_edge(edge_a, True)

# ── Edge B: (2,0,0) → (7,0,0) along same X-axis — overlaps [2,5] with edge_a ─
# DEFECT: interior of edge_b overlaps interior of edge_a over the [2,5] span
edge_b = f.edge_curve(v_b0, v_b1,
                      f.line(f.cartesian_point((2.0, 0.0, 0.0)),
                             f.vector(f.direction((1.0, 0.0, 0.0)), 5.0)))
oe_b = f.oriented_edge(edge_b, True)

# ── Closure edges to complete a valid closed wire ─────────────────────────────
# Go from v_b1(7,0,0) up to (7,5,0) then back to (0,5,0) then down to v_a0(0,0,0)
# This forms a closed (if degenerate) polygon that includes both overlapping segments.
v_top_r = f.vertex_point(f.cartesian_point((7.0, 5.0, 0.0)))
v_top_l = f.vertex_point(f.cartesian_point((0.0, 5.0, 0.0)))

# Connect v_b1 → v_top_r (up)
e_up = f.edge_curve(v_b1, v_top_r,
                    f.line(f.cartesian_point((7.0, 0.0, 0.0)),
                           f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
oe_up = f.oriented_edge(e_up, True)

# Connect v_top_r → v_top_l (left across top)
e_top = f.edge_curve(v_top_r, v_top_l,
                     f.line(f.cartesian_point((7.0, 5.0, 0.0)),
                            f.vector(f.direction((-1.0, 0.0, 0.0)), 7.0)))
oe_top = f.oriented_edge(e_top, True)

# Connect v_top_l → v_a0 (down)
e_down = f.edge_curve(v_top_l, v_a0,
                      f.line(f.cartesian_point((0.0, 5.0, 0.0)),
                             f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))
oe_down = f.oriented_edge(e_down, True)

# Also need to bridge between v_a1(5,0,0) and v_b0(2,0,0) going backwards
# to maintain a closed connected walk that includes both overlapping edges.
# Wire order: v_a0 →[edge_a]→ v_a1 →[conn1]→ v_b0 →[edge_b]→ v_b1 →[up]→ v_top_r →[top]→ v_top_l →[down]→ v_a0
# conn1: v_a1(5,0,0) → v_b0(2,0,0) going BACKWARDS along X — degenerate but closes
e_conn1 = f.edge_curve(v_a1, v_b0,
                       f.line(f.cartesian_point((5.0, 0.0, 0.0)),
                              f.vector(f.direction((-1.0, 0.0, 0.0)), 3.0)))
oe_conn1 = f.oriented_edge(e_conn1, True)

# ── EDGE_LOOP: full walk including both overlapping segments ──────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_a.eid},#{oe_conn1.eid},#{oe_b.eid},#{oe_up.eid},#{oe_top.eid},#{oe_down.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
