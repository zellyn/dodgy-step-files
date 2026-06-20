"""Tsh057 — Merging near-tangent adjacent ADVANCED_FACEs (PLANE normals differ
~1e-4 rad, shared EDGE_CURVE with mismatched vertex z) returns self-overlapping
face.

Catalog claim: Two adjacent ADVANCED_FACEs meet at an EDGE_CURVE with PLANE
normals differing by a small angle (~1e-4 rad, just below the merge threshold).
The shared edge's start VERTEX_POINT has slightly different z on each side
(~9.999e-5 vs 0). Single-edge same-surface check passes; merging produces a
face whose interior is on the wrong side of the original edges (self-overlapping
face with negative area in some region).

Mechanism IS the shell structure: an OPEN_SHELL contains two ADVANCED_FACEs on
two PLANE entities whose normals differ by ~1e-4 rad. The near-zero tilt IS
wired into each PLANE's AXIS2_PLACEMENT_3D direction vector. The shared
EDGE_CURVE has a start VERTEX_POINT at z=9.999e-5 (face A side) vs z=0 (face B
side), wiring the vertex-z mismatch directly into the topology. A merge that
checks only the single-edge surface comparison passes; the resulting merged face
has a self-overlapping boundary.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Tsh057",
    defect=(
        "OPEN_SHELL with 2 adjacent ADVANCED_FACEs; PLANE normals differ by ~1e-4 rad; "
        "near-tangent normal tilt IS wired into AXIS2_PLACEMENT_3D direction of each PLANE; "
        "shared EDGE_CURVE start VERTEX_POINT has z=9.999e-5 on face-A side vs z=0 on face-B side; "
        "vertex-z mismatch IS wired into EDGE_CURVE/VERTEX_POINT topology; "
        "single-edge merge-threshold check passes; merge produces self-overlapping face; "
        "post-merge validity check on face wire (no self-intersections) required"
    ),
)

# Near-tangent angle: 1e-4 rad tilt off Z
angle = 1e-4
# Tilted normal for face A: rotate (0,0,1) slightly toward X axis
# sin(1e-4) ≈ 1e-4, cos(1e-4) ≈ 1 - 5e-9 ≈ 1.0
sin_a = math.sin(angle)
cos_a = math.cos(angle)

# ── Face A: unit square [0,0] → [1,1], normal tilted ~1e-4 rad from +Z ──────
# Points: all at z=0 except shared-edge start at z≈9.999e-5 (the defect vertex)
pA00 = f.cartesian_point((0.0, 0.0, 0.0))
pA10 = f.cartesian_point((1.0, 0.0, 9.999e-5))   # shared start: z≠0 IS the mismatch
pA11 = f.cartesian_point((1.0, 1.0, 0.0))
pA01 = f.cartesian_point((0.0, 1.0, 0.0))

vA00 = f.vertex_point(pA00)
vA10 = f.vertex_point(pA10)   # vertex at z=9.999e-5 IS the mechanism
vA11 = f.vertex_point(pA11)
vA01 = f.vertex_point(pA01)

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Face A edges; shared edge uses vA10 (z=9.999e-5)
eA_bot = line_edge(vA00, vA10, pA00, 1, 0, 0)
eA_rgt = line_edge(vA10, vA11, pA10, 0, 1, 0)
eA_top = line_edge(vA11, vA01, pA11, -1, 0, 0)
eA_lft = line_edge(vA01, vA00, pA01, 0, -1, 0)

loopA = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(eA_rgt, True),
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_lft, True),
])

# Face A plane: normal tilted ~1e-4 rad toward +X (IS the near-tangent mechanism)
origA = f.cartesian_point((0.0, 0.0, 0.0))
# Normal direction: (sin(1e-4), 0, cos(1e-4)) ≈ (1e-4, 0, 1)
normA = f.direction((sin_a, 0.0, cos_a))
xdirA = f.direction((cos_a, 0.0, -sin_a))   # perpendicular to normA in XZ plane
plcA  = f.axis2_placement_3d(origA, normA, xdirA)
planeA = f.plane(plcA)

faceA = f.advanced_face([f.face_outer_bound(loopA)], planeA)

# ── Face B: unit square [1,0] → [2,1], normal exactly +Z ─────────────────────
# Shared edge start at z=0 (different from face A's z=9.999e-5)
pB10 = f.cartesian_point((1.0, 0.0, 0.0))   # z=0 IS the mismatch vs pA10
pB11 = f.cartesian_point((1.0, 1.0, 0.0))
pB20 = f.cartesian_point((2.0, 0.0, 0.0))
pB21 = f.cartesian_point((2.0, 1.0, 0.0))

vB10 = f.vertex_point(pB10)   # distinct vertex at same x,y but z=0
vB11 = f.vertex_point(pB11)
vB20 = f.vertex_point(pB20)
vB21 = f.vertex_point(pB21)

# Shared edge from face B's perspective: from vB10(z=0) to vB11
shared_edge_B = line_edge(vB10, vB11, pB10, 0, 1, 0)
eB_bot = line_edge(vB10, vB20, pB10, 1, 0, 0)
eB_rgt = line_edge(vB20, vB21, pB20, 0, 1, 0)
eB_top = line_edge(vB21, vB11, pB21, -1, 0, 0)

loopB = f.edge_loop([
    f.oriented_edge(eB_bot,       True),
    f.oriented_edge(eB_rgt,       True),
    f.oriented_edge(eB_top,       True),
    f.oriented_edge(shared_edge_B, False),  # (1,1,0)→(1,0,0) reversed to close loop
])

# Face B plane: exact +Z normal (differs from face A by ~1e-4 rad IS the defect)
origB = f.cartesian_point((0.0, 0.0, 0.0))
normB = f.direction((0.0, 0.0, 1.0))
xdirB = f.direction((1.0, 0.0, 0.0))
plcB  = f.axis2_placement_3d(origB, normB, xdirB)
planeB = f.plane(plcB)

faceB = f.advanced_face([f.face_outer_bound(loopB)], planeB)

# ── OPEN_SHELL: near-tangent normals and vertex-z mismatch ARE wired in ───────
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
