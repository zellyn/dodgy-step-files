"""Me152 — flipNormals_neighbor_enqueue_t2: t2 neighbor enqueued during winding propagation.

MeshFix `Basic_TMesh.flipNormals` Branch 3 (*neighbor_enqueue_t2*) @ line 1653:
  't2 != NULL && !IS_BIT(t2,6)' — after flipping the seed triangle, its t2
  neighbor exists and has not yet been flipped. flipNormals enqueues t2 for
  propagation. Branch 3 fires specifically for the t2 adjacency slot.

In MeshFix, t2 is the triangle adjacent across edge e2 (opposite vertex 0).
We model a scenario where a seed triangle (CW) shares its e2-side edge with
an unflipped CW neighbor in the t2 slot.

Geometry (z=0):
  Three triangles in a fan around v0; the seed and one neighbor across the e2
  edge are both CW.

  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0)
  t0=(v0, v2, v1)   — CW, normal -Z (seed)
  t1=(v0, v3, v2)   — CW, normal -Z (t2 neighbor, across edge v0-v2)

The t2 slot of t0 corresponds to the triangle across the edge v0-v2 (edge e2,
opposite the first vertex of t0). t1 is that neighbor, also CW; flipNormals
fires Branch 3 to enqueue t1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me152",
             title="flipNormals_neighbor_enqueue_t2: t2 neighbor CW, enqueued for flip propagation",
             defect_class="inverted_normals")

v0 = m.vertex( 0.0, 0.0, 0.0)   # 0  — hub
v1 = m.vertex( 1.0, 0.0, 0.0)   # 1
v2 = m.vertex( 0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3

# t0: (v0, v2, v1) — CW → normal -Z.
# (v2-v0)×(v1-v0) = (0,1,0)×(1,0,0) = (0*0-0*0, 0*1-0*0, 0*0-1*1) = (0,0,-1) → -Z
t0 = m.triangle(v0, v2, v1)

# t1: (v0, v3, v2) — CW → normal -Z.
# (v3-v0)×(v2-v0) = (-1,0,0)×(0,1,0) = (0*0-0*1, 0*0-(-1)*0, (-1)*1-0*0) = (0,0,-1) → -Z
t1 = m.triangle(v0, v3, v2)

m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)

# Shared edge (v0,v2) is interior — both t0 and t1 incident on it.
m.assert_edge_shared(v0, v2, 2)
# Boundary edges appear once.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)
