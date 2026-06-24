"""Me762 — retriangulateVT_retriangulation_quality_check: new triangles overlap or are exactly degenerate; quality check breaks out of loop (Branch 3).

MeshFix `holeFilling::retriangulateVT` Branch 3 (*RETRIANGULATION_QUALITY_CHECK*) @ line 409:
  'if (t->overlaps() || t->isExactlyDegenerate()) { break; }'
  After TriangulateHole produces new triangles to fill the vertex neighborhood,
  retriangulateVT checks each new triangle for quality. If any new triangle
  overlaps with existing geometry or is exactly degenerate (zero area), the
  loop breaks — Branch 3 fires and triggers the rollback path.

Defect pattern: a vertex hub v0 surrounded by a near-degenerate triangle fan.
  The critical triangle t_bad=(v0,v1,v2) is exactly degenerate: all three
  vertices are collinear (v1, v0, and v2 all lie on the X-axis at y=0).
  When retriangulateVT inserts this zero-area triangle, the quality check
  detects isExactlyDegenerate() == true → Branch 3 fires, loop breaks.

Geometry:
  v0=(1,0,0), v1=(0,0,0), v2=(2,0,0) — collinear on X-axis (degenerate t0)
  v3=(0,1,0), v4=(2,1,0) — outer vertices for context triangles
  t0=(v0,v1,v2): EXACTLY DEGENERATE (zero area — all three collinear at y=0)
  t1=(v0,v1,v3): valid context triangle, CCW
  t2=(v0,v2,v4): valid context triangle, CCW
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me762",
    title="retriangulateVT_retriangulation_quality_check: new triangle t0=(v0,v1,v2) is exactly degenerate (collinear at y=0); quality check fires break (Branch 3)",
    defect_class="degenerate_triangle",
)

# Hub vertex on X-axis
v0 = m.vertex(1.0, 0.0, 0.0)   # 0 — hub vertex
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — left, collinear with v0/v2
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — right, collinear with v0/v1

# Non-degenerate context vertices above the X-axis
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — upper-left
v4 = m.vertex(2.0, 1.0, 0.0)   # 4 — upper-right

# t0 is exactly degenerate: v0, v1, v2 all at y=0, area=0.
# retriangulateVT quality check fires for this triangle → Branch 3 break.
t0 = m.triangle(v0, v1, v2)   # 0 — DEGENERATE (zero area)

# Context triangles above the axis — valid, give the hub a partial fan.
t1 = m.triangle(v0, v1, v3)   # 1 — left-upper sector
t2 = m.triangle(v0, v4, v2)   # 2 — right-upper sector (note order gives CCW)

# Degenerate triangle t0 has zero area.
m.assert_triangle_area_lt(t0, 1e-12)

# Shared edges in the fan.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t2
m.assert_edge_shared(v1, v2, 1)   # t0 base edge (degenerate triangle outer edge)

# Context triangle outer edges.
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v2, v4, 1)

# Euler: V=5, E=8 (7 edges as listed plus v3-v4 if connected, but here V=5, E=7, F=3).
# Count: vertices 5, edges: v0-v1, v0-v2, v1-v2, v0-v3, v1-v3, v0-v4, v2-v4 = 7
# chi = 5 - 7 + 3 = 1
m.assert_euler_characteristic(5, 7, 3, 1)
