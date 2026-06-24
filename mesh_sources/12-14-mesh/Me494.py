"""Me494 — sanitize_candidates recursive_resanitization: after erase, return sanitize_candidates recursively (Branch 5).

CGAL PMP `PMP.internal.sanitize_candidates` Branch 5 (*recursive_resanitization*) @ line 140:
  'candidate_hedges_with_id.erase(candidate_hedges_with_id.begin() + erase_id);
   return sanitize_candidates(candidate_hedges_with_id);'
  — after erasing the incompatible (larger-range) group, sanitize_candidates calls
  itself recursively on the modified list. This recursive call is Branch 5 and fires
  whenever a group is erased (Branch 4 → Branch 5 always follow together).

Defect pattern: a boundary cycle with 4+ coincident vertices arranged so that
  erasing one overlapping group still leaves 2+ groups, requiring another pass
  of sanitize_candidates. Specifically, three coincident vertices at (1,0,0) produce
  overlapping groups A={p0,p1} and B={p1,p2}; after erasing B (or A), one group
  remains. sanitize_candidates recurses and on the second call finds n=1 group —
  which means the outer loop never executes (fr_end = n-1 = 0, so fr_id != fr_end
  is immediately false). But Branch 5 fires because the recursive call itself was
  made. To ensure the recursion is non-trivial (i.e., the recursive call does real
  work), we need at least 3 groups before the first erase, so that after erasing
  one there are still 2+ groups needing another pass.

  Four coincident vertices r0,r1,r2,r3 all at (1,0,0) produce groups
  A={r0,r1}, B={r1,r2}, C={r2,r3} (3 groups, each overlapping the next).
  First pass: erase B (overlaps A at r1 and C at r2) → 2 groups remain {A,C} = {r0,r1} and {r2,r3}.
  Now A=[i,i+1] and C=[i+2,i+3] are disjoint → second pass terminates normally.
  Branch 5 fires because the first erase triggered the recursive call.

Index ranges of coincident groups (before first erase):
  Sorted halfedge positions (within the (1,0,0) run): r0→i, r1→i+1, r2→i+2, r3→i+3.
  Group A: [i, i+1].
  Group B: [i+1, i+2] — overlaps A at i+1.
  Group C: [i+2, i+3] — overlaps B at i+2.
  First pass of sanitize_candidates erases one overlapping group, then recurses
  (Branch 5). Second pass sees 2 disjoint groups → returns true without further erase.

Geometry:
  Five top vertices s0=(0,1,0), s1=(2,1,0), s2=(4,1,0), s3=(6,1,0), s4=(8,1,0);
  four coincident bottom vertices r0=r1=r2=r3=(1,0,0).
  Four cell triangles + three bridge triangles.

  Cell triangles (each uses one coincident bottom vertex):
    t0=(s0,r0,s1), t1=(s1,r1,s2), t2=(s2,r2,s3), t3=(s3,r3,s4).

  Bridge triangles (span top vertices, no bottom vertices):
    t4=(s0,s1,s2), t5=(s0,s2,s3), t6=(s0,s3,s4).

  Interior edges (n=2): (s0,s1),(s1,s2),(s0,s2),(s2,s3),(s0,s3),(s3,s4).
    Wait, (s0,s1) in t0? No — t0=(s0,r0,s1), edges: (s0,r0),(r0,s1),(s0,s1).
    (s0,s1) in t0 and t4 → n=2.
    (s1,s2) in t1 and t4 → n=2.
    (s0,s2) in t4 and t5 → n=2.
    (s2,s3) in t2 and t5 → n=2.
    (s0,s3) in t5 and t6 → n=2.
    (s3,s4) in t3 and t6 → n=2.
  Boundary edges (n=1):
    (s0,r0),(r0,s1) from t0; (s1,r1),(r1,s2) from t1;
    (s2,r2),(r2,s3) from t2; (s3,r3),(r3,s4) from t3;
    (s0,s4) from t6 (outer top span).
  Euler: V=9, E=15, F=7, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me494",
    title="sanitize_candidates recursive_resanitization: four coincident vertices r0==r1==r2==r3 at (1,0,0) create 3 overlapping groups; erase triggers recursive sanitize_candidates call (Branch 5)",
    defect_class="near_coincident_vertex",
)

# Top row — five distinct vertices.
s0 = m.vertex(0.0, 1.0, 0.0)  # 0
s1 = m.vertex(2.0, 1.0, 0.0)  # 1
s2 = m.vertex(4.0, 1.0, 0.0)  # 2
s3 = m.vertex(6.0, 1.0, 0.0)  # 3
s4 = m.vertex(8.0, 1.0, 0.0)  # 4

# Bottom row — four coincident vertices at (1,0,0).
# Sorted positions i, i+1, i+2, i+3 produce groups A=[i,i+1], B=[i+1,i+2], C=[i+2,i+3].
# Groups A&B overlap; B&C overlap. sanitize_candidates erases B and recurses → Branch 5.
r0 = m.vertex(1.0, 0.0, 0.0)  # 5 — coincident with r1, r2, r3
r1 = m.vertex(1.0, 0.0, 0.0)  # 6 — coincident with r0, r2, r3
r2 = m.vertex(1.0, 0.0, 0.0)  # 7 — coincident with r0, r1, r3
r3 = m.vertex(1.0, 0.0, 0.0)  # 8 — coincident with r0, r1, r2

# Four cell triangles — each uses one coincident bottom vertex.
t0 = m.triangle(s0, r0, s1)  # 0: leftmost cell
t1 = m.triangle(s1, r1, s2)  # 1: second cell
t2 = m.triangle(s2, r2, s3)  # 2: third cell
t3 = m.triangle(s3, r3, s4)  # 3: rightmost cell

# Three bridge triangles — span top vertices, no bottom vertices.
t4 = m.triangle(s0, s1, s2)  # 4: left bridge
t5 = m.triangle(s0, s2, s3)  # 5: middle bridge
t6 = m.triangle(s0, s3, s4)  # 6: right bridge

# Interior shared edges (n=2).
m.assert_edge_shared(s0, s1, 2)  # t0 and t4
m.assert_edge_shared(s1, s2, 2)  # t1 and t4
m.assert_edge_shared(s0, s2, 2)  # t4 and t5
m.assert_edge_shared(s2, s3, 2)  # t2 and t5
m.assert_edge_shared(s0, s3, 2)  # t5 and t6
m.assert_edge_shared(s3, s4, 2)  # t3 and t6

# Boundary edges (n=1).
m.assert_edge_shared(s0, r0, 1)  # t0
m.assert_edge_shared(r0, s1, 1)  # t0
m.assert_edge_shared(s1, r1, 1)  # t1
m.assert_edge_shared(r1, s2, 1)  # t1
m.assert_edge_shared(s2, r2, 1)  # t2
m.assert_edge_shared(r2, s3, 1)  # t2
m.assert_edge_shared(s3, r3, 1)  # t3
m.assert_edge_shared(r3, s4, 1)  # t3
m.assert_edge_shared(s0, s4, 1)  # t6 outer top-span

# All four coincident boundary vertices — no two share a triangle.
m.assert_vertex_pair_distance_lt(r0, r1, 1e-9)
m.assert_vertex_pair_distance_lt(r0, r2, 1e-9)
m.assert_vertex_pair_distance_lt(r0, r3, 1e-9)
m.assert_vertex_pair_distance_lt(r1, r2, 1e-9)
m.assert_vertex_pair_distance_lt(r1, r3, 1e-9)
m.assert_vertex_pair_distance_lt(r2, r3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(r0, r1)
m.assert_vertex_pair_no_shared_triangle(r0, r2)
m.assert_vertex_pair_no_shared_triangle(r0, r3)
m.assert_vertex_pair_no_shared_triangle(r1, r2)
m.assert_vertex_pair_no_shared_triangle(r1, r3)
m.assert_vertex_pair_no_shared_triangle(r2, r3)

# Euler: V=9, E=15, F=7, chi=1 (open disk).
m.assert_euler_characteristic(9, 15, 7, 1)
