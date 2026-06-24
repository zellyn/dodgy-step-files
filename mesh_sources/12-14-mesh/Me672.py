"""Me672 — checkAndRepair::mergeCoincidentEdges branch 3: VERTEX_DUPLICATION_AT_V2.

MeshFix `checkAndRepair::mergeCoincidentEdges` Branch 3 (*VERTEX_DUPLICATION_AT_V2*) @ line 282:
  'if (e->v2->info != e->v2)' — analogous to Branch 2 but for the *second*
  endpoint of the boundary edge. When v2 carries a non-self info pointer (i.e.
  v2 was found coincident with another vertex and its info was redirected to the
  canonical representative), Branch 3 fires and the edge's v2 is updated to
  the canonical vertex.

Defect pattern: two triangle patches sharing a stitchable boundary where the
  "start" vertex of the shared boundary is the coincident one. Patch A's
  boundary edge is oriented so that the coincident vertex is v2 (the edge
  destination). After coincident-vertex detection, v2->info != v2, triggering
  Branch 3.

Geometry:
  p0 = (0, 0, 0)
  p1 = (1, 0, 0)
  p2 = (0.5, 1, 0)
  q0 = (2, 0, 0)
  q1 = (1, 0, 0)  — coincident with p1
  q2 = (1.5, 1, 0)
  t0 = (p0, p1, p2)  — left patch; boundary edge (p0->p1) has v2=p1
  t1 = (q0, q1, q2)  — right patch; q1 coincident with p1
  After info redirect q1->info=p1 (canonical), the boundary edge scanning p2->p1
  as v2=p1 will also find a redirect case. The distinct case here is that the
  *v2* endpoint is the coincident one (vs Branch 2 where v1 is coincident).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me672",
    title="mergeCoincidentEdges VERTEX_DUPLICATION_AT_V2: boundary edge v2 has non-self info pointer (p1 coincident with q1); redirect to canonical representative (Branch 3)",
    defect_class="near_coincident_vertex",
)

p0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left triangle left corner
p1 = m.vertex(1.0, 0.0, 0.0)   # 1 — stitchable boundary vertex (canonical)
p2 = m.vertex(0.5, 1.0, 0.0)   # 2 — left triangle apex
q0 = m.vertex(2.0, 0.0, 0.0)   # 3 — right triangle right corner
q1 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident with p1; q1->info = p1
q2 = m.vertex(1.5, 1.0, 0.0)   # 5 — right triangle apex

t0 = m.triangle(p0, p1, p2)    # 0 — left patch (boundary edge p2->p0 has v2=p0)
t1 = m.triangle(q0, q1, q2)    # 1 — right patch

# Boundary edges: all n=1.
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p1, p2, 1)
m.assert_edge_shared(p0, p2, 1)
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q1, q2, 1)
m.assert_edge_shared(q0, q2, 1)

# Coincident vertex pair (p1, q1): same coordinates (1,0,0); Branch 3 fires
# when a boundary edge whose v2 == q1 is scanned and q1->info != q1.
m.assert_vertex_pair_distance_lt(p1, q1, 1e-9)
m.assert_vertex_pair_no_shared_triangle(p1, q1)

# Euler: V=6, E=6, F=2, chi=2 (two disjoint open disks).
m.assert_euler_characteristic(6, 6, 2, 2)
