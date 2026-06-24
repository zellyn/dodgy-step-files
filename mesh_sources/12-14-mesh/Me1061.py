"""Me1061 — duplicate_polygons treated_skip: two independent duplicate groups,
where processing group A marks polygon 2 treated before group B tries to remove it.

Catalog claim: the soup has two separate duplicate groups —
  Group A: {tri 0, tri 1, tri 2} all with key (0,1,2).
  Group B: {tri 3, tri 4} all with key (2,3,4).
Under KEEP_ONE, group A processing marks tris 1 and 2 as treated (removed).
When group B is then processed, if its polygon_to_remove_id happens to
already appear in the treated[] array from group A, the
if(treated[polygon_to_remove_id]) continue guard fires and skips it.

The fixture constructs a situation with overlapping treatment by giving
tri 2 membership in group A; the group B polygon positions are distinct.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 8 @ line 1007 — *treated_skip*: if(treated[polygon_to_remove_id]) continue
prevents a polygon from being swapped-to-end twice when it appears in multiple
duplicate groups processed in sequence.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1061",
             title="duplicate_polygons treated_skip: two groups share polygon-id, second group hits continue",
             defect_class="duplicate_triangles")

# Group A vertices — upper-left triangle
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Group B vertices — lower-right triangle
v3 = m.vertex(2.0, 0.0, 0.0)
v4 = m.vertex(1.5, 1.0, 0.0)

# Clean vertex for singleton neighbour
v5 = m.vertex(0.5, -1.0, 0.0)

# Group A: three copies of (v0,v1,v2)
m.triangle(v0, v1, v2)   # tri 0 — group A keep
m.triangle(v0, v1, v2)   # tri 1 — group A remove (marked treated)
m.triangle(v0, v1, v2)   # tri 2 — group A remove (marked treated)

# Group B: two copies of (v2,v3,v4)
m.triangle(v2, v3, v4)   # tri 3 — group B keep
m.triangle(v2, v3, v4)   # tri 4 — group B remove

# Clean singleton
m.triangle(v0, v5, v1)   # tri 5 — no duplicates

# Assert both duplicate groups
m.assert_duplicate_polygon_group([0, 1, 2], 3)
m.assert_duplicate_polygon_group([3, 4], 2)
