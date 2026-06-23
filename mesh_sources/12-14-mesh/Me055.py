"""Me055 — sequential output-count limit: 3 SI pairs, limit fires after 2.

Catalog claim: the mesh contains three self-intersecting triangle pairs. CGAL
PMP.self_intersections_impl Branch 10 @ line 497 wraps the sequential AABB
callback in a `Count_and_throw_filter` when `do_limit` is true; after
`maximum_number` pairs are recorded the filter throws, stopping collection.
With 3 pairs present and limit=2, only pairs A and B are collected; pair C is
never appended.

Source: CGAL PMP.self_intersections_impl Branch 10 @ line 497 —
*output-limit-in-sequential*: sequential path wraps callback with counter lambda
/ Count_and_throw_filter; fires when pair count reaches maximum_number.

Defect carrier: three independent crossing pairs at x=0, x=10, x=20. Each pair
is a minimal XY/XZ crossing at a distinct apex. Sequential AABB walk visits them
in spatial order; counter fires after pair 2 (x=10) and exits before pair 3
(x=20).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me055",
             title="Sequential count-limit: 3 SI pairs; Count_and_throw_filter fires at limit 2",
             defect_class="self_intersection_sequential_count_limit")

# Pair A: apex at x=0.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(1.0, 1.0, 0.0)   # 1
a2 = m.vertex(1.0, -1.0, 0.0)  # 2
a3 = m.vertex(1.0, 0.0, 1.0)   # 3
a4 = m.vertex(1.0, 0.0, -1.0)  # 4
t0 = m.triangle(a0, a1, a2)
t1 = m.triangle(a0, a3, a4)

# Pair B: apex at x=10.
b0 = m.vertex(10.0, 0.0, 0.0)  # 5
b1 = m.vertex(11.0, 1.0, 0.0)  # 6
b2 = m.vertex(11.0, -1.0, 0.0) # 7
b3 = m.vertex(11.0, 0.0, 1.0)  # 8
b4 = m.vertex(11.0, 0.0, -1.0) # 9
t2 = m.triangle(b0, b1, b2)
t3 = m.triangle(b0, b3, b4)

# Pair C: apex at x=20.
c0 = m.vertex(20.0, 0.0, 0.0)  # 10
c1 = m.vertex(21.0, 1.0, 0.0)  # 11
c2 = m.vertex(21.0, -1.0, 0.0) # 12
c3 = m.vertex(21.0, 0.0, 1.0)  # 13
c4 = m.vertex(21.0, 0.0, -1.0) # 14
t4 = m.triangle(c0, c1, c2)
t5 = m.triangle(c0, c3, c4)

# Assert: all three SI pairs are present in the geometry.
m.assert_triangles_self_intersect(t0, t1)   # pair A
m.assert_triangles_self_intersect(t2, t3)   # pair B
m.assert_triangles_self_intersect(t4, t5)   # pair C (never reported under limit=2)
