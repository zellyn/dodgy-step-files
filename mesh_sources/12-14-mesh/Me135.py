"""Me135 — removeIfRedundant_double_flat_second_edge_removal: DoubleFlat vertex
has both e1 and e2 present; both are removed from the collapse candidate list.

MeshFix `Vertex.removeIfRedundant` Branch 6 (*double_flat_second_edge_removal*) @ line 363:
  'if (e2 != NULL) ve->removeNode(e2)'
  Immediately after Branch 5 removes e1, Branch 6 checks whether e2 is also
  non-NULL and removes it too. Both DoubleFlat boundary edges are excluded from
  the candidate set; only the remaining edges are eligible for collapse.

Geometric signature: vertex v2 is a DoubleFlat vertex with two symmetric ridge
neighbors — v_top above and v_bot below the axis. Both the edge (v2, v_top) =
e1 and edge (v2, v_bot) = e2 must be removed before the collapse candidate
selection at Branch 9. This fixture extends Me134 by introducing a second
symmetric ridge neighbor, so both e1 and e2 are non-NULL.

Geometry (z=0):
  v0=(0,0,0), v2=(2,0,0), v4=(4,0,0)  — collinear axis (DoubleFlat axis)
  v1=(1,1,0)  — upper ridge neighbor (e1 edge is v1-v2)
  v3=(1,-1,0) — lower ridge neighbor (e2 edge is v2-v3)
  v5=(3,1,0)  — upper right neighbor
  v6=(3,-1,0) — lower right neighbor

  Fan:
    t0 = (v0, v1, v2)
    t1 = (v0, v2, v3)
    t2 = (v2, v1, v5)
    t3 = (v2, v5, v4)
    t4 = (v2, v4, v6)
    t5 = (v3, v2, v6)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me135",
             title="removeIfRedundant_double_flat_second_edge_removal: DoubleFlat vertex with both e1 and e2 removed from candidate list",
             defect_class="redundant_vertex_double_flat_e1_e2_removal")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper left ridge
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — DoubleFlat vertex
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower left ridge
v4 = m.vertex(4.0, 0.0, 0.0)   # 4 — right axis point
v5 = m.vertex(3.0, 1.0, 0.0)   # 5 — upper right
v6 = m.vertex(3.0, -1.0, 0.0)  # 6 — lower right

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v2, v1, v5)    # 2
t3 = m.triangle(v2, v5, v4)    # 3
t4 = m.triangle(v2, v4, v6)    # 4
t5 = m.triangle(v3, v2, v6)    # 5

# v2 lies on the collinear axis v0-v4.
m.assert_vertex_on_edge(v2, v0, v4)

# Both ridge edges (e1 and e2) are interior.
m.assert_edge_shared(v1, v2, 2)   # e1 = (v1,v2): shared by t0 and t2
m.assert_edge_shared(v2, v3, 2)   # e2 = (v2,v3): shared by t1 and t5

# Axis edges at v2 are also interior.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v4, 2)   # shared by t3 and t4
