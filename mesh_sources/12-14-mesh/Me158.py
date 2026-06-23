"""Me158 — flipNormals_neighbor_unmark_t1: t1 neighbor's flip bit cleared in cleanup pass.

MeshFix `Basic_TMesh.flipNormals` Branch 9 (*neighbor_unmark_t1*) @ line 1673:
  'IS_BIT(t1,6)' — in the second pass (cleanup), the t1 neighbor of the current
  triangle also has bit 6 set (was flipped in pass 1). flipNormals unmarks t1
  and enqueues it so its own neighbors can be cleaned up. Branch 9 fires
  specifically for the t1 adjacency during the unmark sweep.

This branch is the cleanup-pass analog of Branch 2: while Branch 2 enqueued
a non-flipped t1 neighbor for flipping, Branch 9 enqueues an already-flipped
t1 neighbor for bit-clearing.

Geometric signature: two adjacent CW triangles sharing edge via t1. After pass 1
flips both (bit 6 set on both), pass 2 iterates the seed triangle (Branch 8),
finds t1 still has bit 6 set (Branch 9), and unmarks it.

Geometry (z=0): two adjacent CW triangles sharing edge (v0,v1).
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
  t0=(v0, v2, v1)  — CW, normal -Z (seed; after pass 1 both bits set)
  t1=(v0, v1, v3)  — CW, normal -Z (t1-slot neighbor; Branch 9 unmarks it in pass 2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me158",
             title="flipNormals_neighbor_unmark_t1: t1 flip-bit cleared in cleanup pass",
             defect_class="inverted_normals")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(1.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.5,  1.0, 0.0)   # 2
v3 = m.vertex(0.5, -1.0, 0.0)   # 3

# t0: CW → normal -Z.  (v2-v0)×(v1-v0) = (0.5,1,0)×(1,0,0) = (0,0,-0.5) → -Z
t0 = m.triangle(v0, v2, v1)

# t1: CW → normal -Z.  (v1-v0)×(v3-v0) = (1,0,0)×(0.5,-1,0) = (0,0,-1) → -Z
t1 = m.triangle(v0, v1, v3)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared interior edge (v0,v1) — t1-slot adjacency of t0.
m.assert_edge_shared(v0, v1, 2)
# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
