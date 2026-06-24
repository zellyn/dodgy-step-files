"""Me912 — di_cell.selectIntersections info-list-initialization: t->info != NULL reuse vs new List; hub triangle intersects two others (Branch 3).

MeshFix `di_cell.selectIntersections` Branch 3 (*Info-list initialization*) @ line 124:
  'if (t->info == NULL) t->info = new List; t->info->appendHead(s);'
  — when recording that triangle t intersects triangle s, the code first checks
  whether t already has an info list attached. If t->info == NULL (first SI partner
  recorded for this triangle), a new List is allocated. If t->info != NULL (the
  triangle already has at least one recorded SI partner from a prior cell iteration),
  the existing list is reused and s is appended. Branch 3 fires on the NULL→allocate
  path; the reuse path fires on subsequent partners.

Defect pattern: a central "hub" triangle t0 that crosses two other triangles (t1 and
  t2). When di_cell.selectIntersections processes the first SI partner (t1), it finds
  t0->info == NULL → allocates a new List (Branch 3, allocation path). When it
  subsequently processes the second SI partner (t2), it finds t0->info != NULL →
  reuses the existing list (Branch 3, reuse path). Both paths of this branch are
  exercised.

Geometry:
  t0: flat horizontal triangle in XY plane at z=0 — the hub.
  t1: near-vertical triangle whose edge pierces t0 on the left side.
  t2: near-vertical triangle whose edge pierces t0 on the right side.
  All three triangles have disjoint vertex sets.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me912",
    title="di_cell.selectIntersections info-list-init: hub t0 intersects t1 (NULL→new List) then t2 (reuse list); both info-list paths exercised (Branch 3)",
    defect_class="self_intersection_face_pair",
)

# Hub triangle t0: large triangle in XY plane at z=0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(4.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 4.0, 0.0)   # 2

# t1: near-vertical crossing t0's left half; edge (v3,v4) pierces t0 at (1,1,0).
v3 = m.vertex(1.0, 1.0,-1.0)   # 3
v4 = m.vertex(1.0, 1.0, 1.0)   # 4
v5 = m.vertex(-1.0, 3.0, 0.0)  # 5

# t2: near-vertical crossing t0's right half; edge (v6,v7) pierces t0 at (3,1,0).
v6 = m.vertex(3.0, 1.0,-1.0)   # 6
v7 = m.vertex(3.0, 1.0, 1.0)   # 7
v8 = m.vertex(5.0, 3.0, 0.0)   # 8

t0 = m.triangle(v0, v1, v2)    # 0: hub triangle in XY plane
t1 = m.triangle(v3, v4, v5)    # 1: first crossing — NULL → new List (Branch 3 init)
t2 = m.triangle(v6, v7, v8)    # 2: second crossing — reuse list (Branch 3 reuse)

# No shared vertices between any pair.
m.assert_vertex_pair_no_shared_triangle(v0, v3)  # t0 and t1 disjoint vertices
m.assert_vertex_pair_no_shared_triangle(v0, v6)  # t0 and t2 disjoint vertices
m.assert_vertex_pair_no_shared_triangle(v3, v6)  # t1 and t2 disjoint vertices

# t0 crosses t1: edge (v3,v4) passes through t0's interior at (1,1,0).
m.assert_triangles_self_intersect(t0, t1)

# t0 crosses t2: edge (v6,v7) passes through t0's interior at (3,1,0).
# This is the second SI partner for t0 → t0->info != NULL → reuse list.
m.assert_triangles_self_intersect(t0, t2)
