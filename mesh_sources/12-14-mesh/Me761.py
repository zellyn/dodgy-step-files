"""Me761 — retriangulateVT_hole_triangulation: vertex neighborhood gap filled by TriangulateHole using accumulated normal (Branch 2).

MeshFix `holeFilling::retriangulateVT` Branch 2 (*HOLE_TRIANGULATION*) @ line 404:
  'TriangulateHole(e0, &nor)'
  After accumulating the average normal for vertex v's fan, retriangulateVT
  calls TriangulateHole(e0, &nor) to fill the hole in v's vertex neighborhood.
  Branch 2 fires whenever the vertex's incident triangle fan has a boundary
  gap — a hole that TriangulateHole can patch by introducing new triangles.

Defect pattern: a ring of 4 triangles forming the *walls* around a triangular
  hole. The inner boundary loop [v0, v1, v2] is the unfilled hole that
  TriangulateHole fills. Vertex v3 is the hub; the three triangles t0, t1, t2
  form a partial fan such that the inner triangle (v0, v1, v2) is absent.
  TriangulateHole is invoked with e0 pointing at this hole's boundary and nor
  from the accumulated normals of t0, t1, t2.

Geometry: hub v3=(1,1,1) above, three inner ring vertices v0/v1/v2 below.
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,1,1)
  t0=(v3,v0,v1): left-bottom wall triangle (CCW, +Z-ish normal)
  t1=(v3,v1,v2): right wall triangle
  t2=(v3,v2,v0): top-left wall triangle
  The inner boundary loop [v0,v1,v2] is the unfilled triangular hole.
  All inner edges (v0-v1, v1-v2, v0-v2) are boundary edges (n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me761",
    title="retriangulateVT_hole_triangulation: 3-triangle wall fan around hub v3; inner hole [v0,v1,v2] filled by TriangulateHole(e0, &nor) (Branch 2)",
    defect_class="hole_in_hull",
)

# Inner boundary triangle (the hole that will be filled)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — inner ring SW
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — inner ring SE
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — inner ring top

# Hub vertex elevated above the inner ring
v3 = m.vertex(1.0, 1.0, 1.0)   # 3 — hub (retriangulateVT vertex)

# 3 wall triangles — each connects the hub v3 to one inner ring edge.
# Normal accumulation (Branch 1) precedes this fixture's Branch 2 call.
t0 = m.triangle(v3, v0, v1)   # 0 — bottom wall
t1 = m.triangle(v3, v1, v2)   # 1 — right wall
t2 = m.triangle(v3, v2, v0)   # 2 — left wall

# Hub spokes — each shared by exactly 2 wall triangles.
m.assert_edge_shared(v3, v0, 2)   # t0 and t2
m.assert_edge_shared(v3, v1, 2)   # t0 and t1
m.assert_edge_shared(v3, v2, 2)   # t1 and t2

# Inner ring edges — each incident on exactly 1 triangle (the hole boundary).
m.assert_edge_shared(v0, v1, 1)   # t0 inner edge
m.assert_edge_shared(v1, v2, 1)   # t1 inner edge
m.assert_edge_shared(v0, v2, 1)   # t2 inner edge

# The inner triangular hole boundary: TriangulateHole fills this.
# Each edge of [v0,v1,v2] is a boundary edge (n=1) — the loop is valid.
m.assert_hole_boundary([v0, v1, v2])

# Euler: V=4, E=6 (3 hub spokes + 3 inner rim), F=3, chi=1 (open disk — 3 walls).
m.assert_euler_characteristic(4, 6, 3, 1)
