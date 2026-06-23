"""Me375 — isSelectionSimple_boundary_edge_count: vertex with nae>1 boundary edges, non-simple loop (Branch 6).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 6 (*boundary_edge_count*) @ line 1034:
  `if (nae > 1) break;` — while traversing the boundary loop of the
  selected region, the algorithm counts how many boundary edges each vertex
  has (`nae`). If a vertex has more than one incident boundary edge,
  the boundary loop is not a simple closed curve (the vertex is a
  "pinch point" where the loop self-touches). The inner traversal loop
  breaks out early.

The fixture models a "figure-8" or "bowtie" shaped selection: two
triangle patches that share exactly one vertex (no shared edge). The
shared vertex is a pinch point on the selection boundary — it appears in
the boundary with two incident boundary edges from each patch, so `nae == 2`
at that vertex → Branch 6 fires.

Geometry: two separate triangle patches that touch at a single pinch vertex v0:
  Patch A: t0=(v0,v1,v2) — lower triangle
  Patch B: t1=(v0,v3,v4) — upper triangle
  v0 is shared between both patches but no edge is shared.

At v0 the boundary has 4 edges: (v0,v1), (v0,v2), (v0,v3), (v0,v4).
The boundary traversal finds nae=2 (or more) at v0 → Branch 6 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me375",
    title="isSelectionSimple_boundary_edge_count: figure-8 selection with pinch vertex v0 (nae>1 at v0) → break (Branch 6)",
    defect_class="selection_non_simple_boundary",
)

# Pinch vertex shared by both patches.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0: pinch point

# Patch A — lower triangle.
v1 = m.vertex(-1.0, -1.0, 0.0)  # 1
v2 = m.vertex(1.0,  -1.0, 0.0)  # 2

# Patch B — upper triangle.
v3 = m.vertex(-1.0, 1.0, 0.0)  # 3
v4 = m.vertex(1.0,  1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)  # 0: lower triangle (Patch A)
t1 = m.triangle(v0, v3, v4)  # 1: upper triangle (Patch B)

# All edges are boundary (n=1): the two patches share only vertex v0,
# no shared edge — a non-manifold vertex (bowtie) at v0.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# v0 has a disconnected fan (bowtie): t0 and t1 share only v0, no edge.
m.assert_vertex_fan_disconnected(v0)

# t1 is not reachable from t0 by edge-walking.
m.assert_triangle_not_reachable_from(target=t1, source=t0)
