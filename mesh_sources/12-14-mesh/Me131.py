"""Me131 — removeIfRedundant_check_neighborhood: neighborhood check enabled,
all incident triangles are non-degenerate.

MeshFix `Vertex.removeIfRedundant` Branch 2 (*check_neighborhood_flag*) @ line 352:
  'if (check_neighborhood)'
  When the neighborhood flag is set, the algorithm fetches the list of all
  triangles incident on the vertex via VT() and inspects each one for exact
  degeneracy before proceeding. This branch exercises the *healthy* path where
  no degenerate neighbor is found and removal proceeds past the check.

Geometric signature: vertex v3 is an interior vertex on a planar strip with
three incident triangles all having positive area. The neighborhood scan
at Branch 2 finds no degenerate triangle; the algorithm continues past this
guard and reaches the DoubleFlat/Flat evaluation at Branch 1.

Geometry (z = 0 plane):
  v0=(0,0,0), v1=(2,0,0), v2=(4,0,0)
  v3=(2,1,0)  — the subject vertex (interior, non-flat — will fail Branch 1)
  v4=(0,2,0)

  Fan around v3:
    t0 = (v0, v1, v3)
    t1 = (v1, v2, v3)
    t2 = (v4, v0, v3)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me131",
             title="removeIfRedundant_check_neighborhood: vertex with three healthy non-degenerate incident triangles",
             defect_class="redundant_vertex_removal_neighborhood_check")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(4.0, 0.0, 0.0)   # 2
v3 = m.vertex(2.0, 1.0, 0.0)   # 3 — subject vertex
v4 = m.vertex(0.0, 2.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v3)    # 0
t1 = m.triangle(v1, v2, v3)    # 1
t2 = m.triangle(v4, v0, v3)    # 2

# Confirm fan structure: v3 shares two interior edges and two boundary edges.
m.assert_edge_shared(v0, v3, 2)   # interior: shared by t0 and t2
m.assert_edge_shared(v1, v3, 2)   # interior: shared by t0 and t1
m.assert_edge_shared(v2, v3, 1)   # boundary: only t1
m.assert_edge_shared(v3, v4, 1)   # boundary: only t2

# Confirm all three triangles are non-degenerate: each has area > 0.
# Area of t0: base (v0,v1)=2, height from v3 to that edge=1, area=1.0 < 2.0.
# Area of t1: base (v1,v2)=2, height from v3=1, area=1.0 < 2.0.
# Area of t2: base (v4,v0)=sqrt(8)≈2.83, height from v3≈1.41, area≈2.0 < 4.0.
m.assert_triangle_area_lt(0, 2.0)    # area=1.0, non-degenerate
m.assert_triangle_area_lt(1, 2.0)    # area=1.0, non-degenerate
m.assert_triangle_area_lt(2, 4.0)    # area≈2.0, non-degenerate
