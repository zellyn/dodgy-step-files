"""Me132 — removeIfRedundant_degenerate_neighbor_triangle: an incident triangle
is exactly degenerate, blocking vertex removal.

MeshFix `Vertex.removeIfRedundant` Branch 3 (*degenerate_neighbor_triangle*) @ line 356:
  'if (t->isExactlyDegenerate())'
  During the neighborhood check (Branch 2 path), if any incident triangle is
  exactly degenerate the algorithm immediately returns false. The vertex cannot
  be declared redundant when its neighborhood contains a collapsed triangle.

Geometric signature: vertex v2 is an interior vertex of a strip. One of its
incident triangles, t1, has all three vertices collinear (zero area — exactly
degenerate). The presence of t1 causes Branch 3 to fire and block v2's removal.

Geometry (z = 0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,0)  ← v2 lies exactly on segment v0-v1
  v3=(1,1,0)

  t0 = (v0, v3, v2)   — healthy triangle, area=0.5
  t1 = (v0, v1, v2)   — degenerate: v0, v1, v2 are collinear on y=0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me132",
             title="removeIfRedundant_degenerate_neighbor_triangle: collinear incident triangle blocks vertex removal",
             defect_class="redundant_vertex_removal_degenerate_neighbor")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 0.0)   # 2 — lies on v0-v1 segment
v3 = m.vertex(1.0, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v3, v2)    # 0 — area = 0.5 (healthy)
t1 = m.triangle(v0, v1, v2)    # 1 — degenerate: collinear, area=0

# t1 is the degenerate neighbor that triggers Branch 3.
m.assert_triangle_area_lt(1, 1e-9)    # t1 is exactly degenerate (area=0)

# v2 lies exactly on edge (v0, v1).
m.assert_vertex_on_edge(v2, v0, v1)   # v2 at midpoint of v0-v1

# Confirm t0 is healthy (area > 0).
m.assert_triangle_area_lt(0, 1.0)     # area = 0.5 < 1.0
