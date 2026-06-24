"""Me1064 — duplicate_polygons final_erase: polygons.erase(first, polygons.end())
physically shrinks the container after two independent duplicate groups are removed.

Catalog claim: the soup has two separate duplicate groups —
  Group A: {tri 0, tri 1} with key (0,1,2) — 2 copies; KEEP_ONE keeps 1.
  Group B: {tri 3, tri 4, tri 5} with key (0,1,3) — 3 copies; KEEP_ONE keeps 1.
After the outer while-loop processes both groups and swap_to_end has moved
4 polygons (tris 1, 4, 5, and the surplus of one group) to the back, the
single polygons.erase(first, polygons.end()) call at line 1035 physically
removes all of them in one operation. The container shrinks from 7 triangles
(5 duplicates + 1 clean) to 3 (1 survivor per group + 1 clean singleton).

Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup
Branch 11 @ line 1035 — *final_erase*: polygons.erase(first, polygons.end())
executes once after all groups are processed to physically remove the entire
back region in a single O(k) container resize where k = number of removed polygons.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1064",
             title="duplicate_polygons final_erase: two groups erased together by single erase() call",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 0.0, 0.0)
# Clean vertex
v4 = m.vertex(0.5, -1.0, 0.0)

# Group A: 2 copies of (v0,v1,v2)
m.triangle(v0, v1, v2)   # tri 0 — group A keep
m.triangle(v0, v1, v2)   # tri 1 — group A remove (swapped to back)

# Clean singleton (sits between the two groups)
m.triangle(v0, v4, v1)   # tri 2 — clean (survives)

# Group B: 3 copies of (v0,v1,v3)
m.triangle(v0, v1, v3)   # tri 3 — group B keep
m.triangle(v0, v1, v3)   # tri 4 — group B remove (swapped to back)
m.triangle(v0, v1, v3)   # tri 5 — group B remove (swapped to back)

# Assert both groups
m.assert_duplicate_polygon_group([0, 1], 2)
m.assert_duplicate_polygon_group([3, 4, 5], 3)
