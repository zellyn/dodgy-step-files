"""Me360 — remove_isolated_points_empty_input: empty vertex list triggers early return.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 1 (*empty_input*) @ line 410:
  'if(points.empty()) return 0;' — when the points container is empty the function
  returns immediately without touching polygons.

Defect pattern: a polygon soup where the vertex list has zero entries. The polygon
  list is also empty (you cannot have valid faces with no points). The function must
  correctly short-circuit: 0 removed, 0 iterations performed.

Geometry: completely empty mesh — 0 vertices, 0 triangles.
  The only assertion is Euler V=0, E=0, F=0, chi=0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me360",
             title="remove_isolated_points_empty_input: empty vertex list triggers early return with 0 removed",
             defect_class="isolated_vertex")

# No vertices, no triangles.
# Euler: V=0, E=0, F=0, chi=0.
m.assert_euler_characteristic(0, 0, 0, 0)
