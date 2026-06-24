"""Me671 — checkAndRepair::mergeCoincidentEdges branch 2: VERTEX_DUPLICATION_AT_V1.

MeshFix `checkAndRepair::mergeCoincidentEdges` Branch 2 (*VERTEX_DUPLICATION_AT_V1*) @ line 281:
  'if (e->v1->info != e->v1)' — for each boundary edge, after BIT-5 tagging,
  the algorithm checks whether edge endpoint v1 has already been assigned a
  representative vertex different from itself (i.e. v1 was part of a coincident
  pair and e->v1->info was redirected to the canonical representative). If so,
  the edge's v1 pointer is updated to the canonical representative. Branch 2
  fires precisely when v1 carries a non-self info pointer.

Defect pattern: two triangle patches whose shared boundary has two vertex pairs
  at exactly coincident coordinates. Patch A uses vertices a0, a1, a2 and patch B
  uses b0, b1, b2 where a1 and b1 occupy the same point. After coincident-vertex
  detection runs, a1->info is redirected to b1 (or vice versa). The boundary edge
  from a0 to a1 then has v1 = a1 with a1->info != a1, triggering Branch 2.

Geometry:
  a0 = (0, 0, 0)
  a1 = (1, 0, 0)  — coincident with b0
  a2 = (0.5, 1, 0)
  b0 = (1, 0, 0)  — coincident with a1
  b1 = (2, 0, 0)
  b2 = (1.5, 1, 0)
  t0 = (a0, a1, a2)  — left patch triangle
  t1 = (b0, b1, b2)  — right patch triangle
  Boundary edge (a0->a1) has v1=a1; after info redirect a1->info=b0 (same coords) →
  Branch 2: e->v1->info != e->v1, so v1 is replaced by its representative.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me671",
    title="mergeCoincidentEdges VERTEX_DUPLICATION_AT_V1: boundary edge v1 has non-self info pointer (a1 coincident with b0); redirect to canonical representative (Branch 2)",
    defect_class="near_coincident_vertex",
)

a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left triangle left-bottom
a1 = m.vertex(1.0, 0.0, 0.0)   # 1 — coincident with b0; will get a1->info = b0
a2 = m.vertex(0.5, 1.0, 0.0)   # 2 — left triangle apex
b0 = m.vertex(1.0, 0.0, 0.0)   # 3 — coincident with a1; canonical representative
b1 = m.vertex(2.0, 0.0, 0.0)   # 4 — right triangle right-bottom
b2 = m.vertex(1.5, 1.0, 0.0)   # 5 — right triangle apex

t0 = m.triangle(a0, a1, a2)    # 0 — left patch
t1 = m.triangle(b0, b1, b2)    # 1 — right patch

# Boundary edges: all n=1 (no edge is shared between t0 and t1 in raw topology).
m.assert_edge_shared(a0, a1, 1)
m.assert_edge_shared(a1, a2, 1)
m.assert_edge_shared(a0, a2, 1)
m.assert_edge_shared(b0, b1, 1)
m.assert_edge_shared(b1, b2, 1)
m.assert_edge_shared(b0, b2, 1)

# Coincident vertex pair (a1, b0): same coordinates (1,0,0); Branch 2 fires
# when the boundary edge whose v1 == a1 is scanned and a1->info != a1.
m.assert_vertex_pair_distance_lt(a1, b0, 1e-9)
m.assert_vertex_pair_no_shared_triangle(a1, b0)

# Euler: V=6, E=6, F=2, chi=2 (two disjoint open disks).
m.assert_euler_characteristic(6, 6, 2, 2)
