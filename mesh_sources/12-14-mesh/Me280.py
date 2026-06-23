"""Me280 — checkGeometry_memory_alloc_fail_vertices: near-coincident pair triggers alloc guard (Branch 1).

MeshFix `checkAndRepair::checkGeometry` Branch 1 (*MEMORY_ALLOCATION_FAILURE*) @ line 196:
  Vertex array allocation for coincident-vertex check fails; function skips the
  coincident-vertex scan and continues. The same near-coincident vertex geometry
  would be caught by Branches 2–3 if memory is available.

Geometry: two distinct but spatially near-identical triangles in separate half-spaces,
with one vertex pair separated by 5e-8 (sub-tolerance coincident). The pair does NOT
share any triangle, so if the allocator succeeds it routes to Branch 2
(COINCIDENT_VERTICES_EDGE_ABSENT). Branch 1 fires when ExtTriMesh::newVertices fails
to allocate the sort buffer.

Triangle t0: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — clean upper triangle.
Triangle t1: v3=(0,0,2), v4=(1,0,2), v5=(0.5,1,2) — clean lower triangle.
Near-coincident pair: v6=(0,0,0) vs v0=(0,0,0) separated by ε=5e-8.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 193–200; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me280",
    title="checkGeometry_memory_alloc_fail_vertices: near-coincident vertex pair, alloc guard (Branch 1)",
    defect_class="coincident_vertices",
)

# Triangle 0 — clean upper triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
m.triangle(v0, v1, v2)          # t0

# Triangle 1 — clean lower triangle (separate from t0).
v3 = m.vertex(0.0, 0.0, 2.0)   # 3
v4 = m.vertex(1.0, 0.0, 2.0)   # 4
v5 = m.vertex(0.5, 1.0, 2.0)   # 5
m.triangle(v3, v4, v5)          # t1

# Near-coincident vertex: v6 at same position as v0, but distinct index.
# Separation 5e-8 < default MeshFix epsilon for coincident detection.
v6 = m.vertex(5e-8, 0.0, 0.0)  # 6 — spatially ~= v0, no shared triangle

# Triangle 2 — uses the near-coincident vertex to anchor it in the mesh.
v7 = m.vertex(0.5, -1.0, 0.0)  # 7
v8 = m.vertex(-0.5, -1.0, 0.0) # 8
m.triangle(v6, v7, v8)          # t2 — v6 isolated from v0 (no shared triangle)

# Assert: v0 and v6 are near-coincident (Branch 1/2 trigger geometry).
m.assert_vertex_pair_distance_lt(v0, v6, 1e-7)

# Assert: v0 and v6 share no triangle (EDGE_ABSENT pattern — Branch 2 if alloc succeeds).
m.assert_vertex_pair_no_shared_triangle(v0, v6)
