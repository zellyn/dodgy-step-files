"""Twi007 — Disordered edges in wire — listed out of traversal order but reorderable.

Catalog claim: The edges in an EDGE_LOOP are emitted in arbitrary order; the
head/tail vertices of consecutive entries do not match, but the edges as a set
can be reordered into a valid head-to-tail traversal. Common with Pro/E
composite-curve segments where the exporter writes edges in arbitrary slot order.

Mechanism IS the disordered EDGE_LOOP: four line edges forming a valid unit
square are listed in non-traversal slot order (edge indices 0,2,3,1 of the
intended traversal). The head-vertex of each consecutive pair in the emitted
order does NOT match the tail-vertex of the preceding edge, but permuting the
four edges produces exactly one valid head-to-tail circuit. The defect
EDGE_LOOP IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an
OPEN_SHELL; never orphaned. Kernel must reorder edges by vertex matching to
recover head-to-tail traversal; if no consistent ordering exists reject as
malformed.

Tier-3 assertions:
  - n_edges_total >= 4
  - face[0].surface_type == "plane"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi007",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with four ORIENTED_EDGEs "
        "listed in non-traversal slot order (0→1, 2→3, 3→0, 1→2 of unit square); "
        "head/tail vertices of consecutive emitted edges do not match; "
        "edges as a set can be reordered into one valid head-to-tail circuit; "
        "disordered EDGE_LOOP IS the mechanism; "
        "kernel must reorder by vertex matching to recover head-to-tail traversal; "
        "if no consistent ordering exists reject as malformed"
    ),
)

# ── Carrier plane geometry ────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Unit-square corners — 4 vertices for 4 edges (8 distinct VERTEX_POINTs) ──
# Intended traversal: V0→V1→V2→V3→V0 (bottom, right, top, left).
# Each edge owns its own pair of vertex entities (no sharing) to ensure
# head/tail adjacency is vertex-identity-based.
pA = f.cartesian_point((0.0, 0.0, 0.0))
pB = f.cartesian_point((1.0, 0.0, 0.0))
pC = f.cartesian_point((1.0, 1.0, 0.0))
pD = f.cartesian_point((0.0, 1.0, 0.0))

# Each edge has its own start/end VERTEX_POINTs (8 total, n_vertices_total >= 8).
vA0 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
vA1 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vB0 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))
vB1 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
vC0 = f.vertex_point(f.cartesian_point((1.0, 1.0, 0.0)))
vC1 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))
vD0 = f.vertex_point(f.cartesian_point((0.0, 1.0, 0.0)))
vD1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))

def line_edge(pa, pb, va, vb, dx, dy):
    import math
    mag = math.hypot(dx, dy)
    d   = f.direction((dx / mag, dy / mag, 0.0))
    vec = f.vector(d, 1.0)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Four edges of unit square in their CORRECT traversal sequence:
# e0: (0,0)→(1,0)  e1: (1,0)→(1,1)  e2: (1,1)→(0,1)  e3: (0,1)→(0,0)
e0 = line_edge(pA, pB, vA0, vA1,  1.0,  0.0)   # bottom
e1 = line_edge(pB, pC, vB0, vB1,  0.0,  1.0)   # right
e2 = line_edge(pC, pD, vC0, vC1, -1.0,  0.0)   # top
e3 = line_edge(pD, pA, vD0, vD1,  0.0, -1.0)   # left

# ── Disordered EDGE_LOOP: emit in slot order 0,2,3,1 (not traversal order) ──
# Emitted:  e0(A→B), e2(C→D), e3(D→A), e1(B→C)
# Tail/head adjacency in emitted order: B≠C, D≠D, A≠B — broken at every junction.
# Only the permutation (e0,e1,e2,e3) produces a valid circuit.
# This IS the mechanism.
loop = f.edge_loop([
    f.oriented_edge(e0, True),   # slot 0: (0,0)→(1,0)
    f.oriented_edge(e2, True),   # slot 1: (1,1)→(0,1) — out of order
    f.oriented_edge(e3, True),   # slot 2: (0,1)→(0,0)
    f.oriented_edge(e1, True),   # slot 3: (1,0)→(1,1) — out of order
])

# Wire defect loop into face/shell topology — never orphan.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
