"""Me176 — orient_multi_neighbor_same_orient: edge has >1 incident polygon in same-direction map.

Catalog claim: a non-manifold configuration where three triangles all traverse
the same directed edge (v0→v1) in the same direction. Branch 7
(*multi_neighbor_same_orient*) fires when the same-orientation edge map entry
for (i1→i2) contains more than one incident polygon:
`if (it_same_orient->second.size() > 1)`.

Geometric signature: three triangles — t0, t1, t2 — each include directed
edge v0→v1 as their first half-edge. This means the edge map bucket for
directed (v0→v1) collects all three: a size > 1 condition that Branch 7
catches. This is the orient-specific flavor of non-manifold (same-direction,
not just count->2).

Defect carrier: the directed edge (v0→v1) appears in three triangle
definitions, filling the same-orientation bucket with 3 entries. The
non-manifold edge (v0,v1) is shared by 3 triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me176",
             title="orient multi_neighbor_same_orient: same directed edge in >1 incident polygon same-direction map",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — above edge, +Z
v3 = m.vertex(0.5,-1.0, 0.0)   # 3 — below edge, -Z
v4 = m.vertex(0.5, 0.0, 1.0)   # 4 — out of XY plane

# All three triangles include directed edge v0→v1.
t0 = m.triangle(v0, v1, v2)   # directed v0→v1→v2
t1 = m.triangle(v0, v1, v3)   # directed v0→v1→v3 (same starting half-edge)
t2 = m.triangle(v0, v1, v4)   # directed v0→v1→v4 (same starting half-edge)

# All 3 triangles share the same undirected edge (v0,v1).
m.assert_edge_shared(v0, v1, 3)

# t0 and t1 have antiparallel normals (multi-neighbor same-orient conflict).
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
