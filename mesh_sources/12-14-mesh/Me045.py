"""Me045 — duplicate_polygons: mark_treated + final_erase branches combined.

Catalog claim: after all swap-to-end passes, the healer sets
treated[polygon_to_remove_id]=true for every removed polygon (Branch 10),
then calls polygons.erase(first, polygons.end()) to physically shrink the
container (Branch 11). This fixture contains a soup where a KEEP_ONE_IF_ODD
policy scenario arises: 3 copies of a triangle (odd count) keeps 1 under that
policy, removing 2; the treated[] bit-vector must cover exactly those 2, and
erase() must resize from 5 to 3 polygons.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 10 @ line 1029 — *mark_treated*: treated[polygon_to_remove_id] = true
Branch 11 @ line 1035 — *final_erase*: polygons.erase(first, polygons.end())
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me045",
             title="duplicate_polygons mark_treated+final_erase: KEEP_ONE_IF_ODD with 3 copies",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)

# Three copies of the same triangle: KEEP_ONE_IF_ODD keeps 1 (odd count → 3%2=1 kept).
m.triangle(v0, v1, v2)   # tri 0 — kept
m.triangle(v0, v1, v2)   # tri 1 — marked treated, erased
m.triangle(v0, v1, v2)   # tri 2 — marked treated, erased
m.triangle(v1, v3, v2)   # tri 3 — clean survivor
m.triangle(v3, v4, v2)   # tri 4 — clean survivor

# Three-way duplicate group; treated[] covers tris 1 and 2; erase() shrinks to 3.
m.assert_duplicate_polygon_group([0, 1, 2], 3)
