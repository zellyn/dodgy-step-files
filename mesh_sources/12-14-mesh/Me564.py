"""Me564 — loopSubdivision triangle_topology_after_split: pre-selected fan; new sub-triangles marked visited.

Basic_TMesh.loopSubdivision Branch 5 (*triangle_topology_after_split*) @ line 131:
  'if(ls->e->t2 != NULL) { MARK_VISIT(ls->t1); MARK_VISIT(ls->t2); }'
  — After each edge split, new triangles are created. For an interior edge (n=2),
  the split creates 4 sub-triangles (t1, t2 for each side); for a boundary edge
  (n=1) only 2 sub-triangles are created. When is_selection is active and the
  parent triangle was IS_VISITED, the new sub-triangles must also be marked visited.
  Branch 5 fires when ls->e->t2 (the triangle on the other side of the split edge)
  is non-NULL — i.e. the edge is interior — and both new sub-triangles are marked.

Fixture: a 5-triangle fan around vertex v0 where all triangles are IS_VISITED and
  all spoke edges (v0,vi) are interior. This represents the pre-split state:
  when each fan edge is split, t2 is non-NULL so MARK_VISIT fires for both sub-triangles.

Geometric signature:
  v0 = central fan vertex (all incident edges are interior, n=2)
  v1–v5 = fan ring, each adjacent pair shares one interior spoke edge through v0
  The ring edges (v1-v2, v2-v3, etc.) are boundary edges (n=1)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me564",
    title="loopSubdivision triangle_topology_after_split: 5-triangle fan around v0; all spoke edges interior (n=2); both sub-triangles per split get MARK_VISIT (Branch 5)",
    defect_class="loop_subdivision",
)

# Central fan vertex — all incident edges are interior (n=2).
v0 = m.vertex(0.5, 0.5, 0.0)  # 0 — hub; all (v0,vi) are interior

# Fan ring: 5 outer boundary vertices.
v1 = m.vertex(1.5, 0.0,  0.0)  # 1
v2 = m.vertex(2.0, 1.0,  0.0)  # 2
v3 = m.vertex(1.5, 2.0,  0.0)  # 3
v4 = m.vertex(0.0, 2.0,  0.0)  # 4
v5 = m.vertex(-0.5, 1.0, 0.0)  # 5

# Five fan triangles — all pre-selected (IS_VISITED) in the algorithm.
t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2
t3 = m.triangle(v0, v4, v5)   # 3
t4 = m.triangle(v0, v5, v1)   # 4

# All spoke edges (v0, vi) are interior: shared by exactly 2 consecutive fan triangles.
m.assert_edge_shared(v0, v1, 2)  # t0 and t4
m.assert_edge_shared(v0, v2, 2)  # t0 and t1
m.assert_edge_shared(v0, v3, 2)  # t1 and t2
m.assert_edge_shared(v0, v4, 2)  # t2 and t3
m.assert_edge_shared(v0, v5, 2)  # t3 and t4

# Ring boundary edges (n=1 — on the mesh boundary).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v1, 1)

# Euler characteristic: V=6, E=10, F=5, chi=1 (open disk / pentagon).
m.assert_euler_characteristic(6, 10, 5, 1)
