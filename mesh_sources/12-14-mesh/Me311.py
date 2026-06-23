"""Me311 — watsonInsert_cavity_vertex_v1: vertex v1 added to cavity boundary set.

MeshFix `holeFilling::watsonInsert` Branch 2 (*CAVITY_VERTEX_V1*) @ line 312:
  '!IS_BIT(v1, 5)' → 'bdr.appendHead(v1); MARK_BIT(v1, 5)'
  After a triangle is marked for cavity removal, each of its three vertices is
  checked. Branch 2 fires for v1 (the second vertex) when it has not yet been
  marked — it is added to the boundary vertex list and bit 5 is set.

Defect pattern: a 3-triangle fan around a hub vertex v3. When the Bowyer-Watson
  algorithm excavates the cavity for a new vertex, it walks adjacent marked
  triangles and collects boundary vertices. The 'v1' vertex of the first
  removed triangle is the first to be appended to 'bdr'.

Geometry: 3-triangle fan — hub v3 at centre, outer ring v0, v1, v2.
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,0.5,0) (centroid, the hub).

  t0=(v0,v1,v3), t1=(v1,v2,v3), t2=(v2,v0,v3)

  All 3 triangles share hub v3. If a new vertex is inserted into the
  circumsphere of t0, the cavity excavation reaches t0 and marks v1 (the
  second vertex of t0) as boundary vertex — Branch 2.

The boundary after cavity removal of t0 = outer triangle (v0,v1,v2) minus
  the hub, plus the two remaining fan triangles. The hole_boundary asserts
  the outer loop after the cavity is opened.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me311",
             title="watsonInsert_cavity_vertex_v1: v1 of removed triangle appended to cavity boundary (Branch 2)",
             defect_class="hole_in_hull")

# 3-triangle fan: hub v3, outer ring v0, v1, v2.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(1.0, 0.5, 0.0)   # 3 — hub vertex (centroid region)

t0 = m.triangle(v0, v1, v3)   # 0 — cavity triangle; v1 (index 1) → bdr
t1 = m.triangle(v1, v2, v3)   # 1
t2 = m.triangle(v2, v0, v3)   # 2

# Hub edges — each shared by exactly 2 triangles (fully manifold fan).
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Outer boundary edges — each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Outer loop: the 3 outer vertices form the boundary cycle that becomes
# visible when t0 is excavated (v1 = Branch 2, first bdr appendHead).
m.assert_hole_boundary([v0, v1, v2])
