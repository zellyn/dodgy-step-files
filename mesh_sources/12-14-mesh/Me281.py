"""Me281 — checkGeometry_coincident_vertices_edge_absent: two coincident vertices, no connecting edge (Branch 2).

MeshFix `checkAndRepair::checkGeometry` Branch 2 (*COINCIDENT_VERTICES_EDGE_ABSENT*) @ line 204:
  `getEdge(v2) == null` — two vertices occupy the same geometric point but are NOT
  connected by an edge. checkGeometry marks the first as defective and continues
  searching the sorted vertex list for more coincident pairs.

Geometry: a mesh with six vertices arranged in two separate triangles. Vertices v0
and v3 are placed at identical coordinates (0,0,0) but belong to different triangles
(t0 and t1 respectively) — no triangle references both, so no half-edge connects them.
This is the canonical COINCIDENT_VERTICES_EDGE_ABSENT pattern.

Triangle t0: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — uses v0 at origin.
Triangle t1: v3=(0,0,0), v4=(1,0,2), v5=(0.5,1,2) — v3 coincides with v0, no shared edge.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 201–207; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me281",
    title="checkGeometry_coincident_vertices_edge_absent: two coincident vertices without connecting edge (Branch 2)",
    defect_class="coincident_vertices",
)

# Triangle 0 — uses v0 at origin.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
m.triangle(v0, v1, v2)          # t0

# Triangle 1 — v3 is at the SAME position as v0 but distinct index; no shared triangle.
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — exact coincidence with v0
v4 = m.vertex(1.0, 0.0, 2.0)   # 4
v5 = m.vertex(0.5, 1.0, 2.0)   # 5
m.triangle(v3, v4, v5)          # t1 — no triangle contains both v0 and v3

# Assert: v0 and v3 are coincident (distance = 0).
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)

# Assert: v0 and v3 share no triangle (confirms EDGE_ABSENT branch).
m.assert_vertex_pair_no_shared_triangle(v0, v3)
