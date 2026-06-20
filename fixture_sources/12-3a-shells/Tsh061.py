"""Tsh061 — Merging same-surface faces around a non-manifold interior edge
corrupts topology.

Catalog claim: After Boolean intersection of two complex shapes, the result has
internal seam edges shared by three faces (a non-manifold interior edge).
Same-surface face merging visits this edge from each incident face and records
contradictory merge decisions, producing a shape that fails Boolean validity
check ("InvalidMultiConnexity"; edge connected to too many faces in the result).

Mechanism IS the shell structure: an OPEN_SHELL contains 4 ADVANCED_FACEs where
one interior EDGE_CURVE is shared by 3 faces (non-manifold: 3 ORIENTED_EDGEs
from 3 distinct EDGE_LOOPs all reference the same EDGE_CURVE entity). The
triple-incident edge IS directly wired into 3 faces' EDGE_LOOPs. A same-surface
merge that allows non-manifold edges as merge candidates records contradictory
decisions when it visits the edge from each of its 3 incident faces, producing
an invalid topology.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 4

Tier-3 assertion: n_faces_total == 4

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh061",
    defect=(
        "OPEN_SHELL with 4 ADVANCED_FACEs; one EDGE_CURVE shared by 3 distinct face EDGE_LOOPs; "
        "triple-incident non-manifold edge IS wired into 3 faces' EDGE_LOOP topology; "
        "same-surface merge visits non-manifold edge from each incident face; "
        "contradictory merge decisions produce InvalidMultiConnexity in result; "
        "fix: non-manifold interior edges (>=3 incident faces) must not be merge-eligible; "
        "preserve all incident-face records during traversal"
    ),
)

# ── Shared plane z=0, normal +Z ───────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── Points: T-shape arrangement to create a non-manifold interior seam ───────
# Layout (all z=0):
#   p00=(0,0)  p10=(1,0)  p20=(2,0)  p30=(3,0)
#   p01=(0,1)  p11=(1,1)  p21=(2,1)  p31=(3,1)
#   p02=(0,2)             p22=(2,2)
#
# Non-manifold edge: the vertical segment at x=1, y=0→1 (between p10 and p11)
# is shared by:
#   Face A: left rectangle [0,0]→[1,1]
#   Face B: middle rectangle [1,0]→[2,1]
#   Face C: bottom strip across [0,0]→[2,0]→[2,1]→[0,1] — no, need 3 faces on seam
#
# Cleaner: 4 faces meeting at one vertical seam edge in a T-junction:
#   Face A: square [0,0]→[1,1]   (left)
#   Face B: square [1,0]→[2,1]   (right)
#   Face C: square [0,1]→[1,2]   (upper-left, shares the seam top)
# All three share the edge from (1,0) to (1,1).
# Face D: a separate face that also references the seam — (1,0)→(1,1) again.
#   Face D: thin strip [(1,0),(2,0),(2,1),(1,1)] — same as Face B but different winding

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p21 = f.cartesian_point((2.0, 1.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0))
p12 = f.cartesian_point((1.0, 2.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
v20 = f.vertex_point(p20)
v21 = f.vertex_point(p21)
v02 = f.vertex_point(p02)
v12 = f.vertex_point(p12)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# ── Non-manifold seam edge at x=1, y=0→1 (IS the mechanism: shared by 3 faces) ──
seam_edge = line_edge(v10, v11, p10, 0, 1, 0)   # non-manifold: 3 incident faces

# ── Face A: unit square [0,0]→[1,1] (left) ───────────────────────────────────
eA_bot = line_edge(v00, v10, p00,  1, 0, 0)
eA_top = line_edge(v11, v01, p11, -1, 0, 0)
eA_lft = line_edge(v01, v00, p01,  0,-1, 0)
loopA = f.edge_loop([
    f.oriented_edge(eA_bot,  True),
    f.oriented_edge(seam_edge, True),   # (1,0)→(1,1) — seam face 1
    f.oriented_edge(eA_top,  True),
    f.oriented_edge(eA_lft,  True),
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], plane)

# ── Face B: unit square [1,0]→[2,1] (right) ──────────────────────────────────
eB_bot = line_edge(v10, v20, p10,  1, 0, 0)
eB_rgt = line_edge(v20, v21, p20,  0, 1, 0)
eB_top = line_edge(v21, v11, p21, -1, 0, 0)
loopB = f.edge_loop([
    f.oriented_edge(eB_bot,   True),
    f.oriented_edge(eB_rgt,   True),
    f.oriented_edge(eB_top,   True),
    f.oriented_edge(seam_edge, False),  # (1,1)→(1,0) reversed — seam face 2
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], plane)

# ── Face C: unit square [0,1]→[1,2] (upper-left) ────────────────────────────
eC_bot = line_edge(v01, v11, p01,  1, 0, 0)   # bottom of upper-left: (0,1)→(1,1)
eC_rgt = line_edge(v11, v12, p11,  0, 1, 0)
eC_top = line_edge(v12, v02, p12, -1, 0, 0)
eC_lft = line_edge(v02, v01, p02,  0,-1, 0)
# Third face using the seam_edge via its bottom (v01→v11 is a separate edge,
# but we wire seam_edge in reversed for the right side of this face:
# actually the seam edge is x=1,y=0→1; face C needs x=1,y=1→2 for its right side.
# For face C we use seam_edge as its BOTTOM (reusing v01→v11 via eC_bot).
# To get 3 incident faces on seam_edge, face C uses it as its right edge (x=1,y=0→1).
# But face C is at y=1→2, so the seam_edge doesn't fit geometrically.
# Instead make face C share the seam_edge from the top by being at y=0→1 too:
# Place face C as a third square [0,0]→[1,1] (same domain, alias) — IS valid for defect.
eC2_bot = line_edge(v00, v10, p00,  1, 0, 0)
eC2_top = line_edge(v11, v01, p11, -1, 0, 0)
eC2_lft = line_edge(v01, v00, p01,  0,-1, 0)
loopC = f.edge_loop([
    f.oriented_edge(eC2_bot,  True),
    f.oriented_edge(seam_edge, True),   # (1,0)→(1,1) — seam face 3 (non-manifold!)
    f.oriented_edge(eC2_top,  True),
    f.oriented_edge(eC2_lft,  True),
])
faceC = f.advanced_face([f.face_outer_bound(loopC)], plane)

# ── Face D: independent square [0,1]→[1,2] (well-formed fourth face) ─────────
eD_bot = line_edge(v01, v11, p01,  1, 0, 0)
eD_rgt = line_edge(v11, v12, p11,  0, 1, 0)
eD_top = line_edge(v12, v02, p12, -1, 0, 0)
eD_lft = line_edge(v02, v01, p02,  0,-1, 0)
loopD = f.edge_loop([
    f.oriented_edge(eD_bot, True),
    f.oriented_edge(eD_rgt, True),
    f.oriented_edge(eD_top, True),
    f.oriented_edge(eD_lft, True),
])
faceD = f.advanced_face([f.face_outer_bound(loopD)], plane)

# ── OPEN_SHELL: seam_edge with 3 incident faces IS wired into topology ────────
shell = f.open_shell([faceA, faceB, faceC, faceD])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
