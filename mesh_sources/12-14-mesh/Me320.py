"""Me320 — with_third_points_empty_input_guard: zero-point boundary returns immediately (Branch 1).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 1 (*empty_input_guard*) @ line 729:
  'if (points.empty()) return out;'
  When the hole-boundary polyline has zero points, the function returns the
  output iterator unchanged without creating any triangles.

Defect pattern: an isolated vertex with no triangles — the mesh represents
  the state where points.empty() is true.  The output iterator would be
  returned immediately with nothing emitted.

Geometry: single isolated vertex; no triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me320",
             title="with_third_points_empty_input_guard: zero-point hole boundary returns output iterator unchanged (Branch 1)",
             defect_class="hole_in_hull")

# Single isolated vertex — represents the empty-boundary condition.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0

# No triangles — boundary is empty, so no triangulation occurs.

# Isolated vertex assertion: v0 is not referenced by any triangle.
m.assert_isolated_vertex(v0)

# Euler: V=1, E=0, F=0, chi=1 (single point).
m.assert_euler_characteristic(1, 0, 0, 1)
