"""Me563 — loopSubdivision boundary_vs_interior_edge_split: mixed mesh with n=1 and n=2 edges.

Basic_TMesh.loopSubdivision Branch 4 (*boundary_vs_interior_edge_split*) @ line 125:
  'if(e->isOnBoundary()) { /* midpoint only */ } else { /* Loop weights, k neighbours */ }'
  — For each edge to be split, the algorithm checks whether it lies on the mesh
  boundary (n=1, incident to exactly one triangle). Boundary edges use a plain
  midpoint; interior edges (n=2) use the Loop subdivision weights based on the
  valence (k) of the vertex ring. Both cases fire in a mesh that has boundary
  edges and interior edges simultaneously.

Fixture: a 4-triangle strip with one open boundary edge and several interior edges.
  - Interior edges (n=2): split with Loop weights using 4 or 6 neighbour valence
  - Boundary edges (n=1): split with simple midpoint (no weight averaging)
  The mix guarantees both sub-branches of the boundary check are exercised.

Geometric signature:
  t0–t1 share an interior edge (n=2).
  t2–t3 share another interior edge (n=2).
  t1–t2 share an interior edge (n=2).
  All outer perimeter edges are boundary edges (n=1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me563",
    title="loopSubdivision boundary_vs_interior_edge_split: mix of n=1 boundary edges and n=2 interior edges; both branches of isOnBoundary() fire (Branch 4)",
    defect_class="loop_subdivision",
)

# Four-triangle strip: two rows of two triangles.
#   v0—v1—v3
#   |\ | /|
#   v2—v4—v5
v0 = m.vertex(0.0, 2.0, 0.0)  # 0 — top-left
v1 = m.vertex(1.0, 2.0, 0.0)  # 1 — top-middle
v2 = m.vertex(0.0, 0.0, 0.0)  # 2 — bottom-left
v3 = m.vertex(2.0, 2.0, 0.0)  # 3 — top-right
v4 = m.vertex(1.0, 0.0, 0.0)  # 4 — bottom-middle
v5 = m.vertex(2.0, 0.0, 0.0)  # 5 — bottom-right

# Two triangles in left cell.
t0 = m.triangle(v0, v1, v2)   # 0 — upper-left: edges (0,1),(1,2),(0,2)
t1 = m.triangle(v1, v4, v2)   # 1 — lower-left: edges (1,4),(2,4),(1,2) — shares (1,2) with t0

# Two triangles in right cell.
t2 = m.triangle(v1, v3, v4)   # 2 — upper-right: edges (1,3),(3,4),(1,4) — shares (1,4) with t1
t3 = m.triangle(v3, v5, v4)   # 3 — lower-right: edges (3,5),(4,5),(3,4) — shares (3,4) with t2

# Interior edges (n=2): shared between adjacent triangle pairs.
m.assert_edge_shared(v1, v2, 2)  # shared by t0 and t1
m.assert_edge_shared(v1, v4, 2)  # shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)  # shared by t2 and t3

# Boundary edges (n=1): all perimeter edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v1, v3, 1)

# Euler characteristic: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
