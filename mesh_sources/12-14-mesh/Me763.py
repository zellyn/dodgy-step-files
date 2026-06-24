"""Me763 — retriangulateVT_retriangulation_rollback: quality check failed (i < nt); new triangles unlinked, original VT restored (Branch 4).

MeshFix `holeFilling::retriangulateVT` Branch 4 (*RETRIANGULATION_ROLLBACK*) @ line 413:
  'if (i < nt) { /* unlink new triangles, restore original VT structure */ }'
  After the quality-check loop (Branch 3) breaks early due to an overlapping
  or degenerate new triangle, the re-triangulation index i is less than nt
  (total number of new triangles produced by TriangulateHole). This condition
  triggers the rollback path: all newly introduced triangles are unlinked and
  the original vertex-triangle (VT) incidence list is restored.

Defect pattern: a vertex hub v0 with a 3-triangle fan. The existing fan
  represents the 'original VT' state. A second triangle t3 is introduced
  that is a duplicate of t0 — meaning TriangulateHole produced at least one
  bad triangle (duplicate / overlapping), the quality check fires (Branch 3),
  and since i < nt, the rollback branch fires (Branch 4) to restore the
  original fan t0, t1, t2.

  The duplicate pair (t0, t3) with identical vertex sets [v0,v1,v2] represents
  the failing new triangle that the rollback discards. After rollback, only the
  original three fan triangles (t0, t1, t2) remain.

Geometry:
  v0=(1,1,0) — hub, v1=(0,0,0), v2=(2,0,0), v3=(2,2,0), v4=(0,2,0)
  Original fan: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4)
  Bad new triangle: t3=(v0,v1,v2) — exact duplicate of t0; triggers rollback.

Edge incidence with duplicate t3 present:
  (0,1)=(v0,v1): t0 + t3 → n=2  (non-manifold: 2 triangles on same edge)
  (0,2)=(v0,v2): t0 + t1 + t3 → n=3  (non-manifold)
  (0,3)=(v0,v3): t1 + t2 → n=2
  (0,4)=(v0,v4): t2 only → n=1
  (1,2)=(v1,v2): t0 + t3 → n=2  (non-manifold)
  (2,3)=(v2,v3): t1 → n=1
  (3,4)=(v3,v4): t2 → n=1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me763",
    title="retriangulateVT_retriangulation_rollback: duplicate triangle t3==t0=(v0,v1,v2) causes quality check failure; i<nt triggers rollback, original VT restored (Branch 4)",
    defect_class="retriangulate_region_unlinked",
)

# Hub vertex
v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — hub vertex

# Outer boundary vertices
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — SW
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — SE
v3 = m.vertex(2.0, 2.0, 0.0)   # 3 — NE
v4 = m.vertex(0.0, 2.0, 0.0)   # 4 — NW

# Original 3-triangle fan (the 'original VT' state that rollback restores).
t0 = m.triangle(v0, v1, v2)   # 0 — original fan triangle
t1 = m.triangle(v0, v2, v3)   # 1 — original fan triangle
t2 = m.triangle(v0, v3, v4)   # 2 — original fan triangle

# Duplicate triangle (bad new triangle from TriangulateHole, same vertex set as t0).
# This triangle overlaps t0 exactly — quality check fires, rollback triggered.
t3 = m.triangle(v0, v1, v2)   # 3 — DUPLICATE of t0; triggers Branch 3 + Branch 4

# Duplicate triangle pair — the offending new triangle from retriangulation.
m.assert_duplicate_triangle_pair(t0, t3)

# Edge incidence with the duplicate t3 present (non-manifold state before rollback).
# (v0,v1): t0 + t3 → n=2
m.assert_edge_shared(v0, v1, 2)
# (v0,v2): t0 + t1 + t3 → n=3 (non-manifold)
m.assert_edge_shared(v0, v2, 3)
# (v1,v2): t0 + t3 → n=2 (non-manifold outer edge)
m.assert_edge_shared(v1, v2, 2)

# Clean hub edges from original fan (unchanged by duplicate).
m.assert_edge_shared(v0, v3, 2)   # t1 and t2
m.assert_edge_shared(v0, v4, 1)   # t2 only (open boundary)

# Clean outer edges.
m.assert_edge_shared(v2, v3, 1)   # t1 boundary
m.assert_edge_shared(v3, v4, 1)   # t2 boundary

# Euler: V=5, E=7, F=4 (t0,t1,t2,t3), chi = 5-7+4 = 2
m.assert_euler_characteristic(5, 7, 4, 2)
