"""Me801 — is_polygon_soup_a_polygon_mesh non_manifold_edge: edge shared by 3 polygons (Branch 2).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 2 (*non_manifold_edge*) @ line 220:
  'if(it->second.size() > 2) { ...; marked_edges.insert(edge); }'
  — after building the edge-to-polygon map the validator checks each edge's
  incident polygon count. When a single directed edge (or its reverse) is used by
  more than two polygons the edge is non-manifold and is inserted into marked_edges.
  This branch fires for the first such over-shared edge encountered.

Defect pattern: three triangles all sharing the directed edge v0→v1. Each triangle
  fans away to a distinct apex vertex (v2, v3, v4) so the topology is otherwise
  star-shaped, but edge (v0,v1) is incident on three faces — one more than the
  manifold maximum of two. CGAL marks this edge singular.

Geometry:
  v0=(0,0,0), v1=(1,0,0) — the over-shared edge endpoints.
  v2=(0.5, 1.0, 0.0)   — fan apex A (above XZ plane).
  v3=(0.5,-1.0, 0.0)   — fan apex B (below XZ plane).
  v4=(0.5, 0.0, 1.0)   — fan apex C (out of plane).
  t0=(v0,v1,v2), t1=(v0,v1,v3), t2=(v0,v1,v4) all share edge (v0,v1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me801",
    title="is_polygon_soup_a_polygon_mesh non_manifold_edge: edge (v0,v1) shared by 3 triangles marks edge singular (Branch 2)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0, 0.0,  0.0)  # 0 — shared edge start
v1 = m.vertex(1.0, 0.0,  0.0)  # 1 — shared edge end
v2 = m.vertex(0.5, 1.0,  0.0)  # 2 — fan apex A
v3 = m.vertex(0.5,-1.0,  0.0)  # 3 — fan apex B
v4 = m.vertex(0.5, 0.0,  1.0)  # 4 — fan apex C

# All three triangles share edge (v0, v1) — the non-manifold defect.
t0 = m.triangle(v0, v1, v2)   # fan A
t1 = m.triangle(v0, v1, v3)   # fan B
t2 = m.triangle(v0, v1, v4)   # fan C

# Edge (v0,v1) is incident on 3 triangles → marked_edges fires.
m.assert_edge_shared(v0, v1, 3)
