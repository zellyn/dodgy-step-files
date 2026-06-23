"""Me232 — topTriangle_vertex_z_collection_v2: v2 collected into z-scan list.

MeshFix `Basic_TMesh.topTriangle` Branch 3 (*vertex_z_collection_v2*) @ line 1703:
  '!IS_VISITED(v2)' — v2 not yet marked; mark VISITED and append to vlist.

This is the second of three per-vertex collection branches fired during triangle
BFS. Branch 3 fires when v2 (the second vertex in MeshFix winding order) has not
been visited. With two triangles sharing one vertex but no edge, v2 of t0 is a
distinct unvisited vertex that must be added to the z-scan list by Branch 3.

Geometry: two triangles sharing vertex v1 (not an edge):
  v0=(0,0,0), v1=(1,0,0), v2=(0,0,2)   — t0: v2 is the apex, z=2
  v3=(2,0,0), v4=(1.5,0,1)             — t1 shares no edge with t0
  t0=(v0,v1,v2), t1=(v1,v3,v4)         — share only v1 (no shared edge → t1 unreachable from t0 by BFS)

Because there is no shared edge between t0 and t1, BFS from t0 never reaches t1.
Branch 3 fires when v2 of t0 is first seen: v2 is not yet VISITED, so it is
collected. This demonstrates that v2 (the second triangle vertex in the triple)
triggers Branch 3 independently of v1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me232",
             title="topTriangle_vertex_z_collection_v2: v2 appended to z-scan list (unvisited)",
             defect_class="topTriangle_vertex_z_collection_v2")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared vertex between t0 and t1
v2 = m.vertex(0.0, 0.0, 2.0)   # 2 — v2 in MeshFix triple; z=2, highest in t0
v3 = m.vertex(2.0, 0.0, 0.0)   # 3
v4 = m.vertex(1.5, 0.0, 1.0)   # 4

t0 = m.triangle(v0, v1, v2)   # 0 — Branch 3 fires for v2 here
t1 = m.triangle(v1, v3, v4)   # 1 — disconnected component (no shared edge with t0)

# All edges are boundary (n=1) — no interior edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# t1 is unreachable from t0 by edge-walking (no shared edge — only shared vertex v1).
m.assert_triangle_not_reachable_from(t1, t0)
