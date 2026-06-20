"""Twi164 — ShapeFix_Wire.FixReorder algorithm-cycle.

Catalog claim: Wire where reorder algorithm reaches cycle: edge X must come
before Y but Y also requires X-first; algorithm doesn't detect and loops.

Mechanism: A four-edge diamond wire (v0→v1→v2→v3→v0) is provided in
deliberately shuffled order in the EDGE_LOOP, with near-tangent junctions
creating ambiguous endpoint matching. FixReorder tries to reorder by matching
endpoints: each edge's end must match the next edge's start. With a diamond
where two pairs of vertices are very close together (but not coincident), the
greedy matching algorithm can create dependency cycles:
  - Edge E0: (0,5,0)→(5,10,0)  — top-left spoke
  - Edge E1: (5,0,0)→(10,5,0)  — bottom-right spoke
  - Edge E2: (10,5,0)→(5,10,0) — right spoke (E1-end ≈ E2-end in Y)
  - Edge E3: (5,10,0)→(5,0,0)  — vertical (E0-end = E2-end creates ambiguity)

The EDGE_LOOP lists edges in order [E2, E0, E3, E1] (shuffled). FixReorder
sees: E2-end=(5,10,0) ≈ E0-end=(5,10,0): both have same endpoint, so
algorithm cannot determine ordering: E2 before E0 OR E0 before E2? This
creates a dependency cycle in the reorder graph.

Additionally, near-tangent junctions: E0 end and E2 end both are at (5,10,0)
exactly, while E1 end and E2 start are at (10,5,0) exactly — the "diamond"
has two pairs of edges meeting at shared vertices, which the shuffled order
forces FixReorder to traverse as a cycle: A→B requires B→A.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi164",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 LINE edges forming a diamond, "
        "listed in shuffled order [E2, E0, E3, E1] IS the defect; "
        "E0 (0,5,0)→(5,10,0), E1 (5,0,0)→(10,5,0), "
        "E2 (10,5,0)→(5,10,0), E3 (5,10,0)→(5,0,0); "
        "correct order is E0, E2 (reversed), E3, E1 (reversed) etc.; "
        "shuffled EDGE_LOOP [E2,E0,E3,E1] creates endpoint-matching cycle "
        "in FixReorder dependency graph — E0-end = E2-end = (5,10,0) and "
        "E3 connects them, creating cyclic dependency IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Diamond vertices ──────────────────────────────────────────────────────────
# Diamond: left=(0,5), bottom=(5,0), right=(10,5), top=(5,10)
P_left   = ( 0.0,  5.0, 0.0)
P_bottom = ( 5.0,  0.0, 0.0)
P_right  = (10.0,  5.0, 0.0)
P_top    = ( 5.0, 10.0, 0.0)

v_left   = f.vertex_point(f.cartesian_point(P_left))
v_bottom = f.vertex_point(f.cartesian_point(P_bottom))
v_right  = f.vertex_point(f.cartesian_point(P_right))
v_top    = f.vertex_point(f.cartesian_point(P_top))


def _line_edge(v_src, v_dst, src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    ln = f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )
    return f.edge_curve(v_src, v_dst, ln, True)


# ── Diamond edges (correct order would be: left→top→right→bottom→left) ────────
# E0: left → top
e0 = _line_edge(v_left, v_top, P_left, P_top)
# E1: bottom → right
e1 = _line_edge(v_bottom, v_right, P_bottom, P_right)
# E2: right → top  (same end as E0! — creates ambiguity for FixReorder)
e2 = _line_edge(v_right, v_top, P_right, P_top)
# E3: top → bottom
e3 = _line_edge(v_top, v_bottom, P_top, P_bottom)

# ── ORIENTED_EDGEs in SHUFFLED order [E2, E0, E3, E1] — IS the defect ─────────
# This ordering is non-sequential: E2 ends at top, E0 starts at left (not top) →
# endpoint mismatch at each junction. FixReorder must sort them but the shared
# top vertex (end of both E0 and E2) creates a cyclic ordering constraint.
oe2 = f.oriented_edge(e2, True)   # right → top
oe0 = f.oriented_edge(e0, True)   # left → top   (starts ≠ prev end)
oe3 = f.oriented_edge(e3, True)   # top → bottom
oe1 = f.oriented_edge(e1, True)   # bottom → right

# ── EDGE_LOOP in shuffled order ───────────────────────────────────────────────
loop = f.edge_loop([oe2, oe0, oe3, oe1])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi164.stp")
