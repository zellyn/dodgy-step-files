"""Me554 — checkAndRepair::rebuildConnectivity DEGENERATE_TRIANGLE_DUPLICATE_VERTEX: triangle vertices not pairwise distinct; collapsed triangle discarded (Branch 5).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 5 (*DEGENERATE_TRIANGLE_DUPLICATE_VERTEX*) @ line 376:
  'if (v1!=v2 && v2!=v3 && v1!=v3) { …add triangle… } else { …skip… }'
  — after the vertex info-pointer unification pass, each stored triangle is
  re-examined. If any two of its three resolved vertex pointers are the same
  (e.g., v1==v2 because two formerly distinct indices now point to the same
  canonical vertex), the triangle is degenerate and is silently dropped rather
  than added to the rebuilt mesh → Branch 5 fires (the else clause).

Defect pattern: two valid triangles plus one collapsed/degenerate triangle
  whose first two vertices (r0 and r2) share the same coordinates (0,0,0)
  but are stored as distinct indices. After unification r2->info = r0, so
  both resolve to r0 → v1==v2 in the collapsed triangle → Branch 5 fires.

Geometry:
  r0=(0,0,0), r1=(2,0,0), r2=(0,0,0) [coincident with r0], r3=(1,2,0), r4=(3,2,0)
  t0=(r0,r1,r3): normal triangle (left)
  t1=(r1,r4,r3): normal triangle (right)
  t2=(r0,r2,r3): collapsed (r0==r2 at (0,0,0)) — v1==v2 after unification → discarded
  The collapsed triangle t2 has zero area; its first two vertices are at the same point.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me554",
    title="checkAndRepair::rebuildConnectivity DEGENERATE_TRIANGLE_DUPLICATE_VERTEX: t2=(r0,r2,r3) with r0==r2 at (0,0,0); v1==v2 after unification; triangle discarded (Branch 5)",
    defect_class="degenerate_triangle",
)

r0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base; canonical representative
r1 = m.vertex(2.0, 0.0, 0.0)  # 1 — right base (distinct)
r2 = m.vertex(0.0, 0.0, 0.0)  # 2 — coincident with r0 at (0,0,0); info->r0 after pass
r3 = m.vertex(1.0, 2.0, 0.0)  # 3 — upper-left apex (distinct)
r4 = m.vertex(3.0, 2.0, 0.0)  # 4 — upper-right apex (distinct)

# Two valid triangles.
t0 = m.triangle(r0, r1, r3)  # 0: left triangle (all distinct corners)
t1 = m.triangle(r1, r4, r3)  # 1: right triangle (all distinct corners)

# Degenerate collapsed triangle: r0 == r2 coordinates (v1==v2 after unification).
t2 = m.triangle(r0, r2, r3)  # 2: collapsed — v1(r0)==v2(r2) → Branch 5 discards it

# Shared edge between valid triangles (r1, r3) — n=2.
m.assert_edge_shared(r1, r3, 2)

# Boundary edges of valid triangles — n=1.
m.assert_edge_shared(r0, r1, 1)   # t0 bottom
# Note: edge (r0,r3) appears in both t0 AND the degenerate t2=(r0,r2,r3),
# so it is shared n=2 in the raw mesh (before rebuildConnectivity discards t2).
m.assert_edge_shared(r0, r3, 2)   # shared by t0 and degenerate t2
m.assert_edge_shared(r1, r4, 1)   # t1 right
m.assert_edge_shared(r3, r4, 1)   # t1 top

# Degenerate t2: r0 and r2 at same coordinates → triangle area is zero.
m.assert_triangle_area_lt(t2, 1e-9)

# r0 and r2 are coincident — after unification r2->info=r0, so v1==v2 in t2.
m.assert_vertex_pair_distance_lt(r0, r2, 1e-9)
