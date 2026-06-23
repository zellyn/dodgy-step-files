"""Me101 — unlink_triangle_v2_boundary_non_manifold: v2 is on the boundary but
both its incident edges are non-boundary (shared by two triangles).

MeshFix `Basic_TMesh.unlinkTriangle` Branch 2 (*vertex_manifold_check_v2*):
mirrors Branch 1 but for the *second* vertex (v2) of the target triangle.
v2->isOnBoundary() returns true (its fan does not form a closed ring), yet
both edges incident on v2 in the target triangle are each shared with another
triangle, indicating a non-manifold singularity at v2.

Geometry (target triangle t0 = (v0, v1, v2)):
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,0)  — t0's three vertices
  v2 is the middle of a horizontal strip; its two t0-edges are (v1,v2)
  and (v0,v2), both shared with other triangles.
  The ring at v2 is open (missing closure), so v2 isOnBoundary.

  v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)  — upper row

  t0 = (v0, v1, v2)  ← target (v2 is third vertex)
  t1 = (v0, v4, v2)  — shares edge (v0,v2) with t0
  t2 = (v1, v2, v5)  — shares edge (v1,v2) with t0
  t3 = (v0, v3, v4)  — upper-left, keeps v0 connected
  t4 = (v4, v5, v2)  — closes upper link but leaves v2 boundary (open at v3,v5 gap)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me101",
             title="unlink_triangle_v2_boundary_non_manifold: v2 on boundary but both incident edges non-boundary",
             defect_class="unlink_vertex_manifold_v2")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 0.0)   # 2 — center: on boundary, both t0-edges non-boundary
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# Target triangle t0; v2 is the third vertex.
t0 = m.triangle(v0, v1, v2)   # 0 — target

# Triangles sharing t0's edges at v2.
t1 = m.triangle(v0, v4, v2)   # 1 — shares (v0,v2) with t0
t2 = m.triangle(v1, v2, v5)   # 2 — shares (v1,v2) with t0
t3 = m.triangle(v0, v3, v4)   # 3 — upper-left fill
t4 = m.triangle(v4, v5, v2)   # 4 — upper-middle, v2 link from v4 to v5

# Both t0 edges incident on v2 are non-boundary (interior).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t2

# t0's third edge (v0,v1) is on the boundary.
m.assert_edge_shared(v0, v1, 1)   # boundary

# v2's ring is open: gap between v3 and v5 (no edge v3↔v5 or v3↔v2 closing it).
m.assert_edge_shared(v3, v4, 1)   # boundary edge confirming open ring at v2
m.assert_edge_shared(v4, v5, 1)   # boundary edge confirming open ring at v2
