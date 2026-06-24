"""Me953 — Basic_TMesh.checkGeometry edge_alloc_failure: edge array alloc guard (Branch 4).

MeshFix `Basic_TMesh.checkGeometry` Branch 4 (*edge_alloc_failure*) @ line 220:
  'evarr == NULL' — after calling toArray() to collect all edges into a sort
  buffer for coincident-edge detection, the null-pointer check fires when the
  allocator cannot provide memory. The coincident-edge scan is skipped; the
  function moves on to the degenerate-triangle check.

Cannot trigger an edge allocation failure geometrically. This fixture uses a
minimal mesh with two spatially coincident edges (the geometry that WOULD
trigger Branch 5 duplicate_edges if allocation succeeds). Branch 4 is the
alloc-guard placeholder for the same geometry.

Geometry: two isolated triangles sharing the same geometric edge position.
  t0=(v0,v1,v2): edge (v0,v1) at (0,0,0)-(1,0,0).
  t1=(v3,v4,v5): edge (v3,v4) at (0,0,0)-(1,0,0) — coincident with (v0,v1)
    but different vertex indices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me953",
    title="Basic_TMesh.checkGeometry edge_alloc_failure: coincident edge pair v0/v3 and v1/v4; evarr==NULL alloc guard (Branch 4)",
    defect_class="coincident_edges",
)

# Triangle 0: edge (v0,v1) at (0,0,0)-(1,0,0).
v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — coincident with v3
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — coincident with v4
v2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(v0, v1, v2)           # t0

# Triangle 1: edge (v3,v4) at same coordinates as (v0,v1).
v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — coincident with v0
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — coincident with v1
v5 = m.vertex(0.5, -1.0, 0.0)   # 5
m.triangle(v3, v4, v5)           # t1

# v0 and v3 are coincident (distance = 0).
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)
# v1 and v4 are coincident (distance = 0).
m.assert_vertex_pair_distance_lt(v1, v4, 1e-12)
# The two edges are spatially coincident.
m.assert_edge_pair_coincident((v0, v1), (v3, v4))
