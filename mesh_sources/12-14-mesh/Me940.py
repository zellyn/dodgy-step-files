"""Me940 — orient_polygon_soup initial_point_count: initial_nb_pts captured before reorientation.

CGAL PMP `PMP.orient_polygon_soup` Branch 1 (*initial_point_count*) @ line 556:
  'std::size_t initial_nb_pts = points.size();'
  — the very first executable statement of orient_polygon_soup stores the current
  number of points in the soup. This count is later compared against points.size()
  after potential vertex duplication to detect whether non-manifold vertices were
  present. Branch 1 fires for any non-empty polygon soup.

Defect pattern: a minimal valid triangle soup (four vertices, two triangles sharing
  one edge). Any call to orient_polygon_soup on a non-empty soup will hit this line;
  the simplest fixture is a flat open strip with a shared interior edge.

Geometry:
  p0=(0,0,0), p1=(1,0,0), p2=(0.5,1,0), p3=(1.5,1,0)
  t0=(p0,p1,p2), t1=(p1,p3,p2) sharing edge (p1,p2).
  initial_nb_pts = 4 → Branch 1 executes for this non-empty soup.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me940",
    title="orient_polygon_soup initial_point_count: initial_nb_pts = points.size() = 4 captured at entry (Branch 1)",
    defect_class="inconsistent_face_orientation",
)

p0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
p1 = m.vertex(1.0, 0.0, 0.0)   # 1 — right base / shared edge endpoint
p2 = m.vertex(0.5, 1.0, 0.0)   # 2 — left apex / shared edge endpoint
p3 = m.vertex(1.5, 1.0, 0.0)   # 3 — right apex

# Two triangles sharing interior edge (p1, p2).
t0 = m.triangle(p0, p1, p2)    # 0: left triangle
t1 = m.triangle(p1, p3, p2)    # 1: right triangle

# Shared interior edge — n=2 confirms two triangles build the edge map.
m.assert_edge_shared(p1, p2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p0, p2, 1)
m.assert_edge_shared(p1, p3, 1)
m.assert_edge_shared(p2, p3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk — no vertex duplication needed).
m.assert_euler_characteristic(4, 5, 2, 1)
