"""Me136 — removeIfRedundant_opposite_vertex_coincidence: both DoubleFlat edges
e1 and e2 share the same opposite vertex, making collapse invalid.

MeshFix `Vertex.removeIfRedundant` Branch 7 (*opposite_vertex_coincidence*) @ line 364:
  'if (*e1->oppositeVertex(this) == *e2->oppositeVertex(this)) return false'
  After e1 and e2 are identified for the DoubleFlat vertex, the algorithm checks
  whether both edges have the *same* opposite vertex (the vertex on the far end
  of each ridge edge from the subject vertex). If they coincide, collapsing the
  subject vertex would merge the two triangles into a single degenerate element
  and Branch 7 rejects the removal.

Geometric signature: vertex v2 (DoubleFlat on the x-axis) has two ridge edges
e1=(v2,v1) and e2=(v2,v3). Normally v1 ≠ v3, but here they are placed at the
same 3D coordinates so that e1 and e2 share a coincident opposite vertex.
The duplicate vertex entry (v1 and v3 at the same position) triggers Branch 7.

Geometry (z=0):
  v0=(0,0,0)  — left axis point
  v1=(1,1,0)  — upper ridge (e1 opposite vertex)
  v2=(2,0,0)  — DoubleFlat vertex
  v3=(1,1,0)  — lower ridge (e2 opposite vertex — SAME POSITION as v1!)
  v4=(4,0,0)  — right axis point

  t0 = (v0, v1, v2)
  t1 = (v0, v2, v3)  — v3 at same coords as v1 → triangle t1 collapses onto t0

  Two additional triangles to close the fan:
  t2 = (v2, v1, v4)
  t3 = (v2, v4, v3)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me136",
             title="removeIfRedundant_opposite_vertex_coincidence: DoubleFlat e1 and e2 share coincident opposite vertex, collapse blocked",
             defect_class="redundant_vertex_removal_opposite_vertex_coincidence")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left axis
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper ridge
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — DoubleFlat subject vertex
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — coincident with v1 (same 3D coords!)
v4 = m.vertex(4.0, 0.0, 0.0)   # 4 — right axis

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1 — v3 at same position as v1
t2 = m.triangle(v2, v1, v4)    # 2
t3 = m.triangle(v2, v4, v3)    # 3

# v1 and v3 are at the same position — the coincident opposite vertices.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)

# v2 lies on the collinear axis v0-v4.
m.assert_vertex_on_edge(v2, v0, v4)

# Ridge edges e1=(v1,v2) and e2=(v2,v3) both interior.
m.assert_edge_shared(v1, v2, 2)   # t0 and t2
m.assert_edge_shared(v2, v3, 2)   # t1 and t3
