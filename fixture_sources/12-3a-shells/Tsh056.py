"""Tsh056 — Merging adjacent same-surface faces hangs on a face whose wire
forms a figure-eight.

Catalog claim: A face's outer wire visits one vertex twice (figure-of-eight
topology), so the wire is non-simple. Same-surface face merging walks edges
and never terminates because the visited-edge map records edges, not
edge-with-direction, and the figure-of-eight makes the iterator revisit the
same edge from the opposite side indefinitely.

Mechanism IS the shell structure: an OPEN_SHELL contains one ADVANCED_FACE
whose FACE_OUTER_BOUND has 6 EDGE_CURVEs arranged in a figure-eight — vertex
B (at the pinch point) has 4 incident edges in the loop. The figure-eight
IS wired directly into the EDGE_LOOP topology: vertex B appears as both
start and end of two distinct sub-loops, creating the non-simple wire.
An edge-walking iterator that uses only edge identity (not edge + direction)
in its visited set will cycle indefinitely.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 1

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh056",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE (z=0, normal +Z); "
        "FACE_OUTER_BOUND has 6 EDGE_CURVEs forming a figure-eight at vertex B (1,1,0); "
        "vertex B has 4 incident edges in the loop (pinch point, visited twice); "
        "figure-eight IS wired into EDGE_LOOP topology as a non-simple wire; "
        "edge walker using edge-only visited set loops indefinitely; "
        "fix requires edge+direction in visited map, or reject non-simple wires"
    ),
)

# ── Figure-eight layout ───────────────────────────────────────────────────────
# Two triangles sharing a pinch vertex B at (1,1,0).
# Triangle 1 (left lobe):  A(0,0) → B(1,1) → C(0,2) → A
# Triangle 2 (right lobe): B(1,1) → D(2,0) → E(2,2) → B
#
# The EDGE_LOOP visits: A→B, B→C, C→A, A→B (again? no — we close via B)
# Better figure-eight: wire visits B twice as an intermediate pinch vertex.
# Layout:
#   pA=(0,1,0), pB=(1,1,0)[pinch], pC=(1,0,0), pD=(2,1,0), pE=(1,2,0)
# Sub-loop 1: A→B→C→A  (left triangle)
# Sub-loop 2: A→B→D→E→B→A ... but B must appear twice.
#
# Simplest figure-eight using 6 edges, with B as the pinch:
#   Edges: A→B, B→C, C→A (sub-loop 1), A→B (shared? no — must reuse vertex)
# Use distinct edge segments but same vertex object for B:
#   e1: A(0,0)→B(1,1)
#   e2: B(1,1)→C(2,0)
#   e3: C(2,0)→D(1,-1)  [not helpful]
#
# Clean 6-edge figure-eight: two loops joined at B (one vertex visited twice).
#   Sub-loop 1: A→B→C→A  (3 edges)
#   Sub-loop 2: B→D→E→B  (3 edges)
# Combined wire: A→B, B→D, D→E, E→B, B→C, C→A  (6 edges, B appears at positions 2 and 4)

pA = f.cartesian_point((0.0, 1.0, 0.0))
pB = f.cartesian_point((1.0, 1.0, 0.0))   # pinch vertex — visited twice
pC = f.cartesian_point((0.0, 2.0, 0.0))
pD = f.cartesian_point((2.0, 0.0, 0.0))
pE = f.cartesian_point((2.0, 2.0, 0.0))

vA = f.vertex_point(pA)
vB = f.vertex_point(pB)   # IS the mechanism: appears at positions 2 and 4 in loop
vC = f.vertex_point(pC)
vD = f.vertex_point(pD)
vE = f.vertex_point(pE)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# 6 edges forming the figure-eight (vertex B appears at steps 2 and 4)
e1 = line_edge(vA, vB, pA,  1,  0, 0)   # A(0,1) → B(1,1)
e2 = line_edge(vB, vD, pB,  1, -1, 0)   # B(1,1) → D(2,0)
e3 = line_edge(vD, vE, pD,  0,  1, 0)   # D(2,0) → E(2,2)
e4 = line_edge(vE, vB, pE, -1, -1, 0)   # E(2,2) → B(1,1)  ← second visit to B
e5 = line_edge(vB, vC, pB, -1,  1, 0)   # B(1,1) → C(0,2)
e6 = line_edge(vC, vA, pC,  0, -1, 0)   # C(0,2) → A(0,1)

# Figure-eight EDGE_LOOP: B visited at step 2 (end of e1) and step 4 (end of e4)
fig8_loop = f.edge_loop([
    f.oriented_edge(e1, True),   # A → B
    f.oriented_edge(e2, True),   # B → D
    f.oriented_edge(e3, True),   # D → E
    f.oriented_edge(e4, True),   # E → B  (pinch: B second visit)
    f.oriented_edge(e5, True),   # B → C
    f.oriented_edge(e6, True),   # C → A
])

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Single ADVANCED_FACE with figure-eight outer wire IS the mechanism
face = f.advanced_face([f.face_outer_bound(fig8_loop)], plane)

# OPEN_SHELL: figure-eight IS wired into shell/face/edge topology
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
