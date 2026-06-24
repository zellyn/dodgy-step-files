"""Me1094 — non_monotone_border: degenerate CC boundary non-monotone along collapse line (Branch 11).

CGAL PMP.remove_degenerate_faces Branch 11 @ line 2464 — *non-monotone-boundary*:
  'if (non_monotone_border) { /* WARNING: non-monotone border */ all_removed = false; continue; }'
  — after collecting the degenerate connected component and its boundary halfedges,
  CGAL checks that the boundary vertex projections onto the collapse line are
  monotonically ordered. If they are NOT monotone the component is skipped.

Defect pattern: four collinear vertices v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(3,0,0).
  Three zero-area triangles: t0=(v0,v1,v2), t1=(v0,v3,v2), t2=(v0,v1,v3).
  The three form a connected component. Their combined boundary edges are those
  appearing in exactly one face:
    - (v0,v2) appears in t0 and t1: INTERIOR (shared by 2 faces)
    - (v0,v1) appears in t0 and t2: INTERIOR
    - (v1,v3) appears in t2 only: outer boundary
    - (v2,v3) appears in t1 only: outer boundary
    - (v1,v2) appears in t0 only: outer boundary
    - (v0,v3) appears in t1 and t2: INTERIOR (wait, only t2=(v0,v1,v3) has (v0,v3))
  Correction: t1=(v0,v3,v2) edges: (v0,v3),(v3,v2),(v0,v2). t2=(v0,v1,v3) edges: (v0,v1),(v1,v3),(v0,v3).
  So (v0,v3) is in BOTH t1 and t2 — interior; boundary = {(v1,v2),(v2,v3),(v1,v3)} — WAIT:
  (v1,v2) in t0 only, (v2,v3) in t1 only (same as (v3,v2)), (v1,v3) in t2 only.
  Boundary projection sequence on X: v1=1, v2=2, v3=3.
  Walking boundary from v1: v1→v2 (proj 1→2), v2→v3 (proj 2→3), v3→v1 (proj 3→1 — reversal!).
  The 3→1 step is non-monotone. This is the non_monotone_border condition.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1094",
             title="non-monotone boundary: degenerate CC boundary reverses along line — skip removal",
             defect_class="degenerate_triangle")

# Four collinear vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 0.0, 0.0)   # 3

# Three degenerate triangles forming a connected CC whose boundary is non-monotone.
t0 = m.triangle(v0, v1, v2)   # face 0: zero area; edges (v0,v1),(v1,v2),(v0,v2)
t1 = m.triangle(v0, v3, v2)   # face 1: zero area; edges (v0,v3),(v2,v3),(v0,v2)
t2 = m.triangle(v0, v1, v3)   # face 2: zero area; edges (v0,v1),(v1,v3),(v0,v3)

# Assert all three degenerate faces have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)

# Interior edges of the CC (shared by 2 faces).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t2
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Outer boundary edges of the CC (shared by only 1 face each).
# Boundary vertices projected to X: v1=1, v2=2, v3=3.
# Boundary traversal visits v1→v2→v3→v1: the step v3→v1 reverses (3→1), non-monotone.
m.assert_edge_shared(v1, v2, 1)   # boundary: t0 only
m.assert_edge_shared(v2, v3, 1)   # boundary: t1 only
m.assert_edge_shared(v1, v3, 1)   # boundary: t2 only
