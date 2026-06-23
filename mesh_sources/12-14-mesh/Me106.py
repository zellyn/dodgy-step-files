"""Me106 — unlink_triangle_isolated_edge_pair_v1: both edges e1 and e2 incident
on v1 in the target triangle become isolated after the triangle is unlinked,
making v1 an orphaned (isolated) vertex.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 7 (*isolated_edge_pair_v1*):
'if (e1->isIsolated() && e2->isIsolated())' — e1 and e2 are the two edges of
the target triangle incident on v1. After the triangle is unlinked, if both
edges are isolated (no remaining triangles reference them), then v1 is no longer
connected to anything. The branch sets v1->e0 = NULL to mark v1 as an orphan.

For Branch 7 to fire: v1 must appear in the target triangle ONLY — no other
triangle shares either of v1's two edges. This means v1 has degree 1 (it is in
only one triangle — the target).

Geometry:
  A single triangle (the target) whose first vertex v0 is unique to that triangle.
  Three surrounding triangles fill in to make a valid mesh context, but v0 is
  only referenced by the target.

  v0=(1,0,0)  — first vertex (v1 in MeshFix) of target t0; in t0 only
  v1=(0,0,0), v2=(2,0,0), v3=(1,1,0)  — other vertices
  v4=(0,2,0), v5=(2,2,0)  — upper outer vertices

  t0 = (v0, v1, v2)   ← target; v0 is in t0 only → both its edges isolated after unlink
  t1 = (v1, v3, v2)   — shares no edge with t0 that involves v0
  t2 = (v1, v4, v3)   — fills upper-left
  t3 = (v3, v5, v2)   — fills upper-right

  Edges at v0 in t0:
    (v0,v1) — in t0 only → isolated after unlink
    (v0,v2) — in t0 only → isolated after unlink
  → Branch 7 fires: both e1 and e2 at v1 (=v0 here) are isolated.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me106",
             title="unlink_triangle_isolated_edge_pair_v1: v1's both incident edges isolated, v1 becomes orphan",
             defect_class="unlink_isolated_edge_pair_v1")

v0 = m.vertex(1.0, 0.0, 0.0)   # 0 — v1 in MeshFix target; in t0 only
v1 = m.vertex(0.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.0, 2.0, 0.0)   # 4
v5 = m.vertex(2.0, 2.0, 0.0)   # 5

# Target triangle; v0 is the first vertex (in t0 only → will become isolated).
t0 = m.triangle(v0, v1, v2)    # 0 — target

# Adjacent triangles sharing only the edge (v1,v2) — not involving v0.
t1 = m.triangle(v1, v3, v2)    # 1 — shares edge (v1,v2) but NOT v0
t2 = m.triangle(v1, v4, v3)    # 2
t3 = m.triangle(v3, v5, v2)    # 3

# Both edges incident on v0 in t0 are in t0 only → will be isolated after unlink.
m.assert_edge_shared(v0, v1, 1)   # boundary: in t0 only
m.assert_edge_shared(v0, v2, 1)   # boundary: in t0 only

# The edge (v1,v2) is shared: it connects t0 with t1 (so v1 and v2 are NOT isolated).
m.assert_edge_shared(v1, v2, 2)   # interior: shared by t0 and t1

# After t0 is removed, v0 is unreferenced → v0 becomes isolated.
# We assert v0 is NOT isolated now (it is in t0), and that v0 is the sole
# reference-point for the defect.  We cannot assert v0 is isolated in the
# pre-removal mesh, so instead we confirm t0's unique vertex ownership:
# both (v0,v1) and (v0,v2) have exactly 1 triangle → Branch 7 condition met.
m.assert_edge_shared(v1, v3, 2)   # interior: shared by t1 and t2
m.assert_edge_shared(v2, v3, 2)   # interior: shared by t1 and t3
