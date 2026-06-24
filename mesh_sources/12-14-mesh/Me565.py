"""Me565 — loopSubdivision edge_swap_candidacy: post-split edge connects new midpoint to old vertex.

Basic_TMesh.loopSubdivision Branch 6 (*edge_swap_candidacy*) @ line 151:
  'if(IS_VISITED2(e->v1) != IS_VISITED2(e->v2)) { e->swap(); }'
  — After all edges are split, the algorithm does a pass over all edges to
  identify swap candidates: an edge is swappable if exactly one of its two
  endpoints is IS_VISITED2 (a newly-inserted midpoint vertex) and the other
  is an original vertex (not IS_VISITED2). This "mixed" edge is the result of
  the split and may have poor aspect ratio; swapping it can improve mesh quality.
  This branch fires when such a mixed-endpoint edge exists.

Fixture: a 4-triangle mesh containing a long thin diagonal that would be a
  poor-quality post-split edge between a midpoint and an original vertex.
  The diagonal (v2, v4) has one endpoint that acts as the midpoint of the
  previous split (v2, midpoint of the original long edge) and one original vertex (v4).
  The aspect ratio of the two triangles sharing this diagonal is notably poor,
  signalling that a swap would improve quality.

Geometric signature:
  Two wide base triangles sharing a long diagonal. The diagonal (v1,v3) has a very
  poor aspect ratio (one endpoint is the "new" vertex, the other is "old").
  assert_triangle_aspect_ratio_gt captures the poor-quality triangle that motivates
  the swap.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me565",
    title="loopSubdivision edge_swap_candidacy: diagonal (v2,v3) connects new midpoint v2 to old vertex v3; poor aspect ratio motivates IS_VISITED2 swap (Branch 6)",
    defect_class="loop_subdivision",
)

# Four-vertex base quad split along a poor diagonal.
# v0 and v1 are the two original base vertices of a wide quad.
# v2 is the midpoint of the top edge (the "new" IS_VISITED2 vertex after split).
# v3 is the opposite original vertex.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — original bottom-left
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — original bottom-right
v2 = m.vertex(2.0, 0.1, 0.0)   # 2 — new midpoint vertex (nearly on base, creating thin triangle)
v3 = m.vertex(2.0, 3.0, 0.0)   # 3 — original top vertex (far from base)
v4 = m.vertex(0.0, 3.0, 0.0)   # 4 — original top-left
v5 = m.vertex(4.0, 3.0, 0.0)   # 5 — original top-right

# Two thin triangles sharing the poor diagonal (v2, v3):
# t0: base triangle — very flat because v2 is nearly on the base line.
t0 = m.triangle(v0, v1, v2)   # 0 — thin base triangle (v2 near base → aspect ratio very large)

# t1: connects new midpoint v2 to old vertex v3 — the "mixed endpoint" edge is (v2,v3).
t1 = m.triangle(v0, v2, v3)   # 1 — shares (v0,v2) and (v0,v3); diagonal (v2,v3) is the swap candidate

# Two more triangles to make the mesh connected and demonstrate the wider context.
t2 = m.triangle(v0, v3, v4)   # 2 — left upper; shares (v0,v3) with t1
t3 = m.triangle(v1, v5, v3)   # 3 — right upper; shares ... gives context

# The thin base triangle t0 has a very poor aspect ratio (height ≈ 0.1, base = 4.0).
m.assert_triangle_aspect_ratio_gt(t0, 5.0)

# The shared diagonal (v2,v3) connects new-midpoint v2 to old vertex v3 — swap candidate edge.
m.assert_edge_shared(v2, v3, 2)  # shared by t0... wait: t0=(v0,v1,v2); t1=(v0,v2,v3)
# t0 edges: (0,1),(1,2),(0,2); t1 edges: (0,2),(2,3),(0,3).
# (v2,v3) is NOT in t0. So (v2,v3) is only in t1. Need to add another triangle to share it.
# Let me add t4 sharing (v2,v3) as a proper swap edge: t4=(v1,v3,v2) — shares (v1,v2) with t0 and (v2,v3) with t1.
# BUT: t4=(v1,v3,v2) edges: (1,3),(2,3),(1,2). So (v2,v3) shared by t1 and t4 ✓; (v1,v2) shared by t0 and t4 ✓.

# Re-adding t4 to complete the swap-candidate structure:
t4 = m.triangle(v1, v3, v2)   # 4 — shares (v2,v3) with t1 and (v1,v2) with t0

# Now the diagonal (v2,v3) is shared by t1 and t4 (the swap-candidate edge, n=2).
m.assert_edge_shared(v2, v3, 2)

# The edge (v1,v2) is shared by t0 and t4 (n=2).
m.assert_edge_shared(v1, v2, 2)

# Interior edge (v0,v2) shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)

# Interior edge (v0,v3) shared by t1 and t2.
m.assert_edge_shared(v0, v3, 2)

# Thin triangle t0 has poor aspect ratio — motivates post-split edge swap.
m.assert_triangle_aspect_ratio_gt(t0, 5.0)

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v3, 1)   # wait: t3=(v1,v5,v3) → edges (1,5),(3,5),(1,3); and t4=(v1,v3,v2) → (1,3),(2,3),(1,2). So (1,3) shared by t3 and t4 → n=2!

# I need to avoid (v1,v3) being shared between t3 and t4. Let me restructure:
# Remove t3 and t4, replace with cleaner structure.
# Reset and restructure from Me565 scratch with fewer triangles but correct topology.
m.vertices.clear()
m.triangles.clear()
m.assertions.clear()

# Clean restart — minimal mesh for swap candidacy.
# Minimal: 4 triangles around the swap-candidate diagonal.
#
#  v3 --------- v4
#   |  \  t2  / |
#   |t3 \ | /t1 |
#   |    \|/    |
#  v0----v2----v1
#         t0 (thin)
#
# v2 = midpoint of (v0,v1) — the IS_VISITED2 vertex.
# Diagonal (v2, v3): one endpoint new (v2), one old (v3) → IS_VISITED2 swap candidate.

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — original left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — original right
v2 = m.vertex(1.0, 0.1, 0.0)   # 2 — new midpoint vertex (nearly on base → thin triangles)
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — original top-center
v4 = m.vertex(0.0, 2.0, 0.0)   # 4 — original top-left

# t0: thin base triangle (v2 is new midpoint near the base line).
t0 = m.triangle(v0, v1, v2)   # 0 — thin; edges (0,1),(1,2),(0,2)

# t1: upper-right triangle; shares (v1,v2) with t0; the diagonal (v2,v3) connects new v2 to old v3.
t1 = m.triangle(v1, v3, v2)   # 1 — edges (1,3),(2,3),(1,2)  → shares (1,2) with t0

# t2: upper-left triangle; shares (v2,v3) with t1 → (v2,v3) is interior n=2 (swap candidate).
t2 = m.triangle(v0, v2, v3)   # 2 — edges (0,2),(2,3),(0,3)  → shares (0,2) with t0, (2,3) with t1

# t3: top triangle; shares (v0,v3) with t2.
t3 = m.triangle(v0, v3, v4)   # 3 — edges (0,3),(3,4),(0,4)  → shares (0,3) with t2

# Interior edge (v2,v3): the swap-candidate edge — new midpoint v2 to old vertex v3.
m.assert_edge_shared(v2, v3, 2)  # shared by t1 and t2

# Interior edges.
m.assert_edge_shared(v0, v2, 2)  # shared by t0 and t2
m.assert_edge_shared(v1, v2, 2)  # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)  # shared by t2 and t3

# Thin triangle t0 has very poor aspect ratio (height ≈ 0.1, base = 2.0).
m.assert_triangle_aspect_ratio_gt(t0, 4.0)

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Euler characteristic: V=5, E=8, F=4, chi=1 (open disk).
m.assert_euler_characteristic(5, 8, 4, 1)
