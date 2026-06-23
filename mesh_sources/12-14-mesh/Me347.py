"""Me347 — init_topology_invalidation: d_boundaries/d_handles/d_shells marked dirty at end of init.

MeshFix `Basic_TMesh.init` Branch 8 (*TOPOLOGY_INVALIDATION*) @ line 225:
  'd_boundaries = d_handles = d_shells = 1' — at the very end of init, all three
  topology-cache flags are set dirty. This forces lazy recomputation of boundary loops,
  handle counts, and shell counts the first time any of those values are queried after
  the clone is constructed. The defect class this surfaces: a mesh where all three
  topology properties are non-trivial (has boundaries, has handles, has multiple shells),
  so the invalidation is meaningful — all three caches must be recomputed.

Defect pattern: two separate disconnected triangle components (two shells) with an
  open boundary on one of them (non-trivial boundary) and a closed handle-1 torus ring
  would be overkill; instead we use 2 disconnected open triangles: both have boundaries,
  both are separate shells, and neither has handles (genus 0). This exercises all three
  dirty flags: d_boundaries (both have boundaries), d_shells (two separate shells),
  d_handles (evaluated as 0 for each shell).

Geometry: component A: v0,v1,v2 — triangle at origin.
           component B: v3,v4,v5 — triangle at x=10.
  No shared edges or vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me347",
             title="init_topology_invalidation: two disconnected open shells require d_boundaries/d_shells/d_handles recompute after init",
             defect_class="disconnected_components")

# Component A
v0 = m.vertex(0.0,  0.0, 0.0)
v1 = m.vertex(1.0,  0.0, 0.0)
v2 = m.vertex(0.5,  1.0, 0.0)

# Component B — fully disconnected at x=10
v3 = m.vertex(10.0, 0.0, 0.0)
v4 = m.vertex(11.0, 0.0, 0.0)
v5 = m.vertex(10.5, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # 0: component A
t1 = m.triangle(v3, v4, v5)   # 1: component B

# Component A — all boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Component B — all boundary edges.
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# Two disconnected shells: t1 is not reachable from t0.
m.assert_triangle_not_reachable_from(target=1, source=0)

# Euler: V=6, E=6, F=2, chi=2 (two disjoint open disks: chi=1 each).
m.assert_euler_characteristic(6, 6, 2, 2)
