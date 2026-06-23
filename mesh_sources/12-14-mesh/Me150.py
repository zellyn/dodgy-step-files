"""Me150 — flipNormals_triangle_invert_guard: single CW triangle is the flip seed.

MeshFix `Basic_TMesh.flipNormals` Branch 1 (*triangle_invert_guard*) @ line 1648:
  '!IS_BIT(t,6)' — the triangle's flip bit (bit 6) is not yet set.
  flipNormals starts with a seed triangle and inverts its orientation (swaps
  two vertices to reverse winding), then marks bit 6 to guard against
  re-processing. Branch 1 fires each time a triangle is dequeued whose bit 6
  is clear — i.e. the triangle has not yet been flipped.

Geometric signature: a single isolated CW triangle in the XY plane. Its normal
points in the -Z direction (inward for an XY-plane face). flipNormals processes
this one triangle through Branch 1: bit 6 is clear, so it inverts the winding.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  triangle: (v0, v2, v1) — CW ordering → normal = -Z

The CW winding (v0→v2→v1) gives:
  (v2-v0) × (v1-v0) = (0.5,1,0)×(1,0,0) = (0*0-0*0, 0*1-0.5*0, 0.5*0-1*1) = (0,0,-0.5)
  → normal z-component is negative.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me150",
             title="flipNormals_triangle_invert_guard: seed triangle has bit 6 clear, CW winding inverted",
             defect_class="inverted_normals")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# CW winding → normal = -Z; flipNormals Branch 1 fires on this triangle.
t0 = m.triangle(v0, v2, v1)

# Assert that the triangle has a downward (-Z) normal: confirms CW winding defect.
m.assert_triangle_normal_z_negative(t0)

# No shared edges (it's a lone triangle) — boundary edges each appear once.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v1, 1)
