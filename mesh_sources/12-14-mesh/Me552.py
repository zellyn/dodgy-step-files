"""Me552 — checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V1: e->v1 aliased through info chain (Branch 3).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 3 (*VERTEX_POINTER_INDIRECTION_V1*) @ line 347:
  'if (e->v1->info != e->v1) e->v1 = e->v1->info;'
  — after the info-pointer unification pass (Branch 2), every edge is
  revisited. If an edge's v1 endpoint still has its info pointer pointing
  elsewhere (meaning v1 was identified as a duplicate of some other vertex
  during the sort pass), v1 is updated to the canonical representative.
  This fires when e->v1 is NOT the canonical vertex — Branch 3 fires.

Defect pattern: three triangles (fan from apex). Two boundary vertices
  p1 and p3 share the same coordinates (2.0,0.0,0.0); p2 (the middle one)
  is between them in the sorted order and serves as the canonical
  representative via an info-chain step. After the Branch 2 pass:
    p3->info = p1 (both at (2,0,0))
  Then in the edge scan, any edge referencing p3 as v1 detects
  e->v1->info != e->v1 (since p3->info = p1 ≠ p3) → Branch 3 fires.

Geometry:
  p0=(0,0,0), p1=(2,0,0), p2=(1,2,0), p3=(2,0,0) [coincident with p1], p4=(0,2,0)
  t0=(p0,p1,p2), t1=(p0,p2,p3), t2=(p0,p2,p4)
  Interior edge (p0,p2) shared by all three triangles (n=3).
  p1 and p3 both at (2,0,0) — edge t1's v-endpoint p3 has p3->info=p1 after
  the unification pass, so that edge's v1 field triggers indirection (Branch 3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me552",
    title="checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V1: e->v1 for p3 (=p1 at (2,0,0)) has info!=self after unification; v1 dereferenced to canonical (Branch 3)",
    defect_class="near_coincident_vertex",
)

p0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base
p1 = m.vertex(2.0, 0.0, 0.0)  # 1 — boundary at (2,0,0); canonical representative
p2 = m.vertex(1.0, 2.0, 0.0)  # 2 — apex (hub)
p3 = m.vertex(2.0, 0.0, 0.0)  # 3 — boundary at (2,0,0); coincident with p1; info->p1
p4 = m.vertex(0.0, 2.0, 0.0)  # 4 — upper left (distinct)

# Three triangles fanned from the hub edge (p0, p2).
t0 = m.triangle(p0, p1, p2)  # 0: right sector [p1 on boundary]
t1 = m.triangle(p0, p2, p3)  # 1: middle sector [p3->info=p1, e->v1 indirection fires]
t2 = m.triangle(p0, p4, p2)  # 2: left sector [distinct vertices]

# Interior shared edge (p0, p2) — shared by all three triangles, n=3.
m.assert_edge_shared(p0, p2, 3)

# Boundary edges — n=1 each.
m.assert_edge_shared(p0, p1, 1)  # t0 bottom
m.assert_edge_shared(p1, p2, 1)  # t0 right
m.assert_edge_shared(p2, p3, 1)  # t1 right
m.assert_edge_shared(p0, p3, 1)  # t1 bottom (p3 coincident with p1)
m.assert_edge_shared(p0, p4, 1)  # t2 left
m.assert_edge_shared(p2, p4, 1)  # t2 upper-left

# p1 and p3 are geometrically identical — after Branch 2: p3->info = p1.
# Any edge with p3 as v1 fires Branch 3 (e->v1->info != e->v1).
m.assert_vertex_pair_distance_lt(p1, p3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(p1, p3)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
# Edges: 1 interior (p0,p2) + 6 boundary = 7. V-E+F = 5-7+3 = 1.
m.assert_euler_characteristic(5, 7, 3, 1)
