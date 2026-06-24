"""Me740 — TriangulateHole_L439_edge_not_on_boundary: closed mesh; all edges interior; !e->isOnBoundary() returns 0 (Branch 1).

MeshFix `holeFilling::TriangulateHole` Branch 1 (*EDGE_NOT_ON_BOUNDARY*) @ line 441:
  'if (!e->isOnBoundary()) return 0'
  TriangulateHole@L439 immediately returns 0 if the seed edge is not a boundary
  edge (i.e. it is an interior edge shared by exactly two triangles). The mesh
  must be topologically closed so that every edge has n==2.

Defect pattern: a closed tetrahedral mesh (4 faces, all edges shared by exactly
  2 triangles, no boundary). When the healer calls TriangulateHole(e, ...) with
  any one of these interior edges, Branch 1 fires: !e->isOnBoundary() is true
  and the function immediately returns 0.

Geometry (unit tetrahedron):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.866,0), v3=(0.5,0.289,0.816)
  Four faces: (v0,v1,v2), (v0,v1,v3), (v0,v2,v3), (v1,v2,v3)
  All 6 edges shared by exactly 2 triangles (n=2) — fully closed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me740",
    title="TriangulateHole_L439_edge_not_on_boundary: closed tetrahedral mesh; every edge interior (n=2); !e->isOnBoundary() fires; returns 0 (Branch 1)",
    defect_class="hole_in_hull",
)

# Unit tetrahedron vertices.
v0 = m.vertex(0.0, 0.0, 0.0)              # 0 — base front-left
v1 = m.vertex(1.0, 0.0, 0.0)              # 1 — base front-right
v2 = m.vertex(0.5, 0.866, 0.0)            # 2 — base back
v3 = m.vertex(0.5, 0.289, 0.816)          # 3 — apex

# Four faces of the closed tetrahedron (consistent outward normals).
t0 = m.triangle(v0, v2, v1)   # 0 — bottom face (normal down)
t1 = m.triangle(v0, v1, v3)   # 1 — front face
t2 = m.triangle(v1, v2, v3)   # 2 — right face
t3 = m.triangle(v0, v3, v2)   # 3 — left face

# All 6 edges are interior (n=2) — no boundary exists.
m.assert_edge_shared(v0, v1, 2)   # bottom+front
m.assert_edge_shared(v0, v2, 2)   # bottom+left
m.assert_edge_shared(v1, v2, 2)   # bottom+right
m.assert_edge_shared(v0, v3, 2)   # front+left
m.assert_edge_shared(v1, v3, 2)   # front+right
m.assert_edge_shared(v2, v3, 2)   # right+left

# Euler: V=4, E=6, F=4, chi=2 (closed orientable surface = sphere).
m.assert_euler_characteristic(4, 6, 4, 2)
