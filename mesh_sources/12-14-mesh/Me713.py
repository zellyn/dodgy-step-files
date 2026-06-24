"""Me713 — Basic_TMesh.removeVertices branch 4: topology_invalidation.

MeshFix `Basic_TMesh.removeVertices` Branch 4 (*topology_invalidation*) @ line 619:
  'd_boundaries = d_handles = d_shells = 1;' — after the vertex-removal loop
  completes, the mesh marks its cached topology properties (boundary count,
  handle count, shell count) as dirty so they are recomputed on next access.
  This branch fires whenever at least one vertex was removed (the function
  returns non-zero).

Defect pattern: a closed tetrahedron (4 vertices, 4 triangles, 6 edges) plus
  one isolated vertex (v4 at (10,10,10)). After removeVertices processes the
  list, v4 is removed, the count is non-zero, and the dirty-flag assignment
  fires. The tetrahedron provides a well-defined topology; v4 is the trigger
  for the invalidation branch.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,√3/2,0)≈(0.5,0.866,0), v3=(0.5,√3/6,√6/3)≈(0.5,0.289,0.816).
  Four triangles forming a closed tetrahedron; each edge shared by 2 triangles.
  v4=(10,10,10) is isolated.
  Euler (closed): V=4, E=6, F=4, chi=2. Total vertices in fixture: 5.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me713",
    title="Basic_TMesh.removeVertices topology_invalidation: d_boundaries=d_handles=d_shells=1 after isolated v4 removed (Branch 4)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)           # 0
v1 = m.vertex(1.0, 0.0, 0.0)           # 1
v2 = m.vertex(0.5, 0.866, 0.0)         # 2 — apex in XY plane
v3 = m.vertex(0.5, 0.289, 0.816)       # 3 — apex above XY plane
v4 = m.vertex(10.0, 10.0, 10.0)        # 4 — isolated; triggers topology dirty

# Four faces of the tetrahedron.
t0 = m.triangle(v0, v1, v2)  # base front
t1 = m.triangle(v0, v1, v3)  # left face
t2 = m.triangle(v1, v2, v3)  # right face
t3 = m.triangle(v0, v2, v3)  # back face

# All six tetrahedron edges shared by exactly 2 triangles.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Isolated vertex — its removal triggers d_boundaries=d_handles=d_shells=1.
m.assert_isolated_vertex(v4)

# Euler for the closed tetrahedron (ignoring v4): V=4, E=6, F=4, chi=2.
m.assert_euler_characteristic(4, 6, 4, 2)
