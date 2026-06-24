"""Me524 — iterativeEdgeSwaps swap_norm_alignment: swap rejected because post-flip normals diverge (Branch 5).

Basic_TMesh.iterativeEdgeSwaps branch 5: swap_norm_alignment

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 5 (*swap_norm_alignment*) @ line 1588:
  'else if (nor*e->t1->getNormal() <= 0) { e->swap(1); }'  [undo]
  — after a swap is attempted, the algorithm checks whether the new triangles'
  normals are still consistent with the original normal direction. If the dot product
  of the original normal and the post-swap triangle normal is <= 0, the swap is
  undone (swap(1) reverses it). This prevents swaps that would create a "fold"
  in non-planar geometry.

Defect pattern: two adjacent triangles sharing an edge where they form a "fold" —
  their normals point in opposite directions. When the swap algorithm attempts to
  flip the shared edge, the resulting post-flip triangle normal would diverge from
  the pre-flip orientation, so the swap is rejected (undone).

Geometry: a non-planar "book" configuration — two triangles meeting at a spine
  (shared edge) with pages folding in opposite directions:
    v0=(0, 1, 0)  — top of spine (in XZ plane)
    v1=(0,-1, 0)  — bottom of spine
    v2=(1, 0, 1)  — right page apex (front-right)
    v3=(-1, 0,-1) — left page apex (back-left, opposite side)

  Current triangulation: spine (v0,v1) is the shared edge.
    t0=(v0,v1,v2) — front-right triangle, normal points roughly (+Z,+X direction)
    t1=(v0,v3,v1) — back-left triangle, normal points roughly (-Z,-X direction)
  These two triangles are on opposite sides of the plane → dot product < 0.

  Swapping to diagonal (v2,v3) would produce triangles that cross the original
  surface orientation → swap is undone by MeshFix.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me524",
    title="iterativeEdgeSwaps swap_norm_alignment: non-planar fold; adjacent triangles have anti-parallel normals, swap rejected (Branch 5)",
    defect_class="mesh_optimization",
)

# "Book" configuration: spine (v0,v1) vertical, pages folding opposite ways.
v0 = m.vertex( 0.0,  1.0,  0.0)   # 0 — top of spine
v1 = m.vertex( 0.0, -1.0,  0.0)   # 1 — bottom of spine
v2 = m.vertex( 1.0,  0.0,  1.0)   # 2 — front-right apex
v3 = m.vertex(-1.0,  0.0, -1.0)   # 3 — back-left apex (opposite side)

# t0: front-right page — normal = (v1-v0) × (v2-v0)
#   (v1-v0) = (0,-2,0); (v2-v0) = (1,-1,1)
#   cross = (-2*1-0*(-1), 0*1-0*1, 0*(-1)-(-2)*1) = (-2, 0, 2) → normalized: (-0.707, 0, 0.707)
t0 = m.triangle(v0, v1, v2)    # 0: front-right triangle

# t1: back-left page — normal = (v3-v0) × (v1-v0)
#   (v3-v0) = (-1,-1,-1); (v1-v0) = (0,-2,0)
#   cross = ((-1)*0-(-1)*(-2), (-1)*0-(-1)*0, (-1)*(-2)-(-1)*0) = (-2, 0, 2)
# Wait — let me use reversed winding to get opposite normal:
# t1=(v0,v3,v1): (v3-v0)×(v1-v0) = (-1,-1,-1)×(0,-2,0) = ((-1)*0-(-1)*(-2), (-1)*0-(-1)*0, (-1)*(-2)-(-1)*0) = (-2, 0, 2)
# Same normal — use (v1,v3,v0) instead:
# (v3-v1)×(v0-v1) = (-1,1,-1)×(0,2,0) = (1*0-(-1)*2, (-1)*0-(-1)*0, (-1)*2-1*0) = (2, 0, -2) → (+0.707, 0, -0.707)
# Dot with t0's normal: (-0.707)*(0.707) + 0 + (0.707)*(-0.707) = -0.5 - 0.5 = -1.0 → PASS
t1 = m.triangle(v1, v3, v0)    # 1: back-left triangle (normal anti-parallel to t0)

# Shared interior edge (v0,v1) — the spine / swap candidate.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# The two adjacent triangles have anti-parallel normals (dot product < 0) —
# t0 normal: (-0.707, 0, +0.707); t1 normal: (+0.707, 0, -0.707).
# This is the pre-condition for the swap_norm_alignment branch: any flip would
# encounter nor*getNormal() <= 0 and be undone.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
