"""Me277 — autorefine_triangle_soup: parallel-vs-sequential-deduplication (Branch 8).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 8 @ line 1284:
  'CGAL_LINKED_WITH_TBB && parallel_execution' — after all intersection points have
  been gathered, the implementation deduplicates them. If TBB is available and
  parallel execution was requested, it runs tbb::parallel_for over sorted index
  blocks; otherwise it uses a sequential loop.

The branch is a performance dispatch (parallel vs sequential), not a correctness
branch per se. The fixture demonstrates the input pattern that exercises the
deduplication phase: multiple triangle pairs that together produce many intersection
points, providing a pool large enough to motivate the parallel path.

Geometry: a fan of four intersecting triangles arranged radially, each crossing its
neighbor. Each pair produces a crossing segment, creating a set of intersection points
that require deduplication after collection.

Keywords: CGAL_LINKED_WITH_TBB, parallel_execution, tbb::parallel_for, deduplication.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me277",
             title="autorefine_triangle_soup parallel-vs-sequential dedup: multi-triangle SI pool",
             defect_class="autorefine_dedup_parallel")

# Four triangles arranged in a + pattern at z=0, each pair crossing neighbors.
# t0: horizontal  t1: vertical  → they intersect.
# t2: diagonal /  t3: diagonal \ → each crosses t0 or t1.

# Triangle 0: horizontal slab.
v0 = m.vertex(-2.0,  0.0, -0.5)  # 0
v1 = m.vertex( 2.0,  0.0, -0.5)  # 1
v2 = m.vertex( 0.0,  0.0,  0.5)  # 2

# Triangle 1: vertical slab, perpendicular to t0 in XZ, crossing t0.
v3 = m.vertex( 0.0, -2.0, -0.5)  # 3
v4 = m.vertex( 0.0,  2.0, -0.5)  # 4
v5 = m.vertex( 0.0,  0.0,  0.5)  # 5 — same as v2 position (shared apex touch)

# Triangle 2: tilted \\ shape, crossing t0 and t1.
v6 = m.vertex(-1.5, -1.0, -0.5)  # 6
v7 = m.vertex( 1.5,  1.0, -0.5)  # 7
v8 = m.vertex( 0.0,  0.0,  0.5)  # 8 — same apex position

# Triangle 3: tilted // shape, crossing t0 and t1.
v9  = m.vertex( 1.5, -1.0, -0.5)  # 9
v10 = m.vertex(-1.5,  1.0, -0.5)  # 10
v11 = m.vertex( 0.0,  0.0,  0.5)  # 11 — same apex position

t0 = m.triangle(v0, v1, v2)    # 0 — horizontal
t1 = m.triangle(v3, v4, v5)    # 1 — vertical
t2 = m.triangle(v6, v7, v8)    # 2 — diagonal
t3 = m.triangle(v9, v10, v11)  # 3 — anti-diagonal

# t0 and t1 cross each other.
m.assert_triangles_self_intersect(t0, t1)

# t0 and t2 cross each other.
m.assert_triangles_self_intersect(t0, t2)

# Shared apex positions (near-coincident vertices at the common tip).
m.assert_vertex_pair_distance_lt(v2, v5, 1e-12)
m.assert_vertex_pair_distance_lt(v2, v8, 1e-12)
m.assert_vertex_pair_distance_lt(v2, v11, 1e-12)
