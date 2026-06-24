"""Me1062 — duplicate_polygons swap_to_end: non-contiguous duplicates exercise
the std::swap(polygons[swap_position], polygons[polygon_to_remove_pos]) step.

Catalog claim: a 6-triangle soup has 3 copies of triangle (0,1,2) placed at
positions 0, 2, and 5 (non-contiguous). The swap_to_end mechanism works by
maintaining a swap_position cursor that starts at the last polygon and moves
backward. Each duplicate found at polygon_to_remove_pos is swapped with
swap_position so that duplicates accumulate at the back. This guarantees that
after all swaps, positions [3,4,5] form the back region that erase() will
remove.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 9 @ line 1026 — *swap_to_end*: std::swap(polygons[swap_position],
polygons[polygon_to_remove_pos]) moves each removal candidate to the back
partition without O(n) element-by-element shifting.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1062",
             title="duplicate_polygons swap_to_end: 3 duplicates at non-contiguous positions 0,2,5",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
# Clean triangle vertices
v3 = m.vertex(1.5, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(0.5, -1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — duplicate (kept under KEEP_ONE as first)
m.triangle(v1, v3, v2)   # tri 1 — clean
m.triangle(v0, v1, v2)   # tri 2 — duplicate (swapped to back)
m.triangle(v3, v4, v2)   # tri 3 — clean
m.triangle(v0, v5, v1)   # tri 4 — clean
m.triangle(v0, v1, v2)   # tri 5 — duplicate (swapped to back)

# The three duplicates are at positions 0, 2, 5
m.assert_duplicate_polygon_group([0, 2, 5], 3)
