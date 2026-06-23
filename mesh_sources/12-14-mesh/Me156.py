"""Me156 — flipNormals_edge_orientation_e3: e3 vertex endpoints swapped to match flipped triangle.

MeshFix `Basic_TMesh.flipNormals` Branch 7 (*edge_orientation_e3*) @ line 1659:
  '!IS_BIT(t->e3,6)' — after inverting the triangle's winding, edge e3 has
  not yet been reversed. flipNormals swaps e3's vertex pointers so the directed
  edge matches the new triangle orientation, then marks e3's bit 6.
  Branch 7 fires each time e3 needs its orientation corrected.

In the MeshFix half-edge model, e3 is the third directed edge (closing the
triangle loop: vertex 2 back to vertex 0 in the original winding). After the
winding is inverted the direction of e3 must flip.

Geometric signature: two adjacent CW triangles where the shared edge corresponds
to the e3 slot of the seed triangle. e3 = the closing edge of the seed triangle
(from its last vertex back to its first vertex in CW order).

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
  t0=(v0, v2, v1)  — CW, normal -Z; e3 in CW order = v1→v0 (closing edge).
                     In a CW triangle (v0,v2,v1), e3 connects v1 back to v0.
                     The edge (v0,v1) is shared with t1 in the e3 slot.
  t1=(v1, v2, v3)  — CW, normal -Z; shares edge (v1,v2) with t0? No — (v0,v1).

Let me use:
  t0=(v0, v2, v1): e1=v0→v2, e2=v2→v1, e3=v1→v0.
  e3 = edge (v0,v1). Share it with t1.
  t1=(v1, v0, v3): e1=v1→v0 (= reverse of e3 of t0). CW?
    (v0-v1)×(v3-v1) = (-1,0,0)×(0.5,1,0) = (0*0-0*1, 0*0.5-(-1)*0, (-1)*1-0*0.5) = (0,0,-1) → -Z ✓
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me156",
             title="flipNormals_edge_orientation_e3: e3 reversed when triangle winding is inverted",
             defect_class="inverted_normals")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

# t0: (v0, v2, v1) — CW, normal -Z. e3 is the closing edge v1→v0, i.e. edge (v0,v1).
# (v2-v0)×(v1-v0) = (0.5,1,0)×(1,0,0) = (0,0,-0.5) → -Z ✓
t0 = m.triangle(v0, v2, v1)

# t1: (v1, v0, v3) — CW, normal -Z. Shares edge (v0,v1) as its e1 = v1→v0.
# (v0-v1)×(v3-v1) = (-1,0,0)×(0.5,1,0) = (0*0-0*1, 0*0.5-(-1)*0, (-1)*1-0*0.5)
#                 = (0, 0, -1) → -Z ✓
t1 = m.triangle(v1, v0, v3)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared edge (v0,v1): e3 of t0 and e1 of t1.
m.assert_edge_shared(v0, v1, 2)
# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
