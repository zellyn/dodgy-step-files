"""Me044 — duplicate_polygons: swap_to_end branch — polygon swapped to removal region.

Catalog claim: the healer's remove step does std::swap(polygons[swap_position],
polygons[polygon_to_remove_pos]) to partition the polygon list — moving the
duplicate to the back region that will be erased. This means after the swap
the "active" polygon at swap_position might be a previously-good polygon.
The fixture has 5 triangles; 2 duplicates. After swap+erase the order in
the survivor region changes (active polygon from swap fills the old dup slot).

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 9 @ line 1026 — *swap_to_end*: std::swap(polygons[swap_position],
polygons[polygon_to_remove_pos]) moves duplicates to end without an O(n) erase.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me044",
             title="duplicate_polygons swap_to_end: duplicate swapped to back then erased",
             defect_class="duplicate_triangles")

# Five-triangle soup: two interleaved duplicates so swap displaces a non-dup.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — original (stays)
m.triangle(v1, v3, v2)   # tri 1 — clean (displaced by swap)
m.triangle(v0, v1, v2)   # tri 2 — duplicate of tri 0 (swapped to back, erased)
m.triangle(v1, v4, v3)   # tri 3 — clean
m.triangle(v0, v1, v2)   # tri 4 — second duplicate (also swapped to back, erased)

# Tri 0, 2, 4 form the duplicate group; swap_to_end touches tri 2 and tri 4.
m.assert_duplicate_polygon_group([0, 2, 4], 3)
