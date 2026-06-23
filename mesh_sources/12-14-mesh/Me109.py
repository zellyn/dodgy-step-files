"""Me109 — unlink_triangle_v2_manifold_duplication: v2 is non-manifold and must
be duplicated before the triangle is unlinked.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 12 (*manifold_duplication_v2*):
'if (v2nm)' — v2 was flagged as non-manifold at Branch 2 (boundary but both
incident edges in t0 are non-boundary). Branch 12 clones v2, redirects its
incident edges in one fan group to the duplicate, then proceeds with the unlink.

Geometric signature: v2 is a bowtie vertex — its triangle fan has two disjoint
connected components. One component contains the target triangle (t0). Unlinking
t0 is the action that triggers the v2 duplication so the two fans become clean
manifold vertices.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,0) [second vertex of t0, bowtie center]
  v3=(1,1,0)  — upper apex for first fan
  v4=(-1,-1,0), v5=(3,-1,0)  — lower fan vertices

  Upper fan (contains target):
    t0 = (v0, v2, v1)   ← target; v2 is second vertex
    t1 = (v0, v3, v2)   — shares (v0,v2) with t0
    t2 = (v2, v3, v1)   — shares (v1,v2) with t0

  Lower fan (disconnected from upper):
    t3 = (v2, v4, v5)   — shares only v2 with upper fan

  v2's fan: upper component {t0,t1,t2} and lower {t3} → bowtie.
  Edges (v0,v2) and (v1,v2) in t0 are interior → Branch 2 condition met.
  Branch 12 fires on v2nm.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me109",
             title="unlink_triangle_v2_manifold_duplication: v2 is non-manifold bowtie requiring duplication on unlink",
             defect_class="unlink_manifold_duplication_v2")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(2.0, 0.0, 0.0)    # 1
v2 = m.vertex(1.0, 0.0, 0.0)    # 2 — bowtie center = v2 in target
v3 = m.vertex(1.0, 1.0, 0.0)    # 3 — upper apex
v4 = m.vertex(-1.0, -1.0, 0.0)  # 4 — lower fan left
v5 = m.vertex(3.0, -1.0, 0.0)   # 5 — lower fan right

# Target triangle: v2 is the second vertex.
t0 = m.triangle(v0, v2, v1)     # 0 — target

# Upper fan (shares edges at v2 with t0).
t1 = m.triangle(v0, v3, v2)     # 1 — shares (v0,v2) with t0
t2 = m.triangle(v2, v3, v1)     # 2 — shares (v1,v2) with t0

# Lower fan — disconnected from upper, connected only through v2.
t3 = m.triangle(v2, v4, v5)     # 3

# Both edges of t0 at v2 are interior (non-boundary) → Branch 2 / Branch 12 condition.
m.assert_edge_shared(v0, v2, 2)   # interior: shared by t0 and t1
m.assert_edge_shared(v1, v2, 2)   # interior: shared by t0 and t2

# t0's third edge (v0,v1) is a boundary edge.
m.assert_edge_shared(v0, v1, 1)   # boundary

# Upper fan outer boundary edges.
m.assert_edge_shared(v0, v3, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary

# Lower fan boundary edges.
m.assert_edge_shared(v2, v4, 1)   # boundary in lower fan
m.assert_edge_shared(v2, v5, 1)   # boundary in lower fan

# v2's fan is disconnected (bowtie) — the core non-manifold condition.
m.assert_vertex_fan_disconnected(v2)
