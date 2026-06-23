"""Me159 — flipNormals_edge_unmark_cleanup: edge flip bits cleared in second cleanup pass.

MeshFix `Basic_TMesh.flipNormals` Branch 10 (*edge_unmark_cleanup*) @ line 1677:
  'UNMARK_BIT(t->e1,6)' — in the second pass, after confirming the triangle
  was flipped (IS_BIT(t,6)), flipNormals unmarks bit 6 on all three edges
  (e1, e2, e3) of the current triangle. Branch 10 is the edge-level cleanup
  that mirrors the vertex-swap in pass 1 (Branches 5–7): pass 1 reverses and
  marks the edges; pass 2 unmarks them to leave the mesh in a consistent state.

Geometric signature: a closed strip of three CW triangles forming a triangle
patch. After pass 1 flips all three triangles and marks their edge-flip bits,
pass 2 fires Branch 10 to clear every edge bit. The fixture exposes all three
edge slots (e1, e2, e3) needing bit-clearing on a single triangle.

Geometry (z=0): three CW triangles sharing a common interior hub.
  hub=(0,0,0), v0=(1,0,0), v1=(0,1,0), v2=(-1,0.5,0)
  t0=(hub, v1, v0)  — CW, normal -Z
  t1=(hub, v2, v1)  — CW, normal -Z
  t2=(hub, v0, v2)  — CW, normal -Z

All edges from hub to rim are interior (n=2); rim edges are boundary (n=1).
After pass 1 each edge gets bit 6 set; Branch 10 clears bit 6 on each edge
in pass 2 so the mesh cleanup is complete.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me159",
             title="flipNormals_edge_unmark_cleanup: edge bit 6 cleared on all edges in second cleanup pass",
             defect_class="inverted_normals")

hub = m.vertex( 0.0,  0.0, 0.0)   # 0  — hub
v0  = m.vertex( 1.0,  0.0, 0.0)   # 1
v1  = m.vertex( 0.0,  1.0, 0.0)   # 2
v2  = m.vertex(-1.0,  0.5, 0.0)   # 3  — non-collinear with hub and v0

# t0: (hub, v1, v0) — CW → normal -Z.
# (v1-hub)×(v0-hub) = (0,1,0)×(1,0,0) = (1*0-0*0, 0*1-0*0, 0*0-1*1) = (0,0,-1) → -Z ✓
t0 = m.triangle(hub, v1, v0)

# t1: (hub, v2, v1) — CW → normal -Z.
# (v2-hub)×(v1-hub) = (-1,0.5,0)×(0,1,0) = (0.5*0-0*1, 0*0-(-1)*0, (-1)*1-0.5*0)
#                   = (0, 0, -1) → -Z ✓
t1 = m.triangle(hub, v2, v1)

# t2: (hub, v0, v2) — CW → normal -Z.
# (v0-hub)×(v2-hub) = (1,0,0)×(-1,0.5,0) = (0*0-0*0.5, 0*(-1)-1*0, 1*0.5-0*(-1))
#                   = (0, 0, 0.5) → +Z! That's CCW. Need CW: swap → (hub, v2, v0).
# (v2-hub)×(v0-hub) = (-1,0.5,0)×(1,0,0) = (0.5*0-0*0, 0*1-(-1)*0, (-1)*0-0.5*1)
#                   = (0, 0, -0.5) → -Z ✓
t2 = m.triangle(hub, v2, v0)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)
m.assert_triangle_normal_z_negative(t2)

# Hub spokes: each shared by exactly 2 triangles.
m.assert_edge_shared(hub, v0, 2)   # shared by t0 and t2
m.assert_edge_shared(hub, v1, 2)   # shared by t0 and t1
m.assert_edge_shared(hub, v2, 2)   # shared by t1 and t2

# Rim edges: boundary (incident on exactly 1 triangle each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
