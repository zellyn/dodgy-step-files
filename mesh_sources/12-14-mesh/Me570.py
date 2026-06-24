"""Me570 — Basic_TMesh.invertSelection branch 1: seed_provided — t0 != NULL; component-local invert from seed.

MeshFix `Basic_TMesh.invertSelection` Branch 1 (*seed_provided*) @ line 744:
  'if (t0 != NULL)'
  — when a seed triangle t0 is provided, the function performs a BFS-based
  component-local selection toggle rather than a global invert. Branch 1 fires
  whenever a non-NULL seed is passed.

Defect pattern: a small connected strip of three triangles sharing edges, all
  initially unmarked. The seed triangle t0 (index 0) is provided; the algorithm
  walks BFS through shared edges and inverts the VISITED marks of all reachable
  triangles in t0's component.

Geometry (flat strip, XY plane):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)  — left triangle
  v3=(1.5,1,0)                            — right apex
  v4=(2,0,0)                              — far-right corner
  t0=(v0,v1,v2), t1=(v1,v3,v2), t2=(v1,v4,v3)
  t0-t1 share edge (v1,v2); t1-t2 share edge (v1,v3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me570",
    title="Basic_TMesh.invertSelection seed_provided: t0 != NULL; BFS component-local invert from seed triangle (Branch 1)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — center base
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — left apex
v3 = m.vertex(1.5, 1.0, 0.0)  # 3 — right apex
v4 = m.vertex(2.0, 0.0, 0.0)  # 4 — far-right base

# Three triangles forming a connected strip.
t0 = m.triangle(v0, v1, v2)  # 0: seed triangle — t0 != NULL triggers Branch 1
t1 = m.triangle(v1, v3, v2)  # 1: shares edge (v1,v2) with t0
t2 = m.triangle(v1, v4, v3)  # 2: shares edge (v1,v3) with t1

# Shared interior edges (n=2): BFS walks these to reach all component triangles.
m.assert_edge_shared(v1, v2, 2)  # t0-t1 shared edge
m.assert_edge_shared(v1, v3, 2)  # t1-t2 shared edge

# Boundary edges (n=1): each outer edge is unique.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# All three triangles are in one connected component: t2 is reachable from t0.
# (No assert_triangle_not_reachable_from — they ARE connected, confirming one component.)
m.assert_euler_characteristic(5, 7, 3, 1)
