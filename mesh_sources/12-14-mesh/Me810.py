"""Me810 — StarTriangulateHole_edge_not_on_boundary: closed mesh where every edge
is interior; !e->isOnBoundary() fires; function returns 0.

MeshFix `Basic_TMesh.StarTriangulateHole` Branch 1 (*EDGE_NOT_ON_BOUNDARY*) @ line 48:
  if (!e->isOnBoundary()) return 0;
  The function is called with an edge that is shared by two triangles (n==2).
  Because no edge is a boundary edge, the early-exit guard fires immediately
  and the hole-fill is skipped.

Geometry: a tetrahedron (4 vertices, 4 triangles, 6 edges).  Every edge is
shared by exactly 2 triangles — no boundary edges exist.  StarTriangulateHole
called with any edge returns 0 without modifying the mesh.

  v0=(0,0,0)  v1=(1,0,0)  v2=(0.5,1,0)  v3=(0.5,0.33,1)
  t0=(v0,v1,v2)  t1=(v0,v1,v3)  t2=(v0,v2,v3)  t3=(v1,v2,v3)

Euler: V=4, E=6, F=4, chi=2 (closed surface of genus 0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me810",
    title="StarTriangulateHole_edge_not_on_boundary: closed tetrahedron; every edge n==2; returns 0 (Branch 1)",
    defect_class="star_triangulate_hole_edge_not_on_boundary",
)

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 1.0)

# Four faces of the tetrahedron — consistent winding (outward normals).
m.triangle(v0, v2, v1)  # 0 — bottom, CW from below
m.triangle(v0, v1, v3)  # 1 — front
m.triangle(v0, v3, v2)  # 2 — left
m.triangle(v1, v2, v3)  # 3 — right

# Every edge must be shared by exactly 2 triangles.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Closed orientable surface of genus 0: chi=2.
m.assert_euler_characteristic(v=4, e=6, f=4, chi=2)
