"""Me651 — Basic_TMesh.removeEdges null_vertex_v1: e->v1 == NULL marks edge for removal (Branch 2).

MeshFix `Basic_TMesh.removeEdges` Branch 2 (*null_vertex_v1*) @ line 584:
  'if (e->v1 == NULL || e->v2 == NULL)' — during the edge-list traversal the
  function checks whether vertex pointer v1 on an edge is NULL. A NULL v1
  indicates an orphaned edge whose first endpoint has been unlinked (e.g. by
  a prior deserialization error or a half-completed topology operation). When
  v1 is NULL the edge is flagged for deletion.

Geometric proxy: the internal null-pointer state is modelled by a degenerate
  triangle whose v1 endpoint is coincident with v0 — the edge (v0, v1) has
  a zero-length span at v1, mimicking a vertex that has effectively ceased to
  exist. The coincident pair (v0, v1) both sit at (0, 0, 0); the triangle
  (v0, v1, v2) has zero area (two vertices coincide at the origin).

Geometry:
  v0 = (0, 0, 0)  — base vertex
  v1 = (0, 0, 0)  — coincident with v0 (proxy for null v1 pointer)
  v2 = (2, 1, 0)
  v3 = (1, 2, 0)
  t0 = (v0, v1, v2)   — degenerate (v0==v1); models orphaned-edge with null v1
  t1 = (v0, v2, v3)   — well-formed reference triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me651",
    title="removeEdges null_vertex_v1: degenerate edge with v1 coincident to v0 at (0,0,0); proxy for e->v1==NULL (Branch 2)",
    defect_class="orphaned_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base vertex
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — coincident with v0 (proxy for null v1)
v2 = m.vertex(2.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 2.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: v0==v1 collapses v1 endpoint
t1 = m.triangle(v0, v2, v3)    # 1 — well-formed reference triangle

# v0 and v1 are coincident: models the null-v1 orphaned-edge state.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# The degenerate triangle t0 has zero area (two coincident vertices).
m.assert_triangle_area_lt(t0, 1e-9)

# Edge (v0,v2) is shared by both triangles (n=2).
m.assert_edge_shared(v0, v2, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)   # collapsed edge — the proxy orphaned edge
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
