"""Me820 — does_polygon_soup_self_intersect branch 1: duplicate_point_presence.

PMP.does_polygon_soup_self_intersect Branch 1 (*duplicate_point_presence*) @ line 40:
  Before running the SI check on the raw polygon soup, the function calls
  `merge_duplicate_points_in_polygon_soup` so that coincident-coordinate vertex
  pairs are collapsed to a single point entry.  Branch 1 fires whenever the soup
  contains at least one pair of geometrically identical (duplicate-coordinate)
  points — i.e. when that merge step does real work rather than being a no-op.

Defect pattern: three triangles in a flat XY soup where vertex v3 is a second
  copy of v0 at (0,0,0) with a distinct index.  After duplicate-point merging,
  index 3 is remapped to 0 and the de-duplicated soup has only 3 unique points
  (v0,v1,v2).  The fixture records the spatial coincidence and the absence of any
  shared triangle between v0 and v3 — confirming they are the same coordinate but
  topologically separate entries as required by the branch pre-condition.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(0,0,0) [coincident with v0]
  t0=(v0,v1,v2): base triangle
  t1=(v3,v2,v1): second triangle referencing duplicate of v0
  (Two triangles with the same winding — merge fires to consolidate v0==v3.)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me820",
    title="does_polygon_soup_self_intersect duplicate_point_presence: v0==v3 at (0,0,0); merge_duplicate_points fires before SI check (Branch 1)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — base vertex (first occurrence)
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.0, 1.0, 0.0)  # 2
v3 = m.vertex(0.0, 0.0, 0.0)  # 3 — duplicate of v0, distinct index

# t0 references the original v0.
t0 = m.triangle(v0, v1, v2)   # 0: base triangle
# t1 references the duplicate v3 instead of v0.
t1 = m.triangle(v3, v2, v1)   # 1: second triangle using duplicate v3

# v0 and v3 are spatially identical — merge_duplicate_points_in_polygon_soup
# will collapse them, triggering Branch 1 of does_polygon_soup_self_intersect.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
# They appear in separate triangles (no shared triangle entry in index list).
m.assert_vertex_pair_no_shared_triangle(v0, v3)
