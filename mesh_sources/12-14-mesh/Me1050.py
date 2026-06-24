"""Me1050 — merge_duplicate_polygons_in_polygon_soup erase_policy_selection: KEEP_ONE_IF_ODD with 3-copy group (Branch 1).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 1 (*erase_policy_selection*) @ line 946:
  'erase_policy = choose_parameter(get_parameter(np, internal_np::erase_policy), …)'
  — the named parameter erase_policy is resolved before any polygon scan begins.
  KEEP_ONE_IF_ODD sets i = size%2 (keeps the group only when group size is odd).

Defect pattern: a polygon soup with a group of 3 identical triangles (0,1,2) and a
  group of 2 identical triangles (3,4,5) alongside a clean singleton triangle.
  Under KEEP_ONE_IF_ODD:
  - group of 3 (odd) → keep 1, remove 2
  - group of 2 (even) → erase all 2
  The named-parameter branch fires before any polygon is inspected.

Geometry:
  Upper-left: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — triplicated.
  Upper-right: v3=(2,0,0), v4=(3,0,0), v5=(2.5,1,0) — duplicated.
  Clean singleton (bottom): v6=(0.5,-1,0) shares base edge with upper-left vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1050",
    title="merge_duplicate_polygons erase_policy_selection KEEP_ONE_IF_ODD: 3-copy group (odd→keep1) + 2-copy group (even→erase all) (Branch 1)",
    defect_class="duplicate_triangles",
)

# Upper-left triangle group — 3 identical copies.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2

# Upper-right triangle group — 2 identical copies.
v3 = m.vertex(2.0, 0.0, 0.0)  # 3
v4 = m.vertex(3.0, 0.0, 0.0)  # 4
v5 = m.vertex(2.5, 1.0, 0.0)  # 5

# Clean singleton — no duplicates.
v6 = m.vertex(0.5, -1.0, 0.0)  # 6

# Group A: 3 identical copies of triangle (v0,v1,v2).
t0 = m.triangle(v0, v1, v2)  # 0 — group A copy 1
t1 = m.triangle(v0, v1, v2)  # 1 — group A copy 2 (remove under KEEP_ONE_IF_ODD: odd=3 → keep 1)
t2 = m.triangle(v0, v1, v2)  # 2 — group A copy 3 (remove)

# Group B: 2 identical copies of triangle (v3,v4,v5).
t3 = m.triangle(v3, v4, v5)  # 3 — group B copy 1 (remove under KEEP_ONE_IF_ODD: even=2 → erase all)
t4 = m.triangle(v3, v4, v5)  # 4 — group B copy 2 (remove)

# Clean singleton.
t5 = m.triangle(v0, v1, v6)  # 5 — clean (survives)

# Group A: 3 copies share the same canonical vertex key.
m.assert_duplicate_polygon_group([t0, t1, t2], 3)

# Group B: 2 copies share the same canonical vertex key.
m.assert_duplicate_polygon_group([t3, t4], 2)
