"""Me230 — topTriangle_component_flood_fill: BFS marks both triangles in one component.

MeshFix `Basic_TMesh.topTriangle` Branch 1 (*component_flood_fill*) @ line 1697:
  '!IS_BIT(t1,2)' — triangle not yet visited in BFS; add to queue and mark BIT 2.

topTriangle walks a connected component by BFS over shared edges. For each
adjacent triangle not yet marked with BIT 2, Branch 1 fires: the triangle is
enqueued and BIT 2 is set. A mesh with exactly two triangles sharing one interior
edge exercises Branch 1 once: the seed triangle is processed first, then Branch 1
fires for its unvisited neighbor across the shared edge.

Geometry: two CCW triangles sharing edge (v1, v2):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)   — left triangle t0
  v3=(1.5,1,0)                              — right apex
  t0=(v0,v1,v2), t1=(v1,v3,v2)            — share edge (v1,v2)

The single interior edge (v1,v2) is shared by n=2 triangles. BFS from t0 visits
t1 via Branch 1. The mesh is a single connected component (one shell).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me230",
             title="topTriangle_component_flood_fill: BFS enqueues adjacent unvisited triangle",
             defect_class="topTriangle_component_flood_fill")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0 — BFS seed
t1 = m.triangle(v1, v3, v2)   # 1 — enqueued by Branch 1 via shared edge (v1,v2)

# One interior edge shared by exactly 2 triangles — the BFS link.
m.assert_edge_shared(v1, v2, 2)

# Four boundary edges confirm two-triangle open strip (one shell).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open surface with boundary).
m.assert_euler_characteristic(4, 5, 2, 1)
