"""Me652 — Basic_TMesh.removeEdges null_vertex_v2: e->v2 == NULL marks edge for removal (Branch 3).

MeshFix `Basic_TMesh.removeEdges` Branch 3 (*null_vertex_v2*) @ line 584:
  'if (e->v1 == NULL || e->v2 == NULL)' — the OR-clause checks vertex pointer v2.
  A NULL v2 means the edge's second endpoint has been unlinked. This is the
  symmetric case to Branch 2: while Branch 2 fires on a null first endpoint,
  Branch 3 fires when only v2 is null and v1 is still valid. The edge is
  marked for deletion either way, but the two conditions are separately
  exercisable code-coverage targets.

Geometric proxy: the null v2 state is modelled by a degenerate triangle where
  v2 is coincident with v1 — the edge (v1, v2) has zero length, mimicking
  a second endpoint that has ceased to exist. v0 and v1 are well-separated;
  only v1 and v2 share the same coordinate.

Geometry:
  v0 = (0, 0, 0)
  v1 = (3, 0, 0)  — well-formed first endpoint
  v2 = (3, 0, 0)  — coincident with v1 (proxy for null v2 pointer)
  v3 = (1, 2, 0)
  t0 = (v0, v1, v2)   — degenerate (v1==v2); models orphaned-edge with null v2
  t1 = (v0, v1, v3)   — well-formed reference triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me652",
    title="removeEdges null_vertex_v2: degenerate edge with v2 coincident to v1 at (3,0,0); proxy for e->v2==NULL (Branch 3)",
    defect_class="orphaned_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — well-formed vertex
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — well-formed first endpoint
v2 = m.vertex(3.0, 0.0, 0.0)   # 2 — coincident with v1 (proxy for null v2)
v3 = m.vertex(1.0, 2.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: v1==v2 collapses v2 endpoint
t1 = m.triangle(v0, v1, v3)    # 1 — well-formed reference triangle

# v1 and v2 are coincident: models the null-v2 orphaned-edge state.
m.assert_vertex_pair_distance_lt(v1, v2, 1e-9)

# The degenerate triangle t0 has zero area (two coincident vertices).
m.assert_triangle_area_lt(t0, 1e-9)

# Edge (v0,v1) is shared by both triangles (n=2).
m.assert_edge_shared(v0, v1, 2)

# Boundary edges.
m.assert_edge_shared(v1, v2, 1)   # collapsed edge — the proxy orphaned edge
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)
