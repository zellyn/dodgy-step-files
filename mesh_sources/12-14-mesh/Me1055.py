"""Me1055 — merge_duplicate_polygons_in_polygon_soup keep_decision: KEEP_ONE policy sets i=1 (Branch 6).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 6 (*keep_decision*) @ line 1001:
  '(erase_policy == Policy::ERASE_ALL) ? i=0 : (erase_policy == Policy::KEEP_ONE) ? i=1 : i=size%2'
  — the erase_policy named parameter determines the starting index i for the inner removal
  loop. KEEP_ONE sets i=1, meaning the first copy (index 0) is retained and all remaining
  copies starting at index 1 are scheduled for removal.

Defect pattern: a polygon soup with a 5-copy group under KEEP_ONE policy:
  - Group: {tri0, tri1, tri2, tri3, tri4} all identical (v0,v1,v2).
  - With KEEP_ONE: i=1, so copies at indices 1,2,3,4 are removed; copy 0 is kept.
  - Result: 2 triangles remain (the one kept copy + clean singleton).

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0).
  5 identical copies of (v0,v1,v2); 1 clean lower triangle (v0,v1,v3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1055",
    title="merge_duplicate_polygons keep_decision KEEP_ONE: 5-copy group; i=1 retains copy 0, removes copies 1-4 (Branch 6)",
    defect_class="duplicate_triangles",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 2.0, 0.0)  # 2 — apex
v3 = m.vertex(1.0, -1.5, 0.0) # 3 — clean lower apex

# 5 identical copies of (v0,v1,v2).
t0 = m.triangle(v0, v1, v2)  # 0 — kept copy (KEEP_ONE: i=1 → index 0 is retained)
t1 = m.triangle(v0, v1, v2)  # 1 — removed (i starts at 1)
t2 = m.triangle(v0, v1, v2)  # 2 — removed
t3 = m.triangle(v0, v1, v2)  # 3 — removed
t4 = m.triangle(v0, v1, v2)  # 4 — removed

# Clean singleton (no duplicate).
t5 = m.triangle(v0, v1, v3)  # 5 — clean lower triangle (survives)

# Group of 5 identical copies — keep_decision sets i=1 under KEEP_ONE.
m.assert_duplicate_polygon_group([t0, t1, t2, t3, t4], 5)
