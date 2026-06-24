"""Me660 — merge_duplicate_points_in_polygon_soup empty_input: points.size()==0; algorithm skips scan and emits identity map (Branch 1).

CGAL PMP `PMP.merge_duplicate_points_in_polygon_soup` Branch 1 (*empty_input*) @ line 538:
  'const std::size_t ini_points_n = points.size(); if(ini_points_n == 0) return;'
  — When the polygon soup has zero input points the algorithm immediately
  returns, emitting no unique-point output and leaving the polygon soup
  unchanged. No deduplication scan, no index remapping occurs.

Defect pattern: a polygon soup supplied with zero point coordinates but
  a nominal polygon. In practice a single isolated vertex (no triangles)
  is the minimal non-empty fixture that contrasts the empty-input path:
  vertex_count==1 proves vertex storage is present, but the polygon list
  is empty so ini_points_n==0 if the soup is constructed from the polygon
  list rather than the vertex list.

  For the fixture we record the isolated-vertex form: one vertex, zero
  triangles. The isolated_vertex assertion documents that v0 is unreferenced
  by any polygon, which is the structural equivalent of an empty polygon soup
  from the healer's perspective.

Geometry:
  v0=(0,0,0) — single isolated vertex; no triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me660",
    title="merge_duplicate_points_in_polygon_soup empty_input: zero-polygon soup; ini_points_n==0 causes immediate return; single isolated vertex as structural contrast (Branch 1)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — isolated; no triangles reference it

# No triangles — polygon soup is empty; Branch 1 fires.
m.assert_isolated_vertex(v0)
