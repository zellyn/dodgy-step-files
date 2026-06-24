"""Me560 — loopSubdivision midpoint_vs_full_relaxation: fully interior vertex eligible for Loop relaxation.

Basic_TMesh.loopSubdivision Branch 1 (*midpoint_vs_full_relaxation*) @ line 106:
  'if(!loopRelaxOriginal) { /* skip relaxation */ } else { v->x = ...; v->y = ...; v->z = ...; }'
  — The loopRelaxOriginal flag controls whether original vertex positions are updated
  using Loop's weighted average of their neighbours or left at their current positions
  (midpoint-only mode). This branch fires when the mesh contains at least one fully
  interior vertex (connected to no boundary edges) whose Loop-relaxed position differs
  from its current position.

Fixture: an hourglass-shaped strip of 6 triangles around a central fully-interior vertex v6.
  v6 is shared by all 6 triangles and has no boundary edges, so it is a fully interior
  vertex eligible for Loop-scheme relaxation. v0–v5 form the boundary ring.

Geometric signature:
  v6 = (0.5, 0.5, 0) — central vertex; all edges (v6,vi) are interior (n≥2)
  v0–v5 = hexagonal ring of boundary vertices

  Interior edges (all incident on v6): n=2
  Boundary edges (v0-v1, v1-v2, etc.): n=1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me560",
    title="loopSubdivision midpoint_vs_full_relaxation: central vertex v6 is fully interior; eligible for Loop-scheme vertex relaxation (Branch 1)",
    defect_class="loop_subdivision",
)

# Hexagonal boundary ring around central interior vertex.
v0 = m.vertex(1.0,  0.0, 0.0)  # 0 — boundary ring
v1 = m.vertex(1.5,  0.866, 0.0)  # 1
v2 = m.vertex(1.0,  1.732, 0.0)  # 2
v3 = m.vertex(0.0,  1.732, 0.0)  # 3
v4 = m.vertex(-0.5, 0.866, 0.0)  # 4
v5 = m.vertex(0.0,  0.0, 0.0)   # 5
v6 = m.vertex(0.5,  0.866, 0.0)  # 6 — central interior vertex

# Six triangles all sharing v6.
t0 = m.triangle(v0, v1, v6)  # 0
t1 = m.triangle(v1, v2, v6)  # 1
t2 = m.triangle(v2, v3, v6)  # 2
t3 = m.triangle(v3, v4, v6)  # 3
t4 = m.triangle(v4, v5, v6)  # 4
t5 = m.triangle(v5, v0, v6)  # 5

# All spoke edges (vi, v6) are interior — shared by exactly 2 triangles.
m.assert_edge_shared(v0, v6, 2)
m.assert_edge_shared(v1, v6, 2)
m.assert_edge_shared(v2, v6, 2)
m.assert_edge_shared(v3, v6, 2)
m.assert_edge_shared(v4, v6, 2)
m.assert_edge_shared(v5, v6, 2)

# Boundary ring edges — n=1 (each is on the mesh boundary).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v0, 1)

# Euler characteristic: V=7, E=12 (6 boundary + 6 spokes), F=6, chi=1 (open disk).
m.assert_euler_characteristic(7, 12, 6, 1)
