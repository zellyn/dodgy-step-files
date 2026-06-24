"""Me1051 — merge_duplicate_polygons_in_polygon_soup orientation_requirement: two reversed-winding pairs needing same_orientation flag (Branch 2).

CGAL PMP `PMP.merge_duplicate_polygons_in_polygon_soup` Branch 2 (*orientation_requirement*) @ line 955:
  'same_orientation = choose_parameter(get_parameter(np, internal_np::same_orientation), true)'
  — the named parameter require_same_orientation controls whether winding-reversed copies
  are treated as duplicates (false) or distinct (true).

Defect pattern: a 5-triangle soup with two reversed-winding pairs:
  - Pair A: tri0=(v0,v1,v2) CCW and tri1=(v0,v2,v1) CW — same vertex set, opposite winding.
  - Pair B: tri3=(v3,v4,v5) CCW and tri4=(v3,v5,v4) CW — same vertex set, opposite winding.
  With require_same_orientation=false both pairs are treated as duplicates.
  With require_same_orientation=true neither pair is merged.

Geometry:
  Left pair: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0).
  Right pair: v3=(2,0,0), v4=(3,0,0), v5=(2.5,1,0).
  Clean bottom: (shared v0,v1 base with lower apex v6).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1051",
    title="merge_duplicate_polygons orientation_requirement: two reversed-winding pairs; same_orientation flag controls merge (Branch 2)",
    defect_class="duplicate_triangles",
)

# Left reversed pair.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2

# Right reversed pair.
v3 = m.vertex(2.0, 0.0, 0.0)  # 3
v4 = m.vertex(3.0, 0.0, 0.0)  # 4
v5 = m.vertex(2.5, 1.0, 0.0)  # 5

# Clean bottom singleton.
v6 = m.vertex(1.5, -1.0, 0.0)  # 6

# Pair A: CCW and CW copies of same triangle.
t0 = m.triangle(v0, v1, v2)  # 0 — CCW (outward normal +z)
t1 = m.triangle(v0, v2, v1)  # 1 — CW (outward normal -z; reversed winding)

# Pair B: CCW and CW copies of same triangle.
t3 = m.triangle(v3, v4, v5)  # 2 — CCW
t4 = m.triangle(v3, v5, v4)  # 3 — CW (reversed winding)

# Clean singleton.
t5 = m.triangle(v0, v1, v6)  # 4 — clean bottom (no duplicate)

# Assert both reversed pairs — exercises orientation_requirement branch.
m.assert_reversed_polygon_pair(t0, t1)
m.assert_reversed_polygon_pair(t3, t4)
