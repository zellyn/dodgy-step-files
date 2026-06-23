"""Me226 — eulerUpdate_boundary_loop_traversal: nextOnBoundary() walks multiple loops (Branch 7).

MeshFix `Basic_TMesh.eulerUpdate` Branch 7 (*boundary_loop_traversal*) @ line 1772:
  'IS_BIT(v, 5)', 'nextOnBoundary()' — vertex on boundary, not yet processed;
  traverse next boundary-connected vertex, count boundary loops.

After hasBoundary is set (Branch 6), eulerUpdate walks all vertices. For each
boundary vertex not yet visited (IS_BIT not set), it starts a new boundary-loop
traversal using nextOnBoundary(), marking each vertex visited and counting loops.
Two distinct boundary loops require Branch 7 to fire twice (once per loop seed).

Geometry: two disconnected triangulated disks, each with their own boundary loop.
  Disk A: triangle (v0,v1,v2) — boundary loop: v0-v1-v2
  Disk B: triangle (v3,v4,v5) — boundary loop: v3-v4-v5
  Total: 2 boundary loops, 2 shells.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me226",
             title="eulerUpdate_boundary_loop_traversal: two boundary loops require nextOnBoundary() twice",
             defect_class="open_boundary")

# Disk A: isolated triangle with its own boundary.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Disk B: isolated triangle far away with its own boundary.
v3 = m.vertex(5.0, 0.0, 0.0)   # 3
v4 = m.vertex(6.0, 0.0, 0.0)   # 4
v5 = m.vertex(5.5, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — Disk A
t1 = m.triangle(v3, v4, v5)   # 1 — Disk B

# Two shells: t1 unreachable from t0.
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# Boundary loop A: all edges of t0 are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Boundary loop B: all edges of t1 are boundary (n=1).
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# Each triangle is its own boundary loop.
m.assert_hole_boundary([v0, v1, v2])   # loop A
m.assert_hole_boundary([v3, v4, v5])   # loop B
