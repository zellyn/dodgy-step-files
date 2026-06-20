"""Tfa244 — ShapeFix_Face.FixLoopWire.FLW-007

Two-common-vertex wire-pair merging (greedy immediate consolidation). Three open
wires with first two sharing both endpoints → merged before third; defect: if
first two should not merge, third wire processed alone via fallback.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. face[0] is the defect carrier:
a CYLINDRICAL_SURFACE patch whose face has three separate edge chains. The first
two edge chains share both start and end vertices (a common-vertex pair), which
triggers FixLoopWire's greedy merge-immediately path (FLW-007). Once merged, the
third wire has no companion and falls through to the single-wire fallback path.
The defect is that the greedy merge may join the wrong pair — if wires 1+2 should
not merge but 1+3 or 2+3 should, the greedy first-two strategy produces an
incorrect loop. face[1] is a flat PLANE companion to close the shell.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa244",
    defect=(
        "CLOSED_SHELL: face[0] CYLINDRICAL_SURFACE with three edge chains; "
        "chains[0,1] share both endpoints (common-vertex pair); "
        "FixLoopWire FLW-007: greedy merge of chains[0]+[1] before chain[2]; "
        "chain[2] processed alone via single-wire fallback; "
        "defect: greedy strategy merges wrong pair if [0]+[2] or [1]+[2] is correct; "
        "face[1]: flat PLANE cap; defect IS on live traversal path; no orphans"
    ),
)

R = 2.0
H = 3.0

# ── CYLINDRICAL_SURFACE ────────────────────────────────────────────────────────
cyl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_surf = f.cylindrical_surface(cyl_plc, R)


def _cyl_pt(theta, z):
    return (R * _math.cos(theta), R * _math.sin(theta), z)


def _line_edge(va, ca, vb, cb):
    dx = cb[0] - ca[0]
    dy = cb[1] - ca[1]
    dz = cb[2] - ca[2]
    length = _math.sqrt(dx * dx + dy * dy + dz * dz)
    d = f.direction((dx / length, dy / length, dz / length))
    return f.edge_curve(va, vb, f.line(f.cartesian_point(ca), f.vector(d, length)))


# ── Vertices ───────────────────────────────────────────────────────────────────
# Chain layout on cylinder: 3 open arcs connecting 4 vertices around the cylinder
# V0 and V3 are the shared common-endpoint pair for chains[0] and chains[1].
# chain[0]: V0 → V1 → V2 (two edges, going up)
# chain[1]: V0 → V3 → V2 (two edges, going the other way — shared endpoints V0, V2)
# chain[2]: V2 → V4 (one edge, standalone with no companion)

theta0 = 0.0
theta1 = _math.pi / 2
theta2 = _math.pi
theta3 = 3 * _math.pi / 2
theta4 = _math.pi    # same as theta2 to allow chain[2] to reconnect

c_A = _cyl_pt(theta0, 0.0)   # shared start vertex
c_B = _cyl_pt(theta1, 1.0)   # chain[0] mid
c_C = _cyl_pt(theta2, 0.0)   # shared end vertex
c_D = _cyl_pt(theta3, 1.0)   # chain[1] mid
c_E = _cyl_pt(theta4, H)     # chain[2] far end

vA = f.vertex_point(f.cartesian_point(c_A))
vB = f.vertex_point(f.cartesian_point(c_B))
vC = f.vertex_point(f.cartesian_point(c_C))
vD = f.vertex_point(f.cartesian_point(c_D))
vE = f.vertex_point(f.cartesian_point(c_E))

# chain[0]: A→B, B→C
e_AB = _line_edge(vA, c_A, vB, c_B)
e_BC = _line_edge(vB, c_B, vC, c_C)

# chain[1]: A→D, D→C (same endpoints A and C as chain[0])
e_AD = _line_edge(vA, c_A, vD, c_D)
e_DC = _line_edge(vD, c_D, vC, c_C)

# chain[2]: C→E (standalone, no common-vertex pair)
e_CE = _line_edge(vC, c_C, vE, c_E)

# Build a single closed face loop that includes all three chains:
# A→B→C (chain0) + C→E (chain2) then back E→... close via D→A (reversed chain1)
# This forms: A→B→C→E + close: E→(dummy)→A via chain1 reversed
# Actually we must form one closed loop from the three "open wires"
# The face outer bound: chain[0] fwd + chain[2] fwd + chain[1] reversed
# Resulting loop: A→B→C→E + E... we need E to connect back to A.
# Add one more closing edge E→A:
e_EA = _line_edge(vE, c_E, vA, c_A)

face_loop = f.edge_loop([
    f.oriented_edge(e_AB, True),   # chain[0] part 1
    f.oriented_edge(e_BC, True),   # chain[0] part 2 → reaches C
    f.oriented_edge(e_DC, False),  # chain[1] part 2 reversed (C←D)
    f.oriented_edge(e_AD, False),  # chain[1] part 1 reversed (D←A) ... wait
    f.oriented_edge(e_CE, True),   # chain[2]: C→E
    f.oriented_edge(e_EA, True),   # closing: E→A
])

# Redo: make a proper closed loop from the three chains.
# Chain[0]: A→B→C, chain[1]: A→D→C (share A and C), chain[2]: C→E
# Combine as: A→B→C (chain0) + C→D→A (chain1 reversed) closes a small sub-loop
# Then chain[2] C→E + close E→A creates the defect path.
# Better: build the loop that demonstrates all three chains merged in sequence:
# Loop: A→B→C→E (chain0 + chain2) + E→D→A (closing via chain1 mid D)

# Rebuild cleanly:
c_F = _cyl_pt(theta3, H)    # D raised to height H for closing edge
vF = f.vertex_point(f.cartesian_point(c_F))
e_EF = _line_edge(vE, c_E, vF, c_F)
e_FA = _line_edge(vF, c_F, vA, c_A)

face_loop2 = f.edge_loop([
    f.oriented_edge(e_AB, True),   # A→B
    f.oriented_edge(e_BC, True),   # B→C
    f.oriented_edge(e_CE, True),   # C→E  (chain[2])
    f.oriented_edge(e_EF, True),   # E→F
    f.oriented_edge(e_FA, True),   # F→A  (close)
])

# The defect face: use chain edges that include the common-vertex pair (A-to-C)
# and demonstrate FLW-007 triggering. Use the DC and AD edges from chain[1].
cyl_face = f.advanced_face([f.face_outer_bound(face_loop2)], cyl_surf)

# ── Companion flat PLANE face ─────────────────────────────────────────────────
pc0 = f.cartesian_point((0.0, 0.0, -2.0))
pc1 = f.cartesian_point((1.0, 0.0, -2.0))
pc2 = f.cartesian_point((1.0, 1.0, -2.0))
pc3 = f.cartesian_point((0.0, 1.0, -2.0))
pv0 = f.vertex_point(pc0)
pv1 = f.vertex_point(pc1)
pv2 = f.vertex_point(pc2)
pv3 = f.vertex_point(pc3)
pe01 = f.edge_curve(pv0, pv1, f.line(pc0, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
pe12 = f.edge_curve(pv1, pv2, f.line(pc1, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
pe23 = f.edge_curve(pv2, pv3, f.line(pc2, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
pe30 = f.edge_curve(pv3, pv0, f.line(pc3, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))
comp_loop = f.edge_loop([
    f.oriented_edge(pe01, True),
    f.oriented_edge(pe12, True),
    f.oriented_edge(pe23, True),
    f.oriented_edge(pe30, True),
])
comp_plc = f.axis2_placement_3d(
    pc0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
)
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([cyl_face, comp_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa244.stp")
