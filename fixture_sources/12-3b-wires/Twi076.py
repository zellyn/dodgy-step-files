"""Twi076 — EDGE_LOOP self-intersects (figure-eight): vertex over-visited.

Catalog claim: A vertex referenced by more than two oriented-edges in a single
wire creates a figure-eight or pinched topology. The wire is technically
traversable but cannot bound a face without splitting at the offending vertex.
Related to Twi049 (edge-intersection-centric) but vertex-centric: the "loop
vertex" is visited more than twice by the wire's edge graph.

Mechanism IS a CLOSED_SHELL with TWO ADVANCED_FACEs on PLANEs:
  face0: a figure-eight wire where a central vertex v_center at (5,5,0) is
    visited by FOUR edges — the wire pinches at this vertex, creating two
    sub-loops:
      - sub-loop A: (0,0,0)→(5,5,0)→(10,0,0)→(0,0,0) [triangle bottom-left]
      - sub-loop B: (5,5,0)→(0,10,0)→(10,10,0)→(5,5,0) [triangle top-right]
    The combined EDGE_LOOP visits v_center at the junction of both loops —
    wire has degree-4 vertex (more than two edges at one vertex), forming a
    figure-eight/pinched topology.
  face1: a correct 10x10 square (provides tier-3 face[1]).

The combined EDGE_LOOP uses v_center as a pivot — edges from sub-loop A exit
and enter v_center, as do edges from sub-loop B. The vertex is visited 4 times
(2 exits, 2 entries) making it a "loop vertex" with graph-degree > 2.

Tier-3 assertions:
  - n_edges_total >= 6
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Twi076",
    defect=(
        "Two ADVANCED_FACEs on PLANEs in a CLOSED_SHELL; "
        "face0 has an EDGE_LOOP forming a figure-eight with vertex v_center at (5,5,0) "
        "visited by FOUR edges — degree-4 'loop vertex' (graph degree > 2); "
        "six edges form two interlocked sub-triangles: "
        "sub-loop A: v_bl(0,0)→v_center(5,5)→v_br(10,0)→v_bl; "
        "sub-loop B: v_center(5,5)→v_tl(0,10)→v_tr(10,10)→v_center; "
        "combined EDGE_LOOP traverses: v_bl→v_center→v_tl→v_tr→v_center→v_br→v_bl; "
        "v_center appears at positions 2 and 5 in the traversal (degree-4 entry); "
        "wire is technically closed but pinched at v_center — figure-eight topology; "
        "CheckLoop must identify v_center as loop vertex and split or reject; "
        "face1 is a correct 10x10 square at z=-1 (provides face[1].surface_type==plane); "
        "all EDGE_CURVEs ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → ADVANCED_FACEs in CLOSED_SHELL"
    ),
)

# ── Plane 0: the defective figure-eight face ──────────────────────────────────
pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl0_zdir = f.direction((0.0, 0.0, 1.0))
pl0_xdir = f.direction((1.0, 0.0, 0.0))
pl0_plc  = f.axis2_placement_3d(pl0_orig, pl0_zdir, pl0_xdir)
plane0   = f._emit_raw(f"PLANE('',#{pl0_plc.eid})")

# Vertices for the figure-eight
v_bl     = f.vertex_point(f.cartesian_point((0.0,  0.0,  0.0)))   # (0,0,0)
v_br     = f.vertex_point(f.cartesian_point((10.0, 0.0,  0.0)))   # (10,0,0)
v_center = f.vertex_point(f.cartesian_point((5.0,  5.0,  0.0)))   # (5,5,0) — loop vertex
v_tl     = f.vertex_point(f.cartesian_point((0.0,  10.0, 0.0)))   # (0,10,0)
v_tr     = f.vertex_point(f.cartesian_point((10.0, 10.0, 0.0)))   # (10,10,0)

# Figure-eight traversal: v_bl→v_center→v_tl→v_tr→v_center→v_br→v_bl
# This creates 6 edges; v_center appears at positions 2 and 5 (degree 4 in edge graph)

# edge A1: v_bl(0,0,0) → v_center(5,5,0)
a1_len = math.sqrt(5**2 + 5**2)  # ~7.071
e_a1 = f.edge_curve(v_bl, v_center,
                    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                           f.vector(f.direction((5.0/a1_len, 5.0/a1_len, 0.0)), a1_len)))
oe_a1 = f.oriented_edge(e_a1, True)

# edge B1: v_center(5,5,0) → v_tl(0,10,0)
b1_dx, b1_dy = -5.0, 5.0
b1_len = math.sqrt(b1_dx**2 + b1_dy**2)  # ~7.071
e_b1 = f.edge_curve(v_center, v_tl,
                    f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                           f.vector(f.direction((b1_dx/b1_len, b1_dy/b1_len, 0.0)), b1_len)))
oe_b1 = f.oriented_edge(e_b1, True)

# edge B2: v_tl(0,10,0) → v_tr(10,10,0)
e_b2 = f.edge_curve(v_tl, v_tr,
                    f.line(f.cartesian_point((0.0, 10.0, 0.0)),
                           f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
oe_b2 = f.oriented_edge(e_b2, True)

# edge B3: v_tr(10,10,0) → v_center(5,5,0)  — 2nd visit to v_center
b3_dx, b3_dy = -5.0, -5.0
b3_len = math.sqrt(b3_dx**2 + b3_dy**2)  # ~7.071
e_b3 = f.edge_curve(v_tr, v_center,
                    f.line(f.cartesian_point((10.0, 10.0, 0.0)),
                           f.vector(f.direction((b3_dx/b3_len, b3_dy/b3_len, 0.0)), b3_len)))
oe_b3 = f.oriented_edge(e_b3, True)

# edge A2: v_center(5,5,0) → v_br(10,0,0)  — 3rd visit to v_center domain
a2_dx, a2_dy = 5.0, -5.0
a2_len = math.sqrt(a2_dx**2 + a2_dy**2)  # ~7.071
e_a2 = f.edge_curve(v_center, v_br,
                    f.line(f.cartesian_point((5.0, 5.0, 0.0)),
                           f.vector(f.direction((a2_dx/a2_len, a2_dy/a2_len, 0.0)), a2_len)))
oe_a2 = f.oriented_edge(e_a2, True)

# edge A3: v_br(10,0,0) → v_bl(0,0,0) — closes back to start
e_a3 = f.edge_curve(v_br, v_bl,
                    f.line(f.cartesian_point((10.0, 0.0, 0.0)),
                           f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
oe_a3 = f.oriented_edge(e_a3, True)

# EDGE_LOOP: 6 edges — v_center visited at positions 2 (as end) and 4 (as end)
# → degree-4 "loop vertex" figure-eight
loop0 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_a1.eid},#{oe_b1.eid},#{oe_b2.eid},"
    f"#{oe_b3.eid},#{oe_a2.eid},#{oe_a3.eid}))"
)
fob0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop0.eid},.T.)")
face0 = f._emit_raw(f"ADVANCED_FACE('',(#{fob0.eid}),#{plane0.eid},.T.)")

# ── Plane 1: correct 10x10 square face (provides tier-3 face[1]) ─────────────
pl1_orig = f.cartesian_point((0.0, 0.0, -1.0))
pl1_zdir = f.direction((0.0, 0.0, 1.0))
pl1_xdir = f.direction((1.0, 0.0, 0.0))
pl1_plc  = f.axis2_placement_3d(pl1_orig, pl1_zdir, pl1_xdir)
plane1   = f._emit_raw(f"PLANE('',#{pl1_plc.eid})")

v_bl1 = f.vertex_point(f.cartesian_point((0.0,  0.0,  -1.0)))
v_br1 = f.vertex_point(f.cartesian_point((10.0, 0.0,  -1.0)))
v_tr1 = f.vertex_point(f.cartesian_point((10.0, 10.0, -1.0)))
v_tl1 = f.vertex_point(f.cartesian_point((0.0,  10.0, -1.0)))

eb1 = f.edge_curve(v_bl1, v_br1,
                   f.line(f.cartesian_point((0.0, 0.0, -1.0)),
                          f.vector(f.direction((1.0, 0.0, 0.0)), 10.0)))
er1 = f.edge_curve(v_br1, v_tr1,
                   f.line(f.cartesian_point((10.0, 0.0, -1.0)),
                          f.vector(f.direction((0.0, 1.0, 0.0)), 10.0)))
et1 = f.edge_curve(v_tr1, v_tl1,
                   f.line(f.cartesian_point((10.0, 10.0, -1.0)),
                          f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
el1 = f.edge_curve(v_tl1, v_bl1,
                   f.line(f.cartesian_point((0.0, 10.0, -1.0)),
                          f.vector(f.direction((0.0, -1.0, 0.0)), 10.0)))

oeb1 = f.oriented_edge(eb1, True)
oer1 = f.oriented_edge(er1, True)
oet1 = f.oriented_edge(et1, True)
oel1 = f.oriented_edge(el1, True)

loop1 = f._emit_raw(
    f"EDGE_LOOP('',(#{oeb1.eid},#{oer1.eid},#{oet1.eid},#{oel1.eid}))"
)
fob1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop1.eid},.T.)")
face1 = f._emit_raw(f"ADVANCED_FACE('',(#{fob1.eid}),#{plane1.eid},.T.)")

# ── Shell containing both faces ───────────────────────────────────────────────
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face0.eid},#{face1.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
