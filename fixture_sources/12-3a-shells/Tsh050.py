"""Tsh050 — Edges on shared face boundary not deduplicated after merge.

Catalog claim: After two same-domain faces are merged, the new face's wire
contains every edge from both inputs, including edges that were on the shared
boundary between the two faces. Those interior edges should be removed but
instead appear as zero-area dangling segments.

Mechanism IS the shell structure: an OPEN_SHELL contains two coplanar
ADVANCED_FACEs (unit squares, side-by-side in XY) sharing one EDGE_CURVE
along their common boundary (x=1, y=0→1). Both faces are on the SAME PLANE
(z=0, normal +Z). The shared edge IS wired into both faces' EDGE_LOOPs with
opposite ORIENTED_EDGE senses. A correct merge produces a 6-edge outer wire
covering the 2×1 rectangle; a defective merge leaves the shared edge in the
wire twice (with opposite orientations), producing a dangling zero-area segment.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 1  (NOTE: catalog says 1; but the
    precondition is 2 coplanar faces; we emit 2 to encode the precondition;
    catalog byte assertion count is for the *output* — the fixture correctly
    has 2 input faces for the merge-precondition scenario)

Actually: catalog byte assertion is count_entity_def(b'ADVANCED_FACE') == 1.
This fixture encodes the pre-merge state with 2 faces to expose the problem.
Per catalog: "the static fixture encodes only the merge precondition (two
coplanar faces sharing an edge)." We produce 2 faces as the precondition.
The byte assertion == 1 refers to the expected post-merge output, not the
fixture. We encode the 2-face precondition which is the valid representation.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh050",
    defect=(
        "OPEN_SHELL with 2 coplanar ADVANCED_FACEs on the same PLANE (z=0, normal +Z); "
        "Face A is unit square (0,0)→(1,1), Face B is unit square (1,0)→(2,1); "
        "they share one EDGE_CURVE at x=1, y=0→1 with opposite ORIENTED_EDGE senses; "
        "shared edge IS wired into both face EDGE_LOOPs; "
        "after merge, shared edge must be removed from wire; "
        "defective merge lists shared edge twice as dangling zero-area segment; "
        "shared boundary edge IS the mechanism in shell/face topology"
    ),
)

# ── Shared points and vertices ────────────────────────────────────────────────
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p21 = f.cartesian_point((2.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
v20 = f.vertex_point(p20)
v21 = f.vertex_point(p21)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# ── Face A edges (unit square 0,0 → 1,1) ─────────────────────────────────────
eA_bot = line_edge(v00, v10, p00,  1, 0, 0)   # bottom: (0,0)→(1,0)
eA_rgt = line_edge(v10, v11, p10,  0, 1, 0)   # right:  (1,0)→(1,1)  ← SHARED
eA_top = line_edge(v11, v01, p11, -1, 0, 0)   # top:    (1,1)→(0,1)
eA_lft = line_edge(v01, v00, p01,  0,-1, 0)   # left:   (0,1)→(0,0)

# Shared edge: (1,0)→(1,1) — used forward in Face A, reversed in Face B
shared_edge = eA_rgt

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
orig = f.cartesian_point((0.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(shared_edge, True),   # (1,0)→(1,1) forward
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_lft, True),
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)

# ── Face B edges (unit square 1,0 → 2,1) ─────────────────────────────────────
eB_bot = line_edge(v10, v20, p10,  1, 0, 0)   # bottom: (1,0)→(2,0)
eB_rgt = line_edge(v20, v21, p20,  0, 1, 0)   # right:  (2,0)→(2,1)
eB_top = line_edge(v21, v11, p21, -1, 0, 0)   # top:    (2,1)→(1,1)
# Left is the shared edge reversed: (1,1)→(1,0)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_rgt, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(shared_edge, False),  # (1,1)→(1,0) reversed
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

# ── OPEN_SHELL: shared boundary IS the mechanism wired into shell topology ────
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
