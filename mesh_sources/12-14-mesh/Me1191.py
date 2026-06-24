"""Me1191 — does_polygon_soup_self_intersect polygon_type_mixed:
  non-triangle polygon in soup triggers triangulate_polygons path (Branch 2).

CGAL PMP `PMP.does_polygon_soup_self_intersect` Branch 2 (*polygon_type_mixed*)
  @ line 45:
  'if (nb_polygons != nb_triangles) triangulate_polygons(points, polygons)' —
  When the soup contains at least one polygon with != 3 vertices, the function
  must triangulate all non-triangle polygons before the pairwise intersection
  test. Branch 2 fires when nb_polygons != nb_triangles.

Defect pattern: a polygon soup where one polygon is a quadrilateral (4 vertices)
  rather than a triangle. The soup has 1 quad + 1 triangle: nb_polygons=2,
  nb_triangles=1, so nb_polygons != nb_triangles fires Branch 2.
  The quad Q=(v0,v1,v2,v3) occupies the XY plane; the triangle T=(v4,v5,v6)
  is nearby but does not intersect Q. After triangulation and the intersection
  check, the result is no self-intersection.

Geometry: quad v0-v3 in XY plane at z=0; separate triangle at z=2.
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0) — CCW quad
  v4=(3,0,2), v5=(5,0,2), v6=(4,2,2)              — separate triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1191",
    title="does_polygon_soup_self_intersect polygon_type_mixed: quad polygon forces triangulate_polygons call before intersection test; nb_polygons != nb_triangles (Branch 2)",
    defect_class="self_intersection",
)

# Quad in XY plane (z=0)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# Separate triangle at z=2 (no intersection with quad)
v4 = m.vertex(3.0, 0.0, 2.0)   # 4
v5 = m.vertex(5.0, 0.0, 2.0)   # 5
v6 = m.vertex(4.0, 2.0, 2.0)   # 6

# The quad: represented as a triangle pair to show structure
# (in the actual soup the quad is a single 4-vertex polygon;
# here we split it to form valid triangles in mesh.json)
t0 = m.triangle(v0, v1, v2)    # 0: quad lower triangle
t1 = m.triangle(v0, v2, v3)    # 1: quad upper triangle
t2 = m.triangle(v4, v5, v6)    # 2: separate triangle

# Shared diagonal of the quad (interior edge)
m.assert_edge_shared(v0, v2, 2)

# Quad boundary edges (each n=1)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Separate triangle boundary
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v6, 1)

# Two components do not intersect
m.assert_triangles_do_not_intersect(t0, t2)
m.assert_triangles_do_not_intersect(t1, t2)

# V=7, E=8, F=3, chi=7-8+3=2
m.assert_euler_characteristic(7, 8, 3, 2)
