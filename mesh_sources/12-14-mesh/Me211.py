"""Me211 — cutAndStitch_collect_singular_edges: BIT-5 edge appended to singular_edges list.

MeshFix `Basic_TMesh.cutAndStitch` Branch 2 (*COLLECT_SINGULAR_EDGES*) @ line 997:
  'singular_edges.appendHead(e1); UNMARK_BIT(e1, 5)'
  After duplication, both the original and duplicate edges carry BIT 5. The
  algorithm iterates all edges: if BIT 5 is set, append to singular_edges and
  clear the bit. This fixture targets the collection pass.

Defect pattern: a boundary edge exists that is a cut result — it is on the
boundary of the mesh (incident on exactly one triangle). In the cutAndStitch
flow, such an edge would be collected into singular_edges by this branch after
the edge marked BIT 5 is detected.

Geometry: a simple four-triangle ring with a single boundary edge gap that
simulates what the mesh looks like after duplicateEdge cuts it open.
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3)
  Plus two flanking triangles sharing v0–v1 to make some edges interior.
  v4=(0.5,-1,0)
  t2=(v0,v4,v1) — below t0, shares (v0,v1)
  t3=(v0,v3,v4) is dropped so (v0,v3) is a boundary singular edge.

Edge (v0,v3) appears on only t1 — boundary. It represents the singular edge
that would be appended to singular_edges by Branch 2 after a cut.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me211",
             title="cutAndStitch_collect_singular_edges: boundary edge collected into singular_edges list",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.5, -1.0, 0.0)  # 4 — below baseline

t0 = m.triangle(v0, v1, v2)   # 0 — upper-right
t1 = m.triangle(v0, v2, v3)   # 1 — upper-left
t2 = m.triangle(v0, v4, v1)   # 2 — below (shares v0-v1 with t0 → interior)

# Edge (v0,v1) is interior: shared by t0 and t2.
m.assert_edge_shared(v0, v1, 2)

# Edge (v0,v3) is boundary — singular_edges collection target (Branch 2).
m.assert_edge_shared(v0, v3, 1)

# Edge (v2,v3) is also boundary.
m.assert_edge_shared(v2, v3, 1)

# Edge (v1,v2) is boundary.
m.assert_edge_shared(v1, v2, 1)

# Edges from v4 are boundary.
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
