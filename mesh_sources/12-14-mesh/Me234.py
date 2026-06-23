"""Me234 — topTriangle_edge_collection_e1: e1 added to slope-candidate list.

MeshFix `Basic_TMesh.topTriangle` Branch 5 (*edge_collection_e1*) @ line 1706:
  '!IS_VISITED(t->e1)' — edge e1 of the current BFS triangle not yet marked;
  mark VISITED and append to elist for slope-scan.

After vertices are collected, topTriangle also collects each triangle's edges
into elist so the steepest-descending-edge search (Branches 7–8) has candidates.
Branch 5 fires when e1 (the first edge in the triangle's MeshFix data layout) is
not yet in elist. In a two-triangle mesh where both triangles share one edge,
Branch 5 fires at least once per triangle for e1.

Geometry: two triangles sharing edge (v1,v2) with v2 at z=2 (the highest vertex):
  v0=(0,0,0), v1=(2,0,0), v2=(1,0,2), v3=(3,0,2)
  t0=(v0,v1,v2), t1=(v1,v3,v2)

The highest vertex is v2 (z=2). Edges incident on v2 are (v0,v2), (v1,v2), and
(v2,v3). Branch 5 fires when e1 of t0 — which connects v0 to v1 — is first seen.
The boundary edge (v0,v2) from t0 and (v2,v3) from t1 are also candidates.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me234",
             title="topTriangle_edge_collection_e1: e1 appended to slope-candidate list (unvisited)",
             defect_class="topTriangle_edge_collection_e1")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 0.0, 2.0)   # 2 — highest z=2
v3 = m.vertex(3.0, 0.0, 2.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0 — e1=(v0,v1) triggers Branch 5
t1 = m.triangle(v1, v3, v2)   # 1 — neighbor via shared edge (v1,v2)

# Interior edge shared by both triangles.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# v2 is the highest vertex (z=2). Edge (v0,v2) from t0 and (v2,v3) from t1
# are incident on hv=v2 and will be checked in Branches 7–8.
m.assert_euler_characteristic(4, 5, 2, 1)
