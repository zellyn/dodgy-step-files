"""Me1063 — duplicate_polygons mark_treated: treated[] bit written for each
removed polygon, preventing re-processing in subsequent duplicate groups.

Catalog claim: the soup has two separate duplicate groups —
  Group A: {tri 0, tri 1, tri 2} with key (0,1,2) — 3 copies.
  Group B: {tri 3, tri 4} with key (0,2,3) — 2 copies.
After group A is processed with KEEP_ONE, treated[tri1]=true and
treated[tri2]=true are written. When the outer while-loop then processes
group B, the treated[] array is consulted for each polygon_to_remove_id.
Any polygon_to_remove_id that is already marked treated is skipped via
the Branch 8 guard; the mark_treated write (Branch 10) happens for each
polygon that is NOT yet treated and is swapped to the back region.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 10 @ line 1029 — *mark_treated*: treated[polygon_to_remove_id] = true
records each polygon that has been swapped-to-end so that later groups
(or a re-encounter of the same id) will skip it cleanly.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1063",
             title="duplicate_polygons mark_treated: two groups; treated[] written per removed polygon",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, -1.0, 0.0)
# Clean vertex
v4 = m.vertex(1.5, 1.0, 0.0)

# Group A: 3 copies of (v0,v1,v2)
m.triangle(v0, v1, v2)   # tri 0 — group A keep
m.triangle(v0, v1, v2)   # tri 1 — group A remove; treated[1]=true written
m.triangle(v0, v1, v2)   # tri 2 — group A remove; treated[2]=true written

# Group B: 2 copies of (v0,v2,v3)
m.triangle(v0, v2, v3)   # tri 3 — group B keep
m.triangle(v0, v2, v3)   # tri 4 — group B remove; treated[4]=true written

# Clean singleton
m.triangle(v1, v4, v2)   # tri 5 — no duplicates

# Assert both groups
m.assert_duplicate_polygon_group([0, 1, 2], 3)
m.assert_duplicate_polygon_group([3, 4], 2)
