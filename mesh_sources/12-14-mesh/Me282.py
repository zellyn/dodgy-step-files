"""Me282 — checkGeometry_coincident_vertices_with_edge: two coincident vertices sharing an edge (Branch 3).

MeshFix `checkAndRepair::checkGeometry` Branch 3 (*COINCIDENT_VERTICES_WITH_EDGE*) @ line 208:
  `getEdge(v2) != null` — two vertices at the same geometric point ARE connected by a
  half-edge. This is a severe defect: the edge has zero length, making it degenerate.
  checkGeometry returns immediately with the first vertex as the error location.

Geometry: a triangle where two vertices (v0 and v1) occupy the same point. The triangle
has a degenerate zero-length edge from v0 to v1. This is distinct from a true degenerate
triangle (collinear) because the vertex positions are literally identical — the edge
connecting them has length zero.

Triangle t0: v0=(1,0,0), v1=(1,0,0) (same coords), v2=(0,1,0).
  Edge (v0,v1) has length 0; triangle area = 0.
Triangle t1: v3=(0,0,0), v4=(2,0,0), v5=(1,1,0) — clean control.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 207–212; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me282",
    title="checkGeometry_coincident_vertices_with_edge: coincident vertices connected by zero-length edge (Branch 3)",
    defect_class="coincident_vertices",
)

# Triangle 1 (control) — clean triangle placed first so it's t0.
v3 = m.vertex(0.0, 0.0, 0.0)   # 0
v4 = m.vertex(2.0, 0.0, 0.0)   # 1
v5 = m.vertex(1.0, 1.0, 0.0)   # 2
m.triangle(v3, v4, v5)          # t0 — clean

# Degenerate triangle: v0 and v1 at identical position (1,0,0).
# The half-edge data structure has an explicit edge (v0,v1) of length 0.
v0 = m.vertex(1.0, 0.0, 0.0)   # 3
v1 = m.vertex(1.0, 0.0, 0.0)   # 4 — exact coincidence with v0
v2 = m.vertex(0.0, 1.0, 0.0)   # 5
m.triangle(v0, v1, v2)          # t1 — degenerate; edge (v0,v1) has length 0

# Assert: v0 and v1 are coincident (distance = 0).
m.assert_vertex_pair_distance_lt(v0, v1, 1e-12)

# The degenerate triangle has zero area (v0==v1 as coords → zero cross product).
m.assert_triangle_area_lt(1, 1e-12)

# The edge (v0,v1) exists in the mesh (it's in triangle t1).
# Edge is shared by exactly 1 triangle (boundary), confirming it is a real edge.
m.assert_edge_shared(v0, v1, 1)
