"""Me950 — Basic_TMesh.checkGeometry memory_allocation_failure: vertex array alloc guard (Branch 1).

MeshFix `Basic_TMesh.checkGeometry` Branch 1 (*memory_allocation_failure*) @ line 196:
  'varr == NULL' — after calling toArray() to collect all vertices into a sort
  buffer, the null-pointer check fires when the allocator cannot provide memory.
  The coincident-vertex scan is skipped entirely; the function continues to the
  edge-deduplication block.

Cannot trigger a memory allocation failure geometrically. This fixture uses a
minimal valid mesh with two near-coincident vertices (the geometry that WOULD
trigger Branch 2 duplicate_vertices if allocation succeeds). Branch 1 is the
alloc-guard placeholder for the same geometry.

Geometry: three triangles. v0=(0,0,0) and v6=(5e-8,0,0) are near-coincident
(distance < 1e-7) but belong to separate triangles with no shared edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me950",
    title="Basic_TMesh.checkGeometry memory_allocation_failure: near-coincident vertex pair v0/v6; varr==NULL alloc guard (Branch 1)",
    defect_class="near_coincident_vertex",
)

# Triangle 0: upper-left control triangle.
v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — near-coincident with v6
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(v0, v1, v2)           # t0

# Triangle 1: clean lower-right control triangle.
v3 = m.vertex(2.0, 0.0, 0.0)    # 3
v4 = m.vertex(3.0, 0.0, 0.0)    # 4
v5 = m.vertex(2.5, 1.0, 0.0)    # 5
m.triangle(v3, v4, v5)           # t1

# Triangle 2: near-coincident vertex v6 slightly offset from v0.
v6 = m.vertex(5e-8, 0.0, 0.0)   # 6 — near-coincident with v0 (distance 5e-8 < 1e-7)
v7 = m.vertex(4.0, 0.0, 0.0)    # 7
v8 = m.vertex(3.5, 1.0, 0.0)    # 8
m.triangle(v6, v7, v8)           # t2

# v0 and v6 are near-coincident (distance = 5e-8 < 1e-7).
m.assert_vertex_pair_distance_lt(v0, v6, 1e-7)
# v0 and v6 share no triangle (no edge between them).
m.assert_vertex_pair_no_shared_triangle(v0, v6)
