"""Me210 — cutAndStitch_duplicate_singular_edge: marked edge duplicated for stitching.

MeshFix `Basic_TMesh.cutAndStitch` Branch 1 (*DUPLICATE_SINGULAR_EDGE*) @ line 995:
  'if (e2 = T->duplicateEdge(e1)) MARK_BIT(e2, 5)'
  When a non-manifold edge e1 is marked with BIT 5, cutAndStitch duplicates
  it via duplicateEdge() to create a boundary-free copy e2. The duplicate e2
  is also marked with BIT 5 so subsequent collection (Branch 2) picks it up.

Defect pattern: edge (v0, v2) is shared by THREE triangles — a non-manifold
configuration. This triggers the IS_BIT(e1,5) path; cutAndStitch calls
duplicateEdge to create a second topological copy of the edge so each incident
triangle gets its own boundary edge after the cut.

Geometry: three triangles fan around edge (v0, v2).
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(0,0,1), v4=(-1,0,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v2,v4)
Edge (v0,v2) is shared by all three → non-manifold (n=3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me210",
             title="cutAndStitch_duplicate_singular_edge: BIT-5 edge duplicated before stitching",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 0.0, 1.0)   # 3
v4 = m.vertex(-1.0, 0.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v2, v4)   # 2 — third sharer: non-manifold

# Edge (v0,v2) is incident on 3 triangles — triggers IS_BIT(e1,5) + duplicateEdge.
m.assert_edge_shared(v0, v2, 3)

# Remaining edges are boundary (each on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v0, v4, 1)
