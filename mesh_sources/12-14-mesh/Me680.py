"""Me680 — holeFilling::TriangulateHole@L98 EDGE_NOT_ON_BOUNDARY: input edge is interior (n==2); return 0 immediately (Branch 1).

MeshFix `holeFilling::TriangulateHole@L98` Branch 1 (*EDGE_NOT_ON_BOUNDARY*) @ line 100:
  `if (!e->isOnBoundary()) return 0;`
  — the input edge e is not a boundary edge (it is shared by two triangles, n==2);
  TriangulateHole cannot fill a hole starting from an interior edge and returns 0.

A closed mesh (all edges n==2, no open boundary) exercises this branch: every edge is
interior, so any edge passed to TriangulateHole@L98 immediately returns 0.

Geometry — closed tetrahedron (minimal closed orientable surface):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,0.5,1)
  4 triangles, 6 edges — all edges shared by exactly 2 triangles.

Branch 1 fires because no boundary edge exists — isOnBoundary() is false for all edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me680",
    title="TriangulateHole@L98 EDGE_NOT_ON_BOUNDARY: closed tetrahedron; all edges n==2; no boundary edge; return 0 (Branch 1)",
    defect_class="hole_in_hull",
)

# Tetrahedron vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, 0.5, 1.0)   # 3 — apex

# Four faces of the tetrahedron (CCW winding from outside).
t0 = m.triangle(v0, v2, v1)    # 0 — bottom face
t1 = m.triangle(v0, v1, v3)    # 1 — front face
t2 = m.triangle(v1, v2, v3)    # 2 — right face
t3 = m.triangle(v0, v3, v2)    # 3 — left face

# All 6 edges are shared by exactly 2 triangles — no boundary edge exists.
m.assert_edge_shared(v0, v1, 2)  # bottom-front edge
m.assert_edge_shared(v0, v2, 2)  # bottom-left edge
m.assert_edge_shared(v1, v2, 2)  # bottom-right edge
m.assert_edge_shared(v0, v3, 2)  # apex-left edge
m.assert_edge_shared(v1, v3, 2)  # apex-front edge
m.assert_edge_shared(v2, v3, 2)  # apex-right edge

# Euler: V=4, E=6, F=4, chi=2 (closed genus-0 surface — sphere topology).
m.assert_euler_characteristic(4, 6, 4, 2)
