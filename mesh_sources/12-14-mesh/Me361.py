"""Me361 — remove_isolated_points_usage_scan: polygon iteration marks all referenced vertices visited.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 2 (*point_usage_scan*) @ line 420:
  'for(P_ID polygon_index=0; ...) { for(i=0; ...) { visited[polygon[i]] = true; } }' —
  the function iterates every polygon to build a visited[] bitset of referenced point
  indices. Only points not set in visited[] can be isolated.

Defect pattern: a mesh where all vertices are referenced by at least one triangle.
  The scan marks visited[0], visited[1], visited[2] for the single triangle (v0,v1,v2).
  No isolated vertices exist, so removed_points_n will be 0 at the end.
  This exercises the inner loop body: visited[] set for every polygon vertex.

Geometry: one valid triangle v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0).
  All vertices are referenced; no isolated vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me361",
             title="remove_isolated_points_usage_scan: all vertices referenced; visited[] fully populated by polygon scan",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

m.triangle(v0, v1, v2)

# All edges are boundary (open mesh, one triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# No isolated vertices: every vertex is referenced.
# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
