"""Me316 — watsonInsert_cavity_triangle_removal: triangles inside cavity unlinked (unlinkTriangleNoManifold).

MeshFix `holeFilling::watsonInsert` Branch 7 (*CAVITY_TRIANGLE_REMOVAL*) @ line 333:
  'unlinkTriangleNoManifold(t)' — foreach marked triangle in cavity, unlink it.
  After the Bowyer-Watson boundary list is built (Branches 2-4), the cavity
  triangles are removed by unlinkTriangleNoManifold. Branch 7 fires once per
  cavity triangle that is deleted.

Defect pattern: a central triangular hole surrounded by 6 triangles. The 6
  surrounding triangles form the 'pre-cavity' mesh state. When a vertex is
  inserted at the hole's centroid, all 6 surrounding triangles are inside its
  circumsphere and are marked for removal — Branch 7 fires 6 times, once per
  unlinkTriangleNoManifold call.

Geometry: outer hexagon (6 vertices) + inner triangle (3 vertices shared with
  alternating outer vertices) giving a 6-triangle ring with a triangular hole.

  Outer hexagon: v0-v5 at radius 2, inner triangle: v6=(0,0,0) hub.
  Actually simpler: a 6-triangle fan around hub v6 at (0,0,0).

  v0=(2,0,0), v1=(1,1.732,0), v2=(-1,1.732,0),
  v3=(-2,0,0), v4=(-1,-1.732,0), v5=(1,-1.732,0), v6=(0,0,0)

  6 triangles: t0=(v0,v1,v6), t1=(v1,v2,v6), t2=(v2,v3,v6),
               t3=(v3,v4,v6), t4=(v4,v5,v6), t5=(v5,v0,v6)

  All 6 triangles would be in the cavity of a newly inserted vertex near v6.
  After removal, the outer boundary loop (v0..v5) is the re-triangulation target.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me316",
             title="watsonInsert_cavity_triangle_removal: 6 cavity triangles unlinked by unlinkTriangleNoManifold (Branch 7)",
             defect_class="hole_in_hull")

# Hexagonal fan: outer 6 vertices + hub.
v0 = m.vertex( 2.0,   0.0,    0.0)   # 0
v1 = m.vertex( 1.0,   1.732,  0.0)   # 1
v2 = m.vertex(-1.0,   1.732,  0.0)   # 2
v3 = m.vertex(-2.0,   0.0,    0.0)   # 3
v4 = m.vertex(-1.0,  -1.732,  0.0)   # 4
v5 = m.vertex( 1.0,  -1.732,  0.0)   # 5
v6 = m.vertex( 0.0,   0.0,    0.0)   # 6 — hub; inserted vertex replaces this

# 6-triangle fan — all will be inside the circumsphere of the inserted point.
t0 = m.triangle(v0, v1, v6)   # 0
t1 = m.triangle(v1, v2, v6)   # 1
t2 = m.triangle(v2, v3, v6)   # 2
t3 = m.triangle(v3, v4, v6)   # 3
t4 = m.triangle(v4, v5, v6)   # 4
t5 = m.triangle(v5, v0, v6)   # 5

# Hub edges — each shared by exactly 2 triangles (full manifold fan).
m.assert_edge_shared(v0, v6, 2)
m.assert_edge_shared(v1, v6, 2)
m.assert_edge_shared(v2, v6, 2)
m.assert_edge_shared(v3, v6, 2)
m.assert_edge_shared(v4, v6, 2)
m.assert_edge_shared(v5, v6, 2)

# Outer boundary edges — each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v0, 1)

# After cavity removal of all 6 triangles, the hexagonal boundary loop
# becomes the hole boundary to re-triangulate.
m.assert_hole_boundary([v0, v1, v2, v3, v4, v5])

# Euler: V=7, E=12 (6 outer + 6 hub), F=6, chi=1 (open disk).
m.assert_euler_characteristic(7, 12, 6, 1)
