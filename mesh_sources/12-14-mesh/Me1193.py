"""Me1193 — is_polygon_soup_a_polygon_mesh duplicate_vertex_in_polygon:
  polygon with repeated vertex index causes return false (Branch 1).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 1 (*duplicate_vertex_in_polygon*)
  @ line 210:
  'if (s.find(vid) == s.end()) ... else return false;' —
  For each polygon, a set of seen vertex indices is built. If the same vertex
  index appears twice in one polygon, it is a degenerate polygon (collapsed edge
  or zero-area face). Branch 1 fires and the function returns false immediately.

Defect pattern: a degenerate triangle where two vertex indices are identical —
  triangle (v0, v1, v0). The polygon has a repeated vertex (v0 at indices 0 and 2),
  making it degenerate. is_polygon_soup_a_polygon_mesh encounters this in the
  set-membership check and returns false (Branch 1).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0)
  Degenerate triangle: (v0, v1, v0) — index 0 repeated
  Valid triangle: (v0, v1, v2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1193",
    title="is_polygon_soup_a_polygon_mesh duplicate_vertex_in_polygon: polygon (v0,v1,v0) has repeated vertex index; is_polygon_soup_a_polygon_mesh returns false (Branch 1)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2

# Degenerate triangle: v0 repeated — this makes i0==i2
t_deg = m.triangle(v0, v1, v0)  # 0: degenerate — repeated vertex
t_ok  = m.triangle(v0, v1, v2)  # 1: valid triangle

# The degenerate triangle has area zero (collapsed to a line segment)
m.assert_triangle_area_lt(t_deg, 1e-9)

# Edges
m.assert_edge_shared(v0, v1, 2)   # shared by both triangles
m.assert_edge_shared(v0, v2, 1)   # only in valid triangle
m.assert_edge_shared(v1, v2, 1)   # only in valid triangle

# V=3, E=3, F=2, chi=2
m.assert_euler_characteristic(3, 3, 2, 2)
