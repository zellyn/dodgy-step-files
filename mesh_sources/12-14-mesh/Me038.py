"""Me038 — duplicate_polygons: duplicate_collection branch — hash+equality scan.

Catalog claim: a polygon soup of 6 triangles contains two independent
duplicate groups: group A = {tri 0, tri 1} both (0,1,2); group B = {tri 3, tri 4}
both (3,4,5). The collection step must identify BOTH groups correctly before
any removal begins.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 3 @ line 971 — *duplicate_collection*: scan all polygons for canonical
duplicates using hash+equality; collect groups of duplicate polygon indices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me038",
             title="duplicate_polygons duplicate_collection: two independent duplicate groups",
             defect_class="duplicate_triangles")

# First triangle pair — upper left
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Second triangle pair — upper right (disjoint vertices)
v3 = m.vertex(2.0, 0.0, 0.0)
v4 = m.vertex(3.0, 0.0, 0.0)
v5 = m.vertex(2.5, 1.0, 0.0)

# Singleton clean triangle bridging both groups
v6 = m.vertex(1.5, 0.5, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — group A original
m.triangle(v0, v1, v2)   # tri 1 — group A duplicate
m.triangle(v0, v2, v6)   # tri 2 — singleton (clean)
m.triangle(v3, v4, v5)   # tri 3 — group B original
m.triangle(v3, v4, v5)   # tri 4 — group B duplicate
m.triangle(v4, v6, v5)   # tri 5 — singleton (clean)

# Two independent duplicate groups to be collected.
m.assert_duplicate_polygon_group([0, 1], 2)
m.assert_duplicate_polygon_group([3, 4], 2)
