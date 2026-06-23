"""Me134 — removeIfRedundant_double_flat_edge_removal: DoubleFlat vertex has e1
present and removes it from the candidate edge list.

MeshFix `Vertex.removeIfRedundant` Branch 5 (*double_flat_edge_removal*) @ line 362:
  'if (e1 != NULL) ve->removeNode(e1)'
  For a DoubleFlat vertex, two special edges e1 and e2 are identified during the
  Flat/DoubleFlat classification. Branch 5 fires when e1 != NULL and removes it
  from the incident edge list 've' so it won't be considered as a collapse
  candidate (those edges are handled separately).

Geometric signature: vertex v2 is exactly collinear with its two neighbors v0 and
v4 in the x-direction. The two triangles on one side of v2 form a "double-flat"
configuration where v2 is sandwiched between two coplanar triangle fans meeting
at a shared ridge. e1 is the edge from v2 toward the ridge neighbor v1.

Geometry (z=0, all on same plane):
  v0=(0,0,0), v1=(1,1,0), v2=(2,0,0), v3=(1,-1,0), v4=(4,0,0)

  Fan around v2 (the DoubleFlat vertex at x=2 on the x-axis):
    t0 = (v0, v1, v2)   — upper left
    t1 = (v0, v2, v3)   — lower left
    t2 = (v2, v1, v4)   — upper right
    t3 = (v2, v4, v3)   — lower right

  v0-v2-v4 are collinear (all on y=0) → v2 is a DoubleFlat vertex.
  e1 = edge (v1, v2): the upper shared edge on the left side of the axis.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me134",
             title="removeIfRedundant_double_flat_edge_removal: DoubleFlat vertex v2 with e1=(v1,v2) removed from collapse candidates",
             defect_class="redundant_vertex_double_flat_e1_removal")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left neighbor on axis
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper neighbor
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — DoubleFlat vertex (collinear on y=0)
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower neighbor
v4 = m.vertex(4.0, 0.0, 0.0)   # 4 — right neighbor on axis

t0 = m.triangle(v0, v1, v2)    # 0 — upper left
t1 = m.triangle(v0, v2, v3)    # 1 — lower left (corrected winding)
t2 = m.triangle(v2, v1, v4)    # 2 — upper right
t3 = m.triangle(v2, v4, v3)    # 3 — lower right

# v0-v2-v4 are collinear on y=0: v2 lies on the line v0-v4.
m.assert_vertex_on_edge(v2, v0, v4)

# All four fan edges at v2 are interior.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t2 — this is e1
m.assert_edge_shared(v2, v3, 2)   # shared by t1 and t3
m.assert_edge_shared(v2, v4, 2)   # shared by t2 and t3
