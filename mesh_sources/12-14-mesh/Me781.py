"""Me781 — polygon_soup_to_polygon_mesh point_to_vertex_output_iterator: consistently wound soup; point→vertex index map recorded (Branch 2).

CGAL PMP `PMP.polygon_soup_to_polygon_mesh` Branch 2 (*point_to_vertex_output_iterator*) @ line 305:
  'if(point_to_vertex_output_iterator != boost::none) { ... }'
  — after a consistently oriented soup is successfully converted to a polygon
  mesh, if the caller supplies a point_to_vertex_output_iterator, the algorithm
  records a map from each soup point index to the vertex descriptor it was
  assigned in the output mesh. This branch fires for any clean soup where the
  caller requests the point→vertex correspondence.

Defect pattern (input pattern): a minimal consistently wound polygon soup
  (three vertices, two triangles sharing an interior edge) that is already
  valid for direct conversion. No orientation repair is needed. The Branch 2
  path fires because a point_to_vertex_output_iterator is provided — the map
  records p0→v0, p1→v1, p2→v2, p3→v3 after conversion.

Geometry (XY plane):
  p0=(0,0,0), p1=(2,0,0), p2=(1,1,0), p3=(2,1,0)
  t0=(p0,p1,p2): CCW, normal +Z
  t1=(p1,p3,p2): CCW, normal +Z
  Shared interior edge: (p1,p2).
  Both triangles consistently wound; soup orientation is valid.

Assertions:
  - Shared interior edge (p1,p2) n=2 (manifold interior edge).
  - Boundary edges each n=1 (open-disk topology).
  - euler_characteristic V=4, E=5, F=2, chi=1 confirms valid open-disk mesh
    that conversion will accept without orient_polygon_soup.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me781",
    title="polygon_soup_to_polygon_mesh point_to_vertex_output_iterator: clean consistent-winding 2-triangle soup; point→vertex index map recorded for p0-p3 (Branch 2)",
    defect_class="polygon_soup_point_vertex_map",
)

p0 = m.vertex(0.0, 0.0, 0.0)  # 0
p1 = m.vertex(2.0, 0.0, 0.0)  # 1
p2 = m.vertex(1.0, 1.0, 0.0)  # 2 — shared edge endpoint
p3 = m.vertex(2.0, 1.0, 0.0)  # 3

# t0=(p0,p1,p2): CCW — normal = (p1-p0)×(p2-p0) = (2,0,0)×(1,1,0) = (0,0,2) → +Z
t0 = m.triangle(p0, p1, p2)  # 0: CCW

# t1=(p1,p3,p2): CCW — normal = (p3-p1)×(p2-p1) = (0,1,0)×(-1,1,0) = (-1,0,0)... let's verify:
# (p3-p1) = (0,1,0); (p2-p1) = (-1,1,0)
# cross = (1*0-0*1, 0*(-1)-0*0, 0*1-1*(-1)) = (0, 0, 1) → +Z (CCW)
t1 = m.triangle(p1, p3, p2)  # 1: CCW

# Shared interior edge (p1, p2) — n=2 (manifold edge, shared by t0 and t1).
m.assert_edge_shared(p1, p2, 2)

# Boundary edges — each shared by exactly one triangle.
m.assert_edge_shared(p0, p1, 1)  # t0 bottom
m.assert_edge_shared(p0, p2, 1)  # t0 left
m.assert_edge_shared(p1, p3, 1)  # t1 right
m.assert_edge_shared(p2, p3, 1)  # t1 top

# Euler: V=4, E=5, F=2, chi=1 (open disk, valid for conversion without orient_polygon_soup).
m.assert_euler_characteristic(4, 5, 2, 1)
