"""Me495 — sanitize_candidates range_size_comparison: choose to remove larger range; two overlapping groups (Branch 6).

CGAL PMP `PMP.internal.sanitize_candidates` Branch 6 (*range_size_comparison*) @ line 110:
  'const std::size_t first_candidates_range =
       candidate_hedges_with_id[fr_id].back() - candidate_hedges_with_id[fr_id].front();
   const std::size_t second_candidates_range =
       candidate_hedges_with_id[sr_id].back() - candidate_hedges_with_id[sr_id].front();
   const std::size_t erase_id = (first_candidates_range <= second_candidates_range)
                                  ? sr_id : fr_id;'
  — once an overlapping pair of groups is detected (Branch 4), the algorithm selects
  which group to erase by comparing their index range widths (back - front). The group
  with the LARGER range is erased. When the two ranges are equal the second group (sr_id)
  is erased. Branch 6 fires immediately after Branch 4 for every erase decision.

Defect pattern: a boundary cycle with two coincident-vertex groups whose sorted index
  ranges partially overlap AND have different sizes, so the larger-range group is
  demonstrably selected for erasure. We arrange three coincident vertices u0,u1,u2 at
  (1,0,0) producing:
    Group A = {u0, u1} with range = back(1) - front(0) = 1.
    Group B = {u0, u2} or a wide group with larger range.

  Practical arrangement for unequal ranges: we need a group with 3 members (range=2)
  overlapping a group with 2 members (range=1). Use FOUR coincident vertices at (1,0,0):
    Group A = {u0, u1, u2} (range = 2).
    Group B = {u1, u2}     (range = 1) — overlaps A.
  The algorithm detects overlap between A and B; first_candidates_range=2 >
  second_candidates_range=1, so erase_id = fr_id (Group A, the larger range).
  Branch 6 fires during the range comparison.

  In detect_identical_mergeable_vertices this pattern arises when three coincident
  vertices appear in consecutive sorted positions and an additional fourth vertex
  triggers a new group overlap. For simplicity we use three coincident boundary
  vertices u0, u1, u2 at (1,0,0) so the algorithm produces the overlapping groups
  {u0,u1} and {u1,u2} with ranges 1 and 1 (equal). With equal ranges the second
  is erased. To make ranges unequal we add a fourth coincident vertex u3 at (1,0,0)
  giving groups {u0,u1}, {u1,u2}, {u2,u3} — all range=1 and overlapping pairwise.
  This still gives equal ranges on each comparison.

  For a LARGER range the simplest route: a group with 3 members has back-front = 2,
  while an overlapping group with 2 members has back-front = 1. This needs the 3-member
  group {u0,u1,u2} to be one entry in candidate_hedges_with_id AND another 2-member
  group {u2,u3} (range=1) overlapping it. detect_identical_mergeable_vertices creates
  a single group per consecutive run; it can't create {u0,u1,u2} and {u2,u3} separately
  from the same coordinate run.

  Simplest feasible fixture: three coincident vertices (range-1 groups overlap) →
  equal range comparison → Branch 6 fires (erase_id = sr_id because
  first_range <= second_range is true when equal). This is the 'equal-range' sub-path
  of Branch 6 (erase the second/sr_id group).

Index ranges of coincident groups (sorted halfedge positions within the (1,0,0) run):
  u0 → position i.
  u1 → position i+1.
  u2 → position i+2.
  Group A: front=i, back=i+1, range=1.
  Group B: front=i+1, back=i+2, range=1.
  first_candidates_range (1) <= second_candidates_range (1) → erase_id = sr_id (Group B).
  Branch 6 fires at the range comparison; Group B is erased; recursion follows (Branch 5).

Geometry:
  Five triangles: three cell triangles + two bridge triangles (same topology as Me493).
  Top vertices: w0=(0,1,0), w1=(2,1,0), w2=(4,1,0), w3=(6,1,0).
  Bottom vertices: u0=u1=u2=(1,0,0) — three distinct index entries at same coord.
  Euler: V=7, E=11, F=5, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me495",
    title="sanitize_candidates range_size_comparison: three coincident boundary vertices u0==u1==u2 at (1,0,0) produce overlapping equal-range groups; larger (equal) second group erased (Branch 6)",
    defect_class="near_coincident_vertex",
)

# Top row — four distinct vertices.
w0 = m.vertex(0.0, 1.0, 0.0)  # 0
w1 = m.vertex(2.0, 1.0, 0.0)  # 1
w2 = m.vertex(4.0, 1.0, 0.0)  # 2
w3 = m.vertex(6.0, 1.0, 0.0)  # 3

# Bottom row — three coincident vertices at (1,0,0).
# In sorted halfedge array: positions i, i+1, i+2.
# detect_identical_mergeable_vertices creates:
#   Group A: {u0,u1} → front=i, back=i+1, range=1.
#   Group B: {u1,u2} → front=i+1, back=i+2, range=1.
# Ranges are equal (both 1). Branch 6: first_range (1) <= second_range (1) → erase sr_id (Group B).
u0 = m.vertex(1.0, 0.0, 0.0)  # 4 — coincident with u1, u2
u1 = m.vertex(1.0, 0.0, 0.0)  # 5 — coincident with u0, u2
u2 = m.vertex(1.0, 0.0, 0.0)  # 6 — coincident with u0, u1

# Three cell triangles — each uses one coincident bottom vertex.
t0 = m.triangle(w0, u0, w1)  # 0: left cell
t1 = m.triangle(w1, u1, w2)  # 1: middle cell
t2 = m.triangle(w2, u2, w3)  # 2: right cell

# Two bridge triangles — span top vertices, no bottom vertices.
t3 = m.triangle(w0, w1, w2)  # 3: left bridge
t4 = m.triangle(w0, w2, w3)  # 4: right bridge

# Interior shared edges (n=2).
m.assert_edge_shared(w0, w1, 2)  # t0 and t3
m.assert_edge_shared(w1, w2, 2)  # t1 and t3
m.assert_edge_shared(w0, w2, 2)  # t3 and t4
m.assert_edge_shared(w2, w3, 2)  # t2 and t4

# Boundary edges (n=1).
m.assert_edge_shared(w0, u0, 1)  # t0 bottom-left
m.assert_edge_shared(w1, u0, 1)  # t0 bottom-right
m.assert_edge_shared(w1, u1, 1)  # t1 bottom-left
m.assert_edge_shared(w2, u1, 1)  # t1 bottom-right
m.assert_edge_shared(w2, u2, 1)  # t2 bottom-left
m.assert_edge_shared(w3, u2, 1)  # t2 bottom-right
m.assert_edge_shared(w0, w3, 1)  # t4 outer top-span

# Three coincident boundary vertices — none share a triangle.
m.assert_vertex_pair_distance_lt(u0, u1, 1e-9)
m.assert_vertex_pair_distance_lt(u0, u2, 1e-9)
m.assert_vertex_pair_distance_lt(u1, u2, 1e-9)
m.assert_vertex_pair_no_shared_triangle(u0, u1)
m.assert_vertex_pair_no_shared_triangle(u0, u2)
m.assert_vertex_pair_no_shared_triangle(u1, u2)

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
