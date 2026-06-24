"""Me954 — Basic_TMesh.checkGeometry duplicate_edges: lexicographic coincident edge detection (Branch 5).

MeshFix `Basic_TMesh.checkGeometry` Branch 5 (*duplicate_edges*) @ line 226:
  lexicographic edge comparison — after sorting all edges by endpoint coordinates,
  consecutive entries where both endpoint coordinates are identical are detected as
  coincident edges. A warning is logged and `ret` is updated to record the defect.
  The function continues scanning after this; it does not return early.

Defect pattern: two distinct half-edges that occupy the same geometric line
segment. Triangle t0 and triangle t1 each contain an edge at positions
(0,0,0)→(1,0,0), but using different vertex indices. After lexicographic
sorting of all edges by coordinate, these two entries are adjacent with
coordinate difference 0 → Branch 5 fires.

Geometry: two isolated triangles.
  t0=(v0,v1,v2): v0=(0,0,0), v1=(1,0,0) — edge at (0,0,0)-(1,0,0).
  t1=(v3,v4,v5): v3=(0,0,0), v4=(1,0,0), v5=(0.5,-1,0) — same geometric
    edge but on the opposite side, forming a bowtie/stitch pattern.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me954",
    title="Basic_TMesh.checkGeometry duplicate_edges: edge (v0,v1) at (0,0,0)-(1,0,0) spatially coincident with (v3,v4) (Branch 5)",
    defect_class="coincident_edges",
)

# Triangle 0: upper half, edge (v0,v1) at bottom.
v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — coincident with v3
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — coincident with v4
v2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(v0, v1, v2)           # t0

# Triangle 1: lower half, edge (v3,v4) at same position as (v0,v1).
v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — at same coords as v0
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — at same coords as v1
v5 = m.vertex(0.5, -1.0, 0.0)   # 5
m.triangle(v3, v4, v5)           # t1

# v0 and v3 are coincident.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-12)
# v1 and v4 are coincident.
m.assert_vertex_pair_distance_lt(v1, v4, 1e-12)
# Edges (v0,v1) and (v3,v4) are spatially coincident.
m.assert_edge_pair_coincident((v0, v1), (v3, v4))
