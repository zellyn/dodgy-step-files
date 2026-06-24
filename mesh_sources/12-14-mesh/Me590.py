"""Me590 — holeFilling_TriangulateHole_edge_not_on_boundary: input edge is interior; cannot fill hole (Branch 1).

MeshFix `holeFilling::TriangulateHole@L157` Branch 1 (*EDGE_NOT_ON_BOUNDARY*) @ line 159:
  '!e->isOnBoundary()' → return 0; cannot triangulate from an interior edge.
  TriangulateHole requires its seed edge to be a boundary edge (shared by exactly
  one triangle). When the seed edge is interior (shared by two triangles), the
  method returns immediately with failure.

Defect pattern: a fully closed triangulation — a tetrahedron unfolded flat —
  where every edge is shared by exactly two triangles. There is no boundary
  edge anywhere in the mesh. Any edge passed as seed to TriangulateHole will
  fail the isOnBoundary() check immediately → Branch 1 fires.

Geometry: 4 triangles covering a closed strip around 4 vertices.
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,2,0), v3=(1.5,0.8,0) (interior hub)
  t0=(v0,v1,v3), t1=(v1,v2,v3), t2=(v2,v0,v3), t3=(v0,v2,v1) — back face

  The 4-triangle mesh has all edges shared by exactly 2 triangles (closed
  surface), so no isOnBoundary() check can succeed → Branch 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me590",
    title="holeFilling_TriangulateHole_edge_not_on_boundary: closed mesh has no boundary edge; TriangulateHole seed fails isOnBoundary check (Branch 1)",
    defect_class="hole_in_hull",
)

# 4 vertices: outer triangle + interior hub.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 2.0, 0.0)   # 2
v3 = m.vertex(1.5, 0.8, 0.0)   # 3 — interior hub

# 3 forward fan triangles + 1 back-face triangle to close every edge.
t0 = m.triangle(v0, v1, v3)  # 0: lower-left fan
t1 = m.triangle(v1, v2, v3)  # 1: right fan
t2 = m.triangle(v2, v0, v3)  # 2: upper-left fan
t3 = m.triangle(v0, v2, v1)  # 3: back face (reverse of outer triangle) closes outer edges

# Every edge is shared by exactly 2 triangles — closed surface, no boundary.
# Outer edges (between outer triangle vertices) each appear in t0/t1/t2 AND t3.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)

# Hub edges each appear in two fan triangles.
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler: V=4, E=6, F=4, chi=2 (closed surface, sphere topology).
m.assert_euler_characteristic(4, 6, 4, 2)
