"""Me800 — is_polygon_soup_a_polygon_mesh duplicate_vertex_in_polygon: triangle with repeated vertex index (Branch 1).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 1 (*duplicate_vertex_in_polygon*) @ line 210:
  'for(std::size_t j = 0; j < polygon.size(); ++j)
   { if(polygon[j] == polygon[k]) return false; }'
  — the validator iterates every pair of indices within each polygon and returns
  false immediately if any two positions share the same vertex index. A collapsed
  triangle (two of its three corners are the same vertex) triggers this branch.

Defect pattern: three-triangle soup with one collapsed polygon. Triangle t0 has
  its first and third vertex both equal to v0 (index 0) — the polygon [0, 1, 0]
  has a repeated index. Triangles t1 and t2 form a valid manifold pair that shows
  the surrounding geometry is otherwise ordinary.

Geometry:
  v0=(0,0,0) [repeated in t0], v1=(1,0,0), v2=(0.5,1,0) [apex],
  v3=(1.5,1,0).
  t0=(v0,v1,v0)  — collapsed; v0 appears at positions 0 and 2.
  t1=(v0,v1,v2)  — valid CCW triangle.
  t2=(v1,v3,v2)  — valid CCW triangle sharing edge (v1,v2) with t1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me800",
    title="is_polygon_soup_a_polygon_mesh duplicate_vertex_in_polygon: triangle [v0,v1,v0] has repeated index (Branch 1)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — repeated in t0 (positions 0 and 2)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — apex
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

# t0 is the defect: vertex 0 appears at both position 0 and position 2.
t0 = m.triangle(v0, v1, v0)   # collapsed — indices [0, 1, 0]
t1 = m.triangle(v0, v1, v2)   # valid CCW
t2 = m.triangle(v1, v3, v2)   # valid CCW

# t0 has zero area because two corners coincide at the same point.
m.assert_triangle_area_lt(t0, 1e-9)

# Edge (v0,v1) appears in both t0 and t1; t0 also has a degenerate self-loop
# edge (v0,v0). The valid pair (v1,v2) shared by t1 and t2 is manifold n=2.
m.assert_edge_shared(v1, v2, 2)
