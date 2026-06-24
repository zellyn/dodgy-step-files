"""Me1150 — is_degenerate_edge equal_points: endpoint positions identical (zero-length edge).

CGAL PMP `PMP.is_degenerate_edge` Branch 1 (*equal_points*) @ line 871:
  'if(get(vpm, source(e, tm)) == get(vpm, target(e, tm))) return true;' —
  when both endpoints of a halfedge share the same point in 3D space the edge
  has zero length and is immediately flagged as degenerate.

Defect pattern: a triangle where two distinct topological vertices (v0 and v1)
  are placed at the same coordinate (0, 0, 0). The edge v0→v1 has zero length;
  PMP.is_degenerate_edge fires Branch 1 on first evaluation. A supporting
  triangle (v0,v1,v2) provides the face context needed to hold the edge in a
  halfedge structure; the triangle also has zero area because two vertices
  coincide.

Geometry:
  v0=(0,0,0), v1=(0,0,0) [==v0], v2=(1,0,0)
  t0=(v0,v1,v2) — zero-length edge between v0 and v1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1150",
    title="is_degenerate_edge equal_points: endpoint positions identical — zero-length edge between v0==v1 at (0,0,0)",
    defect_class="degenerate_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — first endpoint
v1 = m.vertex(0.0, 0.0, 0.0)  # 1 — second endpoint; coincident with v0 → zero-length edge
v2 = m.vertex(1.0, 0.0, 0.0)  # 2 — third vertex to form a face

# Single triangle containing the degenerate (zero-length) edge.
t0 = m.triangle(v0, v1, v2)  # 0: face holding the degenerate edge

# v0 and v1 are at exactly the same coordinate — zero-length edge.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# The degenerate edge (v0,v1) is a boundary edge — incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)

# The triangle has zero area because v0 == v1.
m.assert_triangle_area_lt(t0, 1e-9)
