"""Me233 — topTriangle_vertex_z_collection_v3: v3 collected into z-scan list.

MeshFix `Basic_TMesh.topTriangle` Branch 4 (*vertex_z_collection_v3*) @ line 1704:
  '!IS_VISITED(v3)' — v3 (third vertex in the triangle triple) not yet marked;
  mark VISITED and append to vlist.

Branch 4 is the last of the three per-vertex collection checks. It fires when
v3, the third vertex of the current BFS triangle, has not yet been visited. In a
triangle fan around a central hub vertex, v3 of the second triangle in BFS order
is a fresh vertex that has not been collected yet; Branch 4 adds it to vlist.

Geometry: two triangles sharing edge (v0,v1), forming a fan:
  v0=(0,0,0) hub, v1=(1,0,0), v2=(0,1,0), v3=(0,0,2)
  t0=(v0,v1,v2): seed triangle; all three vertices collected by Branches 2,3,4.
  t1=(v0,v3,v1): second triangle via shared edge (v0,v1); v3 is new — Branch 4 fires.

When the BFS processes t1, v0 and v1 are already VISITED from t0. Only v3 (the
third vertex in MeshFix's triple) is unvisited, so Branch 4 fires for v3.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me233",
             title="topTriangle_vertex_z_collection_v3: v3 appended to z-scan list (unvisited)",
             defect_class="topTriangle_vertex_z_collection_v3")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub; shared by both triangles
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared edge endpoint
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — unique to t0
v3 = m.vertex(0.0, 0.0, 2.0)   # 3 — unique to t1; highest z; Branch 4 target

t0 = m.triangle(v0, v1, v2)   # 0 — seed
t1 = m.triangle(v0, v3, v1)   # 1 — neighbor via shared edge (v0,v1); v3 triggers Branch 4

# Shared interior edge (v0,v1) between t0 and t1.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# After scanning vlist, hv=v3 (z=2 is highest).
# Both triangles are reachable from t0 (same shell).
m.assert_euler_characteristic(4, 5, 2, 1)
