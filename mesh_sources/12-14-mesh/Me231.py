"""Me231 — topTriangle_vertex_z_collection_v1: v1 collected into z-scan list.

MeshFix `Basic_TMesh.topTriangle` Branch 2 (*vertex_z_collection_v1*) @ line 1702:
  '!IS_VISITED(v1)' — v1 not yet marked; mark VISITED and append to vlist for
  z-coordinate scan to find the highest vertex in the component.

For each triangle in the BFS queue topTriangle checks whether each of its three
vertices has been visited yet. Branch 2 fires when v1 (the first vertex of the
current triangle in MeshFix's vertex ordering) is unvisited. It marks v1 VISITED
and appends it to the z-scan list.

Geometry: single triangle with v1 as its highest-z vertex.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0,1)
  t0=(v0,v1,v2)

v2 has z=1 (highest), but v1 is added to vlist by Branch 2 when t0 is first
processed (v1 is the first vertex in the winding order). All three boundary edges
are n=1, confirming this is an isolated open triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me231",
             title="topTriangle_vertex_z_collection_v1: v1 appended to z-scan list (unvisited)",
             defect_class="topTriangle_vertex_z_collection_v1")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — v1 in MeshFix: first vertex to be collected
v2 = m.vertex(0.5, 0.0, 1.0)   # 2 — highest-z vertex (hv after scan)

t0 = m.triangle(v0, v1, v2)   # 0

# Single isolated triangle — all edges are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# The boundary loop is the triangle's own perimeter.
m.assert_hole_boundary([v0, v1, v2])

# v2 is the vertex with highest z (z=1); v1 (z=0) is added first to vlist by Branch 2.
# After Branch 6 scans vlist, hv=v2 (z=1 > 0).
m.assert_vertex_pair_distance_lt(v0, v1, 2.0)   # v0 and v1 are co-planar at z=0
