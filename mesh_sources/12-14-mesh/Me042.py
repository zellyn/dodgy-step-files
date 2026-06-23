"""Me042 — duplicate_polygons: removal_iteration branch — inner loop over removal list.

Catalog claim: a group of 4 identical triangles forces the inner removal loop
(for(; i < duplicate_polygons.size(); ++i)) to iterate 3 times under KEEP_ONE
(i starts at 1, removes indices 1, 2, 3 while keeping index 0).

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 7 @ line 1004 — *removal_iteration*: for(; i<duplicate_polygons.size(); ++i)
skip if already treated, else swap to end region.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me042",
             title="duplicate_polygons removal_iteration: 4-copy group, inner loop runs 3 times",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)

# Four identical triangles — the inner loop must iterate to remove the last 3.
m.triangle(v0, v1, v2)   # tri 0 — kept under KEEP_ONE
m.triangle(v0, v1, v2)   # tri 1 — first removal
m.triangle(v0, v1, v2)   # tri 2 — second removal
m.triangle(v0, v1, v2)   # tri 3 — third removal
m.triangle(v1, v3, v2)   # tri 4 — clean neighbour

m.assert_duplicate_polygon_group([0, 1, 2, 3], 4)
