"""Me1052 — merge_duplicate_polygons_in_polygon_soup duplicate_collection: hash+equality scan with 4-copy and 3-copy groups (Branch 3).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 3 (*duplicate_collection*) @ line 971:
  'collect_duplicate_polygons(points, polygons, np, all_duplicate_polygons)'
  — the collection step hashes each polygon's canonical vertex-index set and groups
  identical polygons together. Branch 3 fires during the hash+equality scan.

Defect pattern: a polygon soup with a 4-copy group and a 3-copy group:
  - Group A: triangles (0,1,2) appears 4 times → {tri0, tri1, tri2, tri3}.
  - Group B: triangles (3,4,5) appears 3 times → {tri4, tri5, tri6}.
  Two clean singletons separate the groups. The collection step must correctly
  identify BOTH groups and their complete membership.

Geometry:
  Left 4-copy: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0).
  Right 3-copy: v3=(2,0,0), v4=(3,0,0), v5=(2.5,1,0).
  Two singleton vertices for the clean triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1052",
    title="merge_duplicate_polygons duplicate_collection: 4-copy group A + 3-copy group B; hash+equality scan collects both (Branch 3)",
    defect_class="duplicate_triangles",
)

# Left 4-copy triangle.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2

# Right 3-copy triangle.
v3 = m.vertex(2.0, 0.0, 0.0)  # 3
v4 = m.vertex(3.0, 0.0, 0.0)  # 4
v5 = m.vertex(2.5, 1.0, 0.0)  # 5

# Singleton clean triangle vertices.
v6 = m.vertex(1.5, 0.0, 0.0)  # 6 — bridge vertex for singleton

# Group A: 4 identical copies of (v0,v1,v2).
t0 = m.triangle(v0, v1, v2)  # 0 — group A copy 1
t1 = m.triangle(v0, v1, v2)  # 1 — group A copy 2
t2 = m.triangle(v0, v1, v2)  # 2 — group A copy 3
t3 = m.triangle(v0, v1, v2)  # 3 — group A copy 4

# Clean singleton bridging between groups.
t4 = m.triangle(v2, v6, v3)  # 4 — singleton clean

# Group B: 3 identical copies of (v3,v4,v5).
t5 = m.triangle(v3, v4, v5)  # 5 — group B copy 1
t6 = m.triangle(v3, v4, v5)  # 6 — group B copy 2
t7 = m.triangle(v3, v4, v5)  # 7 — group B copy 3

# Assert both groups are collected by the duplicate_collection branch.
m.assert_duplicate_polygon_group([t0, t1, t2, t3], 4)
m.assert_duplicate_polygon_group([t5, t6, t7], 3)
