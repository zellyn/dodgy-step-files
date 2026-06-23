"""Me228 — eulerUpdate_topology_reset: d_boundaries=d_handles=d_shells=0 cleared (Branch 9).

MeshFix `Basic_TMesh.eulerUpdate` Branch 9 (*topology_reset*) @ line 1780:
  'd_boundaries = d_handles = d_shells = 0' — reset stale topology-dirty flags.

At the end of eulerUpdate, the dirty flags d_boundaries, d_handles, d_shells are
zeroed to indicate the cached topology counts are now fresh. This branch fires
unconditionally at the end of every eulerUpdate call. A mesh that has boundary
edges and multiple shells exercises the full eulerUpdate computation before the
flags are reset.

Geometry: two triangles connected end-to-end forming a strip (one shell, one
boundary loop). eulerUpdate counts n_shells=1, n_boundaries=1, n_handles=0, then
sets d_boundaries=d_handles=d_shells=0 (Branch 9). The geometry confirms
the precondition: interior edge plus four boundary edges.

  t0 = (v0, v1, v2)
  t1 = (v1, v3, v2)   shares (v1,v2) with t0 — interior edge
  Boundary loop: v0-v1-v3-v2-v0 (four boundary edges)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me228",
             title="eulerUpdate_topology_reset: d_boundaries=d_handles=d_shells=0 reset at end of eulerUpdate",
             defect_class="euler_update_topology_reset")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v1, v3, v2)   # 1

# One interior edge — part of a single connected shell.
m.assert_edge_shared(v1, v2, 2)

# Four boundary edges — one boundary loop.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# The boundary loop confirms n_boundaries=1 (precondition for reset branch).
m.assert_hole_boundary([v0, v1, v3, v2])
