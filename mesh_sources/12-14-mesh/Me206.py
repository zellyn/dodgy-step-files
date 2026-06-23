"""Me206 — zip_vertex_replacement_in_edges: all edges incident to ov2 are updated to point to ov1.

MeshFix `Vertex.zip` Branch 7 (*vertex_replacement_in_edges*) @ line 576:
  'e->replaceVertex(ov2, ov1)'
  After confirming ov1 != ov2, zip iterates over all edges incident to ov2 and replaces
  the ov2 endpoint reference with ov1. This effectively redirects the mesh topology so
  ov2 is no longer referenced. Branch 7 covers this edge-by-edge replacement loop.

Defect pattern: a seam where ov2 is referenced by multiple edges that all need to be
redirected to ov1 after the merge. The fixture shows ov2 incident on multiple edges
(a multi-edge fan) so the replacement loop iterates more than once.

Geometry: two-patch open mesh where ov2 has two incident edges (a wider fan on Patch B).
  Patch A: t0=(v0,v1,v2) with (v0,v1) boundary; v2 is ov1 (merge target)
  Patch B: t1=(v3,v4,v5), t2=(v3,v5,v6) sharing vertex v3 (ov2)
  v2 ≈ v3 (near-coincident); zip replaces all references to v3 with v2.

Oracle confirms ov2=v3 is shared by multiple triangles (multi-edge fan), and that
ov1=v2 and ov2=v3 are near-coincident.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me206",
             title="zip_vertex_replacement_in_edges: ov2 incident on multiple edges; zip replaceVertex loop touches all of them",
             defect_class="zip_vertex_replacement_in_edges")

# Patch A: single triangle; v2 is ov1 (merge target)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — zip vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — be1 endpoint
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — ov1 (merge destination)

# Patch B: two-triangle fan at v3 (ov2); v3 ≈ v2
v3 = m.vertex(0.5, 1.0, 0.0)   # 3 — ov2 (merge source); same position as v2
v4 = m.vertex(1.5, 1.5, 0.0)   # 4 — fan neighbor 1
v5 = m.vertex(-0.5, 1.5, 0.0)  # 5 — fan neighbor 2

# Zip vertex duplicate
v6 = m.vertex(0.0, 0.0, 0.0)   # 6 — same position as v0; Patch B base

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v6, v3, v4)    # 1 — Patch B triangle 1; ov2=v3 incident edge (v3,v4)
t2 = m.triangle(v6, v5, v3)    # 2 — Patch B triangle 2; ov2=v3 incident edge (v5,v3)

# Boundary edges on Patch A
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)

# ov2 (v3) is shared by two triangles in Patch B → replaceVertex loops twice
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v5, v3, 1)
m.assert_edge_shared(v3, v6, 2)  # interior edge shared by t1 and t2

# Near-coincident: ov1 (v2) ≈ ov2 (v3) → zip merges them
m.assert_vertex_pair_distance_lt(v2, v3, 1e-9)
# Near-coincident: zip vertex duplicates
m.assert_vertex_pair_distance_lt(v0, v6, 1e-9)
