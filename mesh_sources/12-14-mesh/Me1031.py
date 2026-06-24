"""Me1031 — remove_invalid_polygons_degenerate_filter: std::remove_if predicate returns true for collapsed triangle (polygon.size() <= 2 check fires via duplicate vertex).

CGAL PMP `PMP.remove_invalid_polygons_in_polygon_soup` Branch 1
(*degenerate_polygon_filter*) @ line 298:
  'auto it = std::remove_if(polygons.begin(), polygons.end(),
     [](const Polygon& polygon) {
       return polygon.size() <= 2 ||
              has_duplicate_vertex(polygon); });'
  — the predicate evaluates each polygon; when a triangle contains a
  repeated vertex index (v0 == v1), it is structurally equivalent to a
  2-vertex polygon and has_duplicate_vertex returns true, so remove_if
  marks it for erasure. Branch 1 fires: predicate returns true for the
  degenerate face.

Defect pattern: a polygon soup containing one degenerate triangle where
  vertex 0 and vertex 1 are the same index (v0 == v1 == 0). The face
  [0, 0, 1] is a collapsed sliver — geometrically zero-area. The
  remove_if predicate catches it via the duplicate-vertex check.
  A second valid triangle is also present so the polygon list is non-empty
  after erasure (the erase_execution branch, Me1032, handles the mixed case).

Geometry:
  Vertices: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0).
  Valid triangle t0 = (v0, v1, v2).
  Degenerate triangle t1 = (v0, v0, v1)  [index 0 repeated; zero-area sliver].
  t1 has zero area because two vertex indices are identical.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1031",
    title="remove_invalid_polygons_degenerate_filter: duplicate-vertex triangle [v0,v0,v1] triggers remove_if predicate (Branch 1)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Valid triangle.
t0 = m.triangle(v0, v1, v2)

# Degenerate: v0 repeated — this is a polygon with a duplicate vertex;
# remove_invalid_polygons_in_polygon_soup Branch 1 predicate returns true.
t1 = m.triangle(v0, v0, v1)

# t1 is zero-area (two vertices coincide).
m.assert_triangle_area_lt(t1, 1e-9)

# Valid triangle edges each boundary (n=1); degenerate edge (0,0) is a
# degenerate self-loop, and edge (0,1) appears in both triangles (n=2).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
