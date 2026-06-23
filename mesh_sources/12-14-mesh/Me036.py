"""Me036 — duplicate_polygons: KEEP_ONE erase_policy_selection branch.

Catalog claim: three triangles use identical vertex-index tuple (0,1,2).
With erase_policy=KEEP_ONE the healer retains exactly one and removes two.
The polygon soup has 5 triangles total; after merge only 3 remain.

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 1 @ line 946 — *erase_policy_selection*: named parameter erase_policy
controls which duplicates to keep. KEEP_ONE: retain first, erase remaining.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me036",
             title="duplicate_polygons KEEP_ONE: three identical triangles, keep one remove two",
             defect_class="duplicate_triangles")

# Four vertices for a simple 2D mesh in z=0.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)

m.triangle(v0, v1, v2)   # tri 0 — original
m.triangle(v0, v1, v2)   # tri 1 — first copy (to erase under KEEP_ONE)
m.triangle(v0, v1, v2)   # tri 2 — second copy (to erase under KEEP_ONE)
m.triangle(v1, v3, v2)   # tri 3 — clean neighbour

# All three of tri 0, 1, 2 share the same canonical vertex key.
m.assert_duplicate_polygon_group([0, 1, 2], 3)
