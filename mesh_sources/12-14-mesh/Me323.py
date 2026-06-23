"""Me323 — with_third_points_visitor_optional: Default_visitor substituted when no visitor provided (Branch 4).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 4 (*visitor_parameter_optional*) @ line 746:
  'typename GetVisitor::type visitor = choose_parameter(…, Default_visitor());'
  When the caller does not supply a visitor named parameter, CGAL substitutes
  a no-op Default_visitor.  The visitor is then passed to Is_valid_compose,
  which uses it to filter candidate triangulations.

Defect pattern: a pentagonal hole boundary (5 vertices) representing a hole
  that would be triangulated by with_third_points; the visitor controls
  acceptance of candidate triangles.

Geometry: regular pentagon hole boundary.
  v0-v4 at unit radius in the XY plane. Five surrounding triangles (fan from
  a hub v5=(0,0,0)) close the disk; the outer boundary is the hole.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me323",
             title="with_third_points_visitor_optional: Default_visitor substituted when visitor param absent (Branch 4)",
             defect_class="hole_in_hull")

# Pentagon vertices at radius 1.
def pt(k):
    angle = 2 * math.pi * k / 5
    return math.cos(angle), math.sin(angle), 0.0

v0 = m.vertex(*pt(0))   # 0
v1 = m.vertex(*pt(1))   # 1
v2 = m.vertex(*pt(2))   # 2
v3 = m.vertex(*pt(3))   # 3
v4 = m.vertex(*pt(4))   # 4
v5 = m.vertex(0.0, 0.0, 0.0)   # 5 — hub

# 5-triangle fan from hub.
t0 = m.triangle(v0, v1, v5)   # 0
t1 = m.triangle(v1, v2, v5)   # 1
t2 = m.triangle(v2, v3, v5)   # 2
t3 = m.triangle(v3, v4, v5)   # 3
t4 = m.triangle(v4, v0, v5)   # 4

# Hub spoke edges — each shared by 2 triangles.
m.assert_edge_shared(v0, v5, 2)
m.assert_edge_shared(v1, v5, 2)
m.assert_edge_shared(v2, v5, 2)
m.assert_edge_shared(v3, v5, 2)
m.assert_edge_shared(v4, v5, 2)

# Outer pentagon edges — each incident on 1 triangle (boundary of hole).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Hole boundary the visitor-controlled triangulation must fill.
m.assert_hole_boundary([v0, v1, v2, v3, v4])

# Euler: V=6, E=10 (5 outer + 5 hub), F=5, chi=1 (open disk).
m.assert_euler_characteristic(6, 10, 5, 1)
