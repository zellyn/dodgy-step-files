"""Me553 — checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V2: e->v2 aliased through info chain (Branch 4).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 4 (*VERTEX_POINTER_INDIRECTION_V2*) @ line 348:
  'if (e->v2->info != e->v2) e->v2 = e->v2->info;'
  — symmetric to Branch 3 but applied to the second endpoint of each edge.
  After the info-pointer unification pass (Branch 2), if an edge's v2 has its
  info pointer pointing to the canonical representative (meaning v2 was
  recognized as a duplicate during the sort pass), v2 is updated to that
  canonical vertex → Branch 4 fires.

Defect pattern: three triangles fanned around a central hub vertex. Two
  boundary vertices q1 and q3 share identical coordinates (3.0,0.0,0.0)
  but are topologically distinct. After the sorted-walk Branch 2 pass:
    q3->info = q1
  Then in the edge scan, any edge referencing q3 as v2 detects
  e->v2->info != e->v2 (since q3->info = q1 ≠ q3) → Branch 4 fires.
  The two coincident vertices are each in exactly one triangle with no
  shared triangle between them.

Geometry:
  q0=(0,0,0), q1=(3,0,0), q2=(1.5,2,0), q3=(3,0,0) [coincident with q1], q4=(0,3,0)
  t0=(q0,q1,q2): right sector, q1 on boundary
  t1=(q2,q3,q0): middle sector, q3 (coincident with q1) on boundary as v2-endpoint
  t2=(q0,q2,q4): left sector, all distinct vertices
  Interior edge (q0,q2) shared by all three triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me553",
    title="checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V2: e->v2 for q3 (=q1 at (3,0,0)) has info!=self after unification; v2 dereferenced to canonical (Branch 4)",
    defect_class="near_coincident_vertex",
)

q0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base (hub base)
q1 = m.vertex(3.0, 0.0, 0.0)  # 1 — boundary at (3,0,0); canonical representative
q2 = m.vertex(1.5, 2.0, 0.0)  # 2 — upper apex (hub)
q3 = m.vertex(3.0, 0.0, 0.0)  # 3 — boundary at (3,0,0); coincident with q1; info->q1
q4 = m.vertex(0.0, 3.0, 0.0)  # 4 — upper left (distinct)

# Three triangles sharing interior hub edge (q0, q2).
t0 = m.triangle(q0, q1, q2)  # 0: right sector [q1 as v2 of edge (q0,q1)]
t1 = m.triangle(q2, q3, q0)  # 1: middle sector [q3 as v2 of edge (q2,q3) — Branch 4]
t2 = m.triangle(q0, q2, q4)  # 2: left sector [all distinct]

# Interior shared edge (q0, q2) — shared by all three triangles, n=3.
m.assert_edge_shared(q0, q2, 3)

# Boundary edges — n=1 each.
m.assert_edge_shared(q0, q1, 1)  # t0 bottom
m.assert_edge_shared(q1, q2, 1)  # t0 right
m.assert_edge_shared(q2, q3, 1)  # t1 right (q3 coincident with q1)
m.assert_edge_shared(q0, q3, 1)  # t1 bottom
m.assert_edge_shared(q0, q4, 1)  # t2 left
m.assert_edge_shared(q2, q4, 1)  # t2 upper-left

# q1 and q3 are geometrically identical — after Branch 2: q3->info = q1.
# Any edge with q3 as v2 fires Branch 4 (e->v2->info != e->v2).
m.assert_vertex_pair_distance_lt(q1, q3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(q1, q3)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
# 1 interior edge (q0,q2) + 6 boundary edges = 7. V-E+F = 5-7+3 = 1.
m.assert_euler_characteristic(5, 7, 3, 1)
