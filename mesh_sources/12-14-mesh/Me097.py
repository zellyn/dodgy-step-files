"""Me097 — edge_collapse_orphan_vertex: isolated vertex left after failed collapse cleanup.

Catalog claim: a mesh contains an isolated vertex (v0) that is not referenced by
any triangle. This models the post-collapse state when MeshFix `collapseOnV1`
Branch 12 (*MARK_UNLINKED_V2*) sets 'v2->e0 = NULL' but the vertex record
remains in the vertex list without being freed or removed.

The resulting mesh has v0 as a dangling isolated vertex — a defect that is distinct
from a near-coincident-vertex (v0 is not close to any other vertex; it was simply
left behind after the merge).

This exercises Branch 12 (*MARK_UNLINKED_V2*): in MeshFix, after collapsing v0
onto v1, the vertex v0 is marked unlinked (e0=NULL). The fixture captures a mesh
where a vertex has zero triangle references — the state MeshFix leaves behind.

Defect carrier: 4 vertices forming two triangles, with v0 not referenced by
any triangle. v0 is geometrically separate from the triangle cluster.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me097",
             title="edge_collapse_orphan_vertex: isolated vertex left behind by collapse cleanup",
             defect_class="isolated_vertex")

v0 = m.vertex(5.0, 5.0, 0.0)   # 0 — isolated (unreferenced) vertex: post-collapse orphan
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — collapse target vertex (now absorbs all fan triangles)
v2 = m.vertex(1.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.5, 1.0, 0.0)   # 3
v4 = m.vertex(0.5, -1.0, 0.0)  # 4

# Triangle mesh around v1 — the fan that was formerly shared with v0.
t0 = m.triangle(v1, v2, v3)   # 0
t1 = m.triangle(v1, v4, v2)   # 1

# v0 is NOT referenced by any triangle → isolated vertex.
m.assert_isolated_vertex(v0)

# The remaining mesh is well-formed.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v3, 1)   # boundary
m.assert_edge_shared(v1, v4, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary
m.assert_edge_shared(v2, v4, 1)   # boundary
