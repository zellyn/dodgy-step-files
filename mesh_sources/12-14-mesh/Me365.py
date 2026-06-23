"""Me365 — remove_isolated_points_physical_erase: isolated tail segment erased from points container.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 6 (*physical_erase*) @ line 468:
  'points.erase(points.begin() + (points.size() - removed_points_n), points.end())' —
  after detection and counting, the function erases the tail segment of the points
  container that holds the swapped-out isolated vertices. This branch fires whenever
  removed_points_n > 0.

Defect pattern: a quad (two triangles sharing a diagonal) plus two isolated vertices
  v4 and v5 at the end of the vertex list. After the swap phase, v4 and v5 occupy
  the tail positions. The erase call removes exactly these two entries, leaving a
  4-vertex, 2-triangle soup.

Geometry: v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0) form the quad.
  v4=(8,8,0) and v5=(9,9,0) are orphans appended after the quad.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me365",
             title="remove_isolated_points_physical_erase: two orphan tail vertices erased from points container",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(8.0, 8.0, 0.0)   # isolated
v5 = m.vertex(9.0, 9.0, 0.0)   # isolated

t0 = m.triangle(v0, v1, v2)   # lower-right triangle
t1 = m.triangle(v0, v2, v3)   # upper-left triangle

# Both isolated vertices.
m.assert_isolated_vertex(v4)
m.assert_isolated_vertex(v5)

# Shared diagonal.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges (open quad).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
