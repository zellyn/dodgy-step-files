"""Me153 — flipNormals_neighbor_enqueue_t3: t3 neighbor enqueued during winding propagation.

MeshFix `Basic_TMesh.flipNormals` Branch 4 (*neighbor_enqueue_t3*) @ line 1654:
  't3 != NULL && !IS_BIT(t3,6)' — after flipping the seed triangle, its t3
  neighbor exists and has not yet been flipped. flipNormals enqueues t3 for
  propagation. Branch 4 fires specifically for the t3 adjacency slot.

In MeshFix, t3 is the triangle adjacent across edge e3 (opposite vertex 1).
We model a scenario where the seed triangle and the neighbor across edge e3 are
both CW; all three neighbor slots (t1, t2, t3) exist but this fixture emphasizes
the t3-slot neighbor.

Geometry (z=0): four-spoke hub. All four CW triangles are wound inward.
  v0=(0,0,0) [hub], v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0)
  t0=(v0, v2, v1)   — CW, normal -Z (seed)
  t1=(v0, v3, v2)   — CW (neighbor across e2 of t0 — v0-v2 edge)
  t2=(v0, v4, v3)   — CW (neighbor across e3 of t1)
  t3=(v0, v1, v4)   — CW (neighbor across e3 of t0 — v0-v1 edge)

t3 in the t3 adjacency slot of t0 corresponds to the triangle across edge e3
(v0-v1). t3=(v0,v1,v4) is CW; flipNormals Branch 4 fires to enqueue it.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me153",
             title="flipNormals_neighbor_enqueue_t3: t3 neighbor CW, all four-spoke fan triangles inverted",
             defect_class="inverted_normals")

hub = m.vertex( 0.0,  0.0, 0.0)   # 0  — hub vertex
v1  = m.vertex( 1.0,  0.0, 0.0)   # 1
v2  = m.vertex( 0.0,  1.0, 0.0)   # 2
v3  = m.vertex(-1.0,  0.0, 0.0)   # 3
v4  = m.vertex( 0.0, -1.0, 0.0)   # 4

# All four triangles are CW (normal -Z) — flipNormals must propagate through
# all three neighbor slots including t3.

# t0: (hub, v2, v1) — CW → normal -Z.
# (v2-hub)×(v1-hub) = (0,1,0)×(1,0,0) = (0,0,-1) → -Z
t0 = m.triangle(hub, v2, v1)

# t1: (hub, v3, v2) — CW → normal -Z.
t1 = m.triangle(hub, v3, v2)

# t2: (hub, v4, v3) — CW → normal -Z.
t2 = m.triangle(hub, v4, v3)

# t3: (hub, v1, v4) — CW → -Z. This is the t3-slot neighbor of t0 across edge (hub,v1).
# (v1-hub)×(v4-hub) = (1,0,0)×(0,-1,0) = (0,0,-1) → -Z
t3 = m.triangle(hub, v1, v4)

# All four normals are -Z (CW).
m.assert_triangle_normal_z_negative(t0)
m.assert_triangle_normal_z_negative(t1)
m.assert_triangle_normal_z_negative(t2)
m.assert_triangle_normal_z_negative(t3)

# Interior spoke edges (each shared by 2 triangles).
m.assert_edge_shared(hub, v1, 2)   # shared by t0 and t3
m.assert_edge_shared(hub, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(hub, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(hub, v4, 2)   # shared by t2 and t3

# Boundary rim edges appear once.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)
