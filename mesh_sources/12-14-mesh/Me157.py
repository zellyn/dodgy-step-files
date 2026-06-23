"""Me157 — flipNormals_flip_propagation_guard: second-pass guard fires on already-flipped triangles.

MeshFix `Basic_TMesh.flipNormals` Branch 8 (*flip_propagation_guard*) @ line 1669:
  'IS_BIT(t,6)' — in the second pass (cleanup/unmark phase), the triangle has
  its flip bit (bit 6) set, confirming it was processed in the first pass.
  This branch enqueues the already-flipped triangle's neighbors for the cleanup
  sweep. Branch 8 fires for each triangle that was successfully flipped in
  pass 1 and now needs its bit 6 cleared and neighbors examined in pass 2.

Geometric signature: a fully-inverted closed mesh. All triangles have CW winding
(bit 6 was set during the first-pass flip of each). In the second pass, flipNormals
iterates over all triangles, fires Branch 8 (IS_BIT(t,6)) for each, then enqueues
neighbors for bit-clearing.

We model a complete tetrahedron with all faces wound inward (CW). All four faces
have their flip bit set after pass 1; pass 2 (Branch 8) unmarks them all.

Geometry: CW tetrahedron (all faces wound so normals point inward).
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,0.5,1)
  CW faces: (v0,v2,v1), (v0,v3,v2), (v0,v1,v3), (v1,v2,v3)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me157",
             title="flipNormals_flip_propagation_guard: second-pass cleanup iterates already-flipped triangles",
             defect_class="inverted_normals")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, 0.5, 1.0)   # 3

# CW tetrahedron — all faces have inward normals (pass 1 would flip all four,
# setting bit 6 on each; pass 2 / Branch 8 then unmarks them).
# Face 0: base, CW → normal -Z.
t0 = m.triangle(v0, v2, v1)
# Face 1: CW → inward normal.
t1 = m.triangle(v0, v3, v2)
# Face 2: CW → inward normal.
t2 = m.triangle(v0, v1, v3)
# Face 3: CW → inward normal.
t3 = m.triangle(v1, v2, v3)

# Base face (XY plane) has -Z normal — confirms CW inward winding.
m.assert_triangle_normal_z_negative(t0)

# All interior edges of the tetrahedron are shared by exactly 2 faces.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)
