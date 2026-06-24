"""Me383 — isDoubleFlat_edge_convexity_second: second non-coplanar edge found; nne increments to 2.

MeshFix `Vertex.isDoubleFlat` Branch 4 (*edge_convexity_second*) @ line 333:
  'else if (nne == 2) { e2 = e; }'  (equivalent: else { e2 = e; })
  When the 1-ring scan finds a second edge with non-zero convexity (after e1 was
  already set at Branch 2), it stores this second edge as e2 and increments nne to
  2. This fixture captures vertex v0 that has exactly two ridge edges in its 1-ring
  — a configuration that can lead to isDoubleFlat returning true (Branch 7) if the
  two ridges are collinear through v0.

Geometric signature: vertex v0 is a classic ridge vertex — it sits at the apex of
a "tent fold" with two ridge lines through it. The 1-ring has 4 triangles; two
share a flat z=0 half-plane and two share a raised z=1 half-plane. Exactly two
fan edges are ridges (at the flat/raised transitions): (v0,v1) and (v0,v3). After
the scan, nne==2, e1=(v0,v1), e2=(v0,v3).

Geometry:
  v0 = (0.0, 0.0, 0.5)   — ridge center vertex (raised)
  v1 = (-1.0, 0.0, 0.0)  — flat left
  v2 = (0.0, 1.0, 0.0)   — flat top
  v3 = (1.0, 0.0, 0.0)   — flat right
  v4 = (0.0, -1.0, 1.0)  — raised bottom

  t0 = (v1, v2, v0)   — upper-left triangle
  t1 = (v2, v3, v0)   — upper-right triangle
  t2 = (v3, v4, v0)   — lower-right triangle
  t3 = (v4, v1, v0)   — lower-left triangle

The four fan edges at v0 are all interior. Edges (v0,v1) and (v0,v3) are ridges
where the dihedral changes sharply between the flat and raised triangles.
The two ridge edges are found sequentially: first triggers Branch 2 (nne=1),
second triggers Branch 4 (nne=2), making e2 = second edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me383",
             title="isDoubleFlat_edge_convexity_second: v0 has exactly 2 ridge edges; second ridge triggers Branch 4 (e2 set, nne=2)",
             defect_class="double_flat_vertex_two_ridges")

v0 = m.vertex(0.0,  0.0,  0.5)   # 0 — ridge center vertex
v1 = m.vertex(-1.0, 0.0,  0.0)   # 1 — flat left
v2 = m.vertex(0.0,  1.0,  0.0)   # 2 — flat top
v3 = m.vertex(1.0,  0.0,  0.0)   # 3 — flat right
v4 = m.vertex(0.0, -1.0,  1.0)   # 4 — raised bottom

t0 = m.triangle(v1, v2, v0)    # 0 — upper-left
t1 = m.triangle(v2, v3, v0)    # 1 — upper-right
t2 = m.triangle(v3, v4, v0)    # 2 — lower-right
t3 = m.triangle(v4, v1, v0)    # 3 — lower-left

# All 4 fan edges at v0 are interior (shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t3 — first ridge (e1)
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2 — second ridge (e2)
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# The outer boundary edges are each incident on exactly 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)
