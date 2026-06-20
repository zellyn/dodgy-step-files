"""Tfa045 — Multiple inner FACE_BOUND wires of an ADVANCED_FACE touch
tangentially at a single point (kissing wires sharing a VERTEX_POINT).

Catalog claim: A face has two inner wires that touch at a single point in UV
(tangent rather than crossing). The face boundary is technically simple (no
edges cross) but the wires are kissing; under tolerance perturbations the
kissing point becomes an actual crossing or a separation.

Reproducer recipe (from catalog): Two triangle wires inside a square face,
both having a vertex at (5,5) and otherwise non-overlapping. The shared
vertex is the kissing point.

Mechanism: face[0] is a 12×12 ADVANCED_FACE on a PLANE at z=0 with:
  - Outer FACE_OUTER_BOUND: 12×12 square (x=[0,12], y=[0,12])
  - Inner wire A: triangle with vertices (2,2), (5,5), (2,8) — left side
  - Inner wire B: triangle with vertices (10,2), (5,5), (10,8) — right side
  Both inner wires share VERTEX_POINT at (5,5,0) — the kissing vertex.

Note: we use the SAME vertex entity for the shared kissing point in both wires.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa045",
    defect=(
        "OPEN_SHELL: face[0] is 12×12 PLANE with outer FACE_OUTER_BOUND "
        "plus two inner FACE_BOUND triangle wires kissing at shared VERTEX_POINT (5,5,0); "
        "wire_a: (2,2)→(5,5)→(2,8)→back; wire_b: (10,2)→(5,5)→(10,8)→back; "
        "wires are tangent (kiss) rather than crossing; "
        "FixIntersectingWires must distinguish tangent kiss from crossing; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)


def _mk_edge(x0, y0, vstart, cp_start, x1, y1, vend, cp_end):
    """Build a LINE-based EDGE_CURVE from (x0,y0) to (x1,y1) at z=0."""
    dx = x1 - x0
    dy = y1 - y0
    mag = math.sqrt(dx*dx + dy*dy)
    return f.edge_curve(
        vstart, vend,
        f.line(cp_start, f.vector(f.direction((dx/mag, dy/mag, 0.0)), mag))
    )


# ── shared kissing vertex at (5,5,0) ──────────────────────────────────────────
p_kiss = f.cartesian_point((5.0, 5.0, 0.0))
v_kiss = f.vertex_point(p_kiss)

# ── Outer 12×12 bound ─────────────────────────────────────────────────────────
p_o0 = f.cartesian_point(( 0.0,  0.0, 0.0))
p_o1 = f.cartesian_point((12.0,  0.0, 0.0))
p_o2 = f.cartesian_point((12.0, 12.0, 0.0))
p_o3 = f.cartesian_point(( 0.0, 12.0, 0.0))
v_o0 = f.vertex_point(p_o0); v_o1 = f.vertex_point(p_o1)
v_o2 = f.vertex_point(p_o2); v_o3 = f.vertex_point(p_o3)

oe0 = _mk_edge( 0,  0, v_o0, p_o0, 12,  0, v_o1, p_o1)
oe1 = _mk_edge(12,  0, v_o1, p_o1, 12, 12, v_o2, p_o2)
oe2 = _mk_edge(12, 12, v_o2, p_o2,  0, 12, v_o3, p_o3)
oe3 = _mk_edge( 0, 12, v_o3, p_o3,  0,  0, v_o0, p_o0)

outer_loop = f.edge_loop([
    f.oriented_edge(oe0, True), f.oriented_edge(oe1, True),
    f.oriented_edge(oe2, True), f.oriented_edge(oe3, True),
])

# ── Inner wire A: triangle (2,2)→(5,5)→(2,8) — left side ─────────────────────
p_a0 = f.cartesian_point((2.0, 2.0, 0.0))
p_a2 = f.cartesian_point((2.0, 8.0, 0.0))
v_a0 = f.vertex_point(p_a0)
v_a2 = f.vertex_point(p_a2)

ae0 = _mk_edge(2, 2, v_a0,  p_a0,  5, 5, v_kiss, p_kiss)  # (2,2)→(5,5)
ae1 = _mk_edge(5, 5, v_kiss, p_kiss, 2, 8, v_a2,  p_a2)   # (5,5)→(2,8)
ae2 = _mk_edge(2, 8, v_a2,  p_a2,   2, 2, v_a0,  p_a0)   # (2,8)→(2,2)

wire_a_loop = f.edge_loop([
    f.oriented_edge(ae0, True), f.oriented_edge(ae1, True),
    f.oriented_edge(ae2, True),
])

# ── Inner wire B: triangle (10,2)→(5,5)→(10,8) — right side ──────────────────
p_b0 = f.cartesian_point((10.0,  2.0, 0.0))
p_b2 = f.cartesian_point((10.0,  8.0, 0.0))
v_b0 = f.vertex_point(p_b0)
v_b2 = f.vertex_point(p_b2)

be0 = _mk_edge(10, 2, v_b0,  p_b0,  5, 5, v_kiss, p_kiss)  # (10,2)→(5,5)
be1 = _mk_edge( 5, 5, v_kiss, p_kiss, 10, 8, v_b2, p_b2)   # (5,5)→(10,8)
be2 = _mk_edge(10, 8, v_b2,  p_b2,  10, 2, v_b0,  p_b0)   # (10,8)→(10,2)

wire_b_loop = f.edge_loop([
    f.oriented_edge(be0, True), f.oriented_edge(be1, True),
    f.oriented_edge(be2, True),
])

# ── ADVANCED_FACE: outer + two kissing inner wires ────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane0  = f.plane(pl_plc)

face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(wire_a_loop, orientation=False),
    f.face_bound(wire_b_loop, orientation=False),
], plane0)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa045.stp")
