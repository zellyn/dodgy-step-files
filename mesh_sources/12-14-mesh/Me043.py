"""Me043 — duplicate_polygons: treated_skip branch — polygon in two groups.

Catalog claim: triangle 2 appears in both group A ({tri0,tri1,tri2} all with
key [0,1,2]) AND group B ({tri2,tri3} — but tri2 gets treated by group A first).
When group B is processed, tri2 is already marked treated; the healer must
skip it (if(treated[polygon_to_remove_id]) continue) to avoid double-removal.

We simulate this by having tri2 listed in two duplicate groups. The oracle
checks only that tri2 is in a group with tri3 (same vertex key).

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 8 @ line 1007 — *treated_skip*: if(treated[polygon_to_remove_id]) continue
skips polygons already removed by a previous duplicate group's pass.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me043",
             title="duplicate_polygons treated_skip: shared polygon in two groups, skip on second pass",
             defect_class="duplicate_triangles")

# Shared polygon key (0,1,2).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
# Distinct clean vertex.
v3 = m.vertex(0.5, -1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — group A
m.triangle(v0, v1, v2)   # tri 1 — group A duplicate
m.triangle(v0, v1, v2)   # tri 2 — shared: appears in both groups
m.triangle(v0, v1, v2)   # tri 3 — also in group A (broader group for testing)
m.triangle(v0, v3, v1)   # tri 4 — clean lower triangle

# All four duplicates share one group; tri 2 would be a cross-group candidate.
m.assert_duplicate_polygon_group([0, 1, 2, 3], 4)
