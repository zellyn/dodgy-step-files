"""Me1054 — merge_duplicate_polygons_in_polygon_soup duplicate_group_iteration: 4 separate duplicate pairs forcing 4 outer-loop iterations (Branch 5).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 5 (*duplicate_group_iteration*) @ line 996:
  'while(!all_duplicate_polygons.empty()) { auto& duplicate_polygons = all_duplicate_polygons.back(); … }'
  — the outer while loop pops one group per iteration until all_duplicate_polygons is empty.
  Branch 5 fires for EACH iteration of this outer loop.

Defect pattern: a polygon soup with 4 independent duplicate pairs:
  - Group A: {tri0, tri1} — both (v0,v1,v2).
  - Group B: {tri2, tri3} — both (v3,v4,v5).
  - Group C: {tri4, tri5} — both (v6,v7,v8).
  - Group D: {tri6, tri7} — both (v9,v10,v11).
  Forces 4 outer-loop iterations, one per group.

Geometry: four spatially disjoint triangles each duplicated; groups at x=0, x=2, x=4, x=6.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1054",
    title="merge_duplicate_polygons duplicate_group_iteration: 4 independent duplicate pairs; outer while loop iterates 4 times (Branch 5)",
    defect_class="duplicate_triangles",
)

# Group A vertices.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(1.0, 0.0, 0.0)   # 1
a2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Group B vertices.
b0 = m.vertex(2.0, 0.0, 0.0)   # 3
b1 = m.vertex(3.0, 0.0, 0.0)   # 4
b2 = m.vertex(2.5, 1.0, 0.0)   # 5

# Group C vertices.
c0 = m.vertex(4.0, 0.0, 0.0)   # 6
c1 = m.vertex(5.0, 0.0, 0.0)   # 7
c2 = m.vertex(4.5, 1.0, 0.0)   # 8

# Group D vertices.
d0 = m.vertex(6.0, 0.0, 0.0)   # 9
d1 = m.vertex(7.0, 0.0, 0.0)   # 10
d2 = m.vertex(6.5, 1.0, 0.0)   # 11

# Group A: 2 identical copies.
t0 = m.triangle(a0, a1, a2)  # 0 — group A copy 1
t1 = m.triangle(a0, a1, a2)  # 1 — group A copy 2

# Group B: 2 identical copies.
t2 = m.triangle(b0, b1, b2)  # 2 — group B copy 1
t3 = m.triangle(b0, b1, b2)  # 3 — group B copy 2

# Group C: 2 identical copies.
t4 = m.triangle(c0, c1, c2)  # 4 — group C copy 1
t5 = m.triangle(c0, c1, c2)  # 5 — group C copy 2

# Group D: 2 identical copies.
t6 = m.triangle(d0, d1, d2)  # 6 — group D copy 1
t7 = m.triangle(d0, d1, d2)  # 7 — group D copy 2

# Assert all 4 groups — outer loop iterates once per group.
m.assert_duplicate_polygon_group([t0, t1], 2)
m.assert_duplicate_polygon_group([t2, t3], 2)
m.assert_duplicate_polygon_group([t4, t5], 2)
m.assert_duplicate_polygon_group([t6, t7], 2)
