"""Me154 — flipNormals_edge_orientation_e1: e1 vertex endpoints swapped to match flipped triangle.

MeshFix `Basic_TMesh.flipNormals` Branch 5 (*edge_orientation_e1*) @ line 1657:
  '!IS_BIT(t->e1,6)' — after inverting the triangle's winding, edge e1 has
  not yet been reversed. flipNormals swaps e1's vertex pointers (p_swap) so
  the directed edge matches the new triangle orientation, then marks e1's bit 6.
  Branch 5 fires each time e1 needs its orientation corrected.

In MeshFix, each triangle has three directed edges (e1, e2, e3). When the
triangle winding is inverted, the edge directions must also be reversed to keep
the half-edge structure consistent. Branch 5 specifically handles e1.

Geometric signature: two adjacent triangles that together span two edges needing
orientation repair. The seed triangle (CW) has e1 pointing in the wrong direction
relative to the flipped winding. A second triangle shares e1 and confirms it is
an interior edge.

Geometry (z=0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0)
  t0=(v0, v2, v1)  — CW, normal -Z; e1 is the edge v0→v2 (wrong direction
                     after flip; must be reversed to v2→v0).
  t1=(v0, v1, v3)  — also CW, normal -Z; shares edge (v0,v1) with t0.

The shared interior edge (v0,v1) = e2 of t0 also needs reversal (Branch 6),
but here we focus on e1 = (v0,v2) in t0, which is its own boundary edge
and flipped when the triangle winding is inverted.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me154",
             title="flipNormals_edge_orientation_e1: e1 reversed when triangle winding is inverted",
             defect_class="inverted_normals")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(2.0,  0.0, 0.0)   # 1
v2 = m.vertex(1.0,  1.0, 0.0)   # 2
v3 = m.vertex(1.0, -1.0, 0.0)   # 3

# t0: CW → normal -Z; e1 = directed edge from v0 to v2 (first edge of the triangle).
# After flipNormals inverts t0 to (v0,v1,v2), e1 direction must be reversed.
t0 = m.triangle(v0, v2, v1)

# t1: CW → normal -Z; shares edge (v0,v1) with t0.
t1 = m.triangle(v0, v1, v3)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared edge (v0,v1) is interior.
m.assert_edge_shared(v0, v1, 2)
# e1 of t0 = (v0,v2): boundary edge of t0 only.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
