"""Me155 — flipNormals_edge_orientation_e2: e2 vertex endpoints swapped to match flipped triangle.

MeshFix `Basic_TMesh.flipNormals` Branch 6 (*edge_orientation_e2*) @ line 1658:
  '!IS_BIT(t->e2,6)' — after inverting the triangle's winding, edge e2 has
  not yet been reversed. flipNormals swaps e2's vertex pointers so the directed
  edge matches the new triangle orientation, then marks e2's bit 6.
  Branch 6 fires each time e2 needs its orientation corrected.

In the MeshFix half-edge model, e2 is the second directed edge of the triangle
(e.g. the edge from vertex 1 to vertex 2 in the original winding). After the
winding is inverted the direction of e2 must flip to keep the directed-edge
representation consistent with the new CCW order.

Geometric signature: a CW triangle whose e2 edge (the interior shared edge
connecting it to a neighbor) must be reversed. Two adjacent CW triangles
sharing an interior edge that corresponds to the e2 slot of the seed.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  t0=(v0, v2, v1)  — CW, normal -Z; e2 = directed edge v2→v1 (interior, shared with t1).
  t1=(v1, v2, v3)  — CW, normal -Z; shares edge (v1,v2) with t0.

The shared edge (v1,v2) is e2 of t0 in CW order v0→v2→v1; after inversion
to CCW v0→v1→v2 the direction of that edge must be reversed (Branch 6).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me155",
             title="flipNormals_edge_orientation_e2: e2 reversed when triangle winding is inverted",
             defect_class="inverted_normals")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

# t0: (v0, v2, v1) — CW → normal -Z.
# e2 in CW order = v2→v1; this edge (v1,v2) is shared with t1.
t0 = m.triangle(v0, v2, v1)

# t1: (v1, v2, v3) — CW → normal -Z.
# (v2-v1)×(v3-v1) = (0,1,0)×(-1,1,0) = (0*0-0*1, 0*(-1)-0*0, 0*1-1*(-1)) = (0,0,1)
# Wait — let's verify: (v2-v1)=(0,1,0), (v3-v1)=(-1,1,0).
# cross: (1*0-0*1, 0*(-1)-0*0, 0*1-1*(-1)) = (-0, 0, 1) → +Z.
# Need CW. Use (v1, v3, v2) instead.
# (v3-v1)×(v2-v1) = (-1,1,0)×(0,1,0) = (1*0-0*1, 0*0-(-1)*0, (-1)*1-1*0) = (0,0,-1) → -Z
t1 = m.triangle(v1, v3, v2)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared edge (v1,v2) is interior — both t0 and t1 incident on it.
m.assert_edge_shared(v1, v2, 2)
# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
