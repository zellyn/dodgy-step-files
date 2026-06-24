"""Me1060 — duplicate_polygons removal_iteration: 5-copy group forces 4 inner-loop passes.

Catalog claim: a group of 5 identical triangles (all sharing vertex-index tuple
(0,1,2)) forces the inner removal loop (for(; i<duplicate_polygons.size(); ++i))
to iterate 4 times under KEEP_ONE — keeping index 0 and removing indices 1-4.
The 6-triangle soup shrinks to 2 after merging.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 7 @ line 1004 — *removal_iteration*: for(; i<duplicate_polygons.size(); ++i)
iterates over each polygon in the duplicate group that must be removed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1060",
             title="duplicate_polygons removal_iteration: 5-copy group, inner loop runs 4 times",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)

# Five identical triangles — the inner loop must iterate 4 times (KEEP_ONE keeps tri 0).
m.triangle(v0, v1, v2)   # tri 0 — kept under KEEP_ONE
m.triangle(v0, v1, v2)   # tri 1 — removal iteration 1
m.triangle(v0, v1, v2)   # tri 2 — removal iteration 2
m.triangle(v0, v1, v2)   # tri 3 — removal iteration 3
m.triangle(v0, v1, v2)   # tri 4 — removal iteration 4
m.triangle(v1, v3, v2)   # tri 5 — clean neighbour (survives)

m.assert_duplicate_polygon_group([0, 1, 2, 3, 4], 5)
