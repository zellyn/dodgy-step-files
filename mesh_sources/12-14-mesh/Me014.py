"""Me014 — disconnected_components: two separate triangle shells, no shared vertices.

Catalog claim: the mesh has two fully disconnected connected components —
a large triangle and a tiny noise triangle far away. Shell traversal starting
from triangle 0 cannot reach triangle 1 without global index search. CGAL
keep_largest_connected_components / remove_connected_components_of_negligible_size
and MeshFix removeSmallestComponents both address this defect.

Defect carrier: triangles 0-2 form one closed triangular patch; triangles 3-4
form a tiny separate patch 100 units away, with no shared vertices or edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me014",
             title="disconnected components: large patch plus tiny noise triangle 100 units away",
             defect_class="disconnected_components")

# Component A: a small triangulated quad (4 triangles) near the origin.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(0.5, 0.5, 0.5)   # apex
m.triangle(v0, v1, v4)   # face 0
m.triangle(v1, v2, v4)   # face 1
m.triangle(v2, v3, v4)   # face 2
m.triangle(v3, v0, v4)   # face 3

# Component B: a tiny triangle 100 units away — the "noise island".
v5 = m.vertex(100.0, 100.0, 100.0)
v6 = m.vertex(100.01, 100.0, 100.0)
v7 = m.vertex(100.0, 100.01, 100.0)
m.triangle(v5, v6, v7)   # face 4: disconnected noise

# Assert: triangle 4 is not reachable (by shared-edge walk) from triangle 0.
m.assert_triangle_not_reachable_from(4, 0)
