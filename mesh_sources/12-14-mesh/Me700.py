"""Me700 — Basic_TMesh.bridgeBoundaries branch 1: same_edge_or_non_boundary.

MeshFix `Basic_TMesh.bridgeBoundaries` Branch 1 (*same_edge_or_non_boundary*) @ line 429:
  'if (gve == gwe || !gve->isOnBoundary()) return NULL;'
  — when the two input edges are the same object, or when gve is not a
  boundary edge (shared by two triangles rather than one), the bridge
  attempt is invalid and the function returns NULL immediately.

Defect pattern: two triangles sharing an interior edge. The shared edge
  is incident on 2 triangles, so isOnBoundary() returns false for it.
  A caller that mistakenly passes this interior edge as gve triggers the
  early-return guard in Branch 1.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,-2,0)
  t0=(v0,v1,v2), t1=(v0,v3,v1) sharing interior edge (v0,v1).
  The interior edge (v0,v1) is shared by 2 triangles — not a boundary edge.
  Boundary edges: (v1,v2), (v0,v2), (v0,v3), (v1,v3) each n=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me700",
    title="bridgeBoundaries same_edge_or_non_boundary: interior edge (v0,v1) shared by 2 triangles; isOnBoundary() false, bridge returns NULL (Branch 1)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared at both ends of the interior edge
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — upper apex
v3 = m.vertex(1.0, -2.0, 0.0)  # 3 — lower apex

# Two triangles sharing interior edge (v0, v1).
t0 = m.triangle(v0, v1, v2)  # 0: upper triangle
t1 = m.triangle(v0, v3, v1)  # 1: lower triangle

# Interior shared edge — n=2, not a boundary edge.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v1, v2, 1)  # t0 right
m.assert_edge_shared(v0, v2, 1)  # t0 left
m.assert_edge_shared(v0, v3, 1)  # t1 left
m.assert_edge_shared(v1, v3, 1)  # t1 right

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
