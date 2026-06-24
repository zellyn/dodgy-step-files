"""Me782 — polygon_soup_to_polygon_mesh polygon_to_face_output_iterator: consistently wound soup; polygon→face descriptor map recorded (Branch 3).

CGAL PMP `PMP.polygon_soup_to_polygon_mesh` Branch 3 (*polygon_to_face_output_iterator*) @ line 310:
  'if(polygon_to_face_output_iterator != boost::none) { ... }'
  — after a consistently oriented soup is converted to a polygon mesh, if
  the caller supplies a polygon_to_face_output_iterator, the algorithm records
  a map from each soup polygon index to the face descriptor it was assigned in
  the output mesh. Analogous to Branch 2 but for faces rather than vertices.
  This branch fires for any clean soup where the caller requests the
  polygon→face correspondence.

Defect pattern (input pattern): a minimal consistently wound polygon soup
  (four vertices, two triangles sharing an interior edge) that is already
  valid for direct conversion. No orientation repair is needed. The Branch 3
  path fires because a polygon_to_face_output_iterator is provided — the map
  records polygon 0→face f0, polygon 1→face f1 after conversion.

Geometry (XY plane):
  q0=(0,0,0), q1=(1,0,0), q2=(0.5,1,0), q3=(1.5,1,0)
  t0=(q0,q1,q2): CCW, normal +Z
  t1=(q1,q3,q2): CCW, normal +Z
  Shared interior edge: (q1,q2).
  Both triangles consistently wound; soup is valid for conversion.

Assertions:
  - Shared interior edge (q1,q2) n=2 (manifold interior edge).
  - Boundary edges each n=1 (open-disk topology).
  - euler_characteristic V=4, E=5, F=2, chi=1 confirms valid open-disk mesh
    that conversion accepts without orient_polygon_soup.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me782",
    title="polygon_soup_to_polygon_mesh polygon_to_face_output_iterator: clean consistent-winding 2-triangle soup; polygon→face descriptor map recorded for t0,t1 (Branch 3)",
    defect_class="polygon_soup_polygon_face_map",
)

q0 = m.vertex(0.0, 0.0, 0.0)  # 0
q1 = m.vertex(1.0, 0.0, 0.0)  # 1 — shared edge endpoint
q2 = m.vertex(0.5, 1.0, 0.0)  # 2 — shared edge endpoint
q3 = m.vertex(1.5, 1.0, 0.0)  # 3

# t0=(q0,q1,q2): CCW — normal = (q1-q0)×(q2-q0) = (1,0,0)×(0.5,1,0) = (0,0,1) → +Z
t0 = m.triangle(q0, q1, q2)  # 0: CCW

# t1=(q1,q3,q2): CCW — (q3-q1)×(q2-q1) = (0.5,1,0)×(-0.5,1,0) = (-1,0,0.5+0.5)
# more carefully: cross((0.5,1,0),(-0.5,1,0)) = (1*0-0*1, 0*(-0.5)-0.5*0, 0.5*1-1*(-0.5)) = (0,0,1) → +Z (CCW)
t1 = m.triangle(q1, q3, q2)  # 1: CCW

# Shared interior edge (q1, q2) — n=2 (manifold edge, shared by t0 and t1).
m.assert_edge_shared(q1, q2, 2)

# Boundary edges — each shared by exactly one triangle.
m.assert_edge_shared(q0, q1, 1)  # t0 bottom
m.assert_edge_shared(q0, q2, 1)  # t0 left
m.assert_edge_shared(q1, q3, 1)  # t1 right
m.assert_edge_shared(q2, q3, 1)  # t1 top

# Euler: V=4, E=5, F=2, chi=1 (open disk, valid for conversion without orient_polygon_soup).
m.assert_euler_characteristic(4, 5, 2, 1)
