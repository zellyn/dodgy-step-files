"""Me405 — detect_identical_mergeable_vertices interval_sanitation: two overlapping candidate groups in the same cycle, sanitize_candidates drops one (Branch 6).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 6 (*interval_sanitation*) @ line 196:
  'if(!sanitize_candidates(candidate_hedges_with_id)) continue;'
  — after collecting all candidate groups for a boundary cycle, if any two groups have
  overlapping halfedge index intervals, sanitize_candidates is called to resolve the
  conflict. The condition check and call constitute Branch 6. Two separate duplicate-
  vertex groups within the same cycle trigger this branch.

Defect pattern: a polygon mesh whose single boundary cycle contains TWO separate
  groups of coincident vertices: group A (c1,c3 at (1,0,0)) and group B (c2,c4 at
  (2,0,0)). In the sorted halfedge array the two groups may have index ranges that
  overlap, requiring sanitize_candidates to determine which group to keep. Branch 6
  fires when the candidate count exceeds 1 and overlap is detected.

Geometry:
  c0=(0,0,0), c1=(1,0,0), c2=(2,0,0), c3=(3,0,0), c4=(1,0,0) [=c1], c5=(2,0,0) [=c2]
  Five triangles forming a hexagonal open strip, boundary cycle visits c0,c1,c2,c3,c4,c5.
  Group A: c1 and c4 at (1,0,0). Group B: c2 and c5 at (2,0,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me405",
    title="detect_identical_mergeable_vertices interval_sanitation: two coincident groups (c1==c4 at (1,0,0), c2==c5 at (2,0,0)) in same boundary cycle; sanitize_candidates invoked (Branch 6)",
    defect_class="near_coincident_vertex",
)

# Build a mesh with a single boundary cycle and two coincidence groups.
# Hub vertex c0 from which a fan of triangles radiates.
# Boundary cycle will visit: c1(1,0,0), c2(2,0,0), c3(3,0,0), c4(1,0,0), c5(2,0,0)
# plus the hub c0 itself.

c0 = m.vertex(0.0, 0.0, 0.0)  # 0 — fan hub (distinct)
c1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary Group A (1,0,0)
c2 = m.vertex(2.0, 0.0, 0.0)  # 2 — boundary Group B (2,0,0)
c3 = m.vertex(3.0, 0.0, 0.0)  # 3 — boundary distinct
c4 = m.vertex(1.0, 0.0, 0.0)  # 4 — boundary Group A (1,0,0), coincident with c1
c5 = m.vertex(2.0, 0.0, 0.0)  # 5 — boundary Group B (2,0,0), coincident with c2
c6 = m.vertex(1.5, 2.0, 0.0)  # 6 — top apex (distinct)

# Five triangles forming a closed fan from c0 through c6.
# The fan shares interior edges; boundary cycle is the outer rim.
# t0=(c0,c1,c6): sector 1
# t1=(c0,c6,c2): sector 2 [shares (c0,c6) with t0]
# t2=(c0,c2,c3): sector 3 [shares (c0,c2)... wait, (c0,c2) must be shared]
# Let me use a strip instead.
# Strip: t0=(c0,c1,c6), t1=(c1,c2,c6) [shares (c1,c6)], t2=(c2,c3,c6) [shares (c2,c6)],
#         t3=(c3,c4,c6) [shares (c3,c6)], t4=(c4,c5,c6) [shares (c4,c6)]
# Plus one more to close the fan back to c0:
#  t5=(c5,c0,c6) [shares (c5,c6)] — but (c0,c6) must be boundary or shared with t0.
#  (c0,c6) in t0 and t5 → n=2 interior.
# Boundary: bottom row of spokes.
# Bottom boundary edges: (c0,c1),(c1,c2),(c2,c3),(c3,c4),(c4,c5),(c5,c0).
# Top boundary: none (all (c_i,c6) edges shared by adjacent triangles).
# Actually (c1,c6) appears in t0 and t1 → n=2. (c2,c6) in t1 and t2 → n=2.
# (c3,c6) in t2 and t3 → n=2. (c4,c6) in t3 and t4 → n=2. (c5,c6) in t4 and t5 → n=2.
# (c0,c6) in t0 and t5 → n=2.
# All top edges interior! This makes a CLOSED annular mesh — no boundary!
# Need open mesh. Don't close the fan.

# Instead: 5 triangles, fan from c6, open bottom.
# t0=(c6,c0,c1), t1=(c6,c1,c2), t2=(c6,c2,c3), t3=(c6,c3,c4), t4=(c6,c4,c5)
# Interior (n=2): (c6,c1),(c6,c2),(c6,c3),(c6,c4) — shared between adjacent tris.
# Boundary (n=1): (c6,c0) in t0 only; (c6,c5) in t4 only;
#                 bottom: (c0,c1),(c1,c2),(c2,c3),(c3,c4),(c4,c5).
# Boundary cycle: c6→c0→c1→c2→c3→c4→c5→c6.
# Targets visited: c0(0,0,0), c1(1,0,0), c2(2,0,0), c3(3,0,0), c4(1,0,0), c5(2,0,0), c6(apex).
# Group A: c1 and c4 at (1,0,0). Group B: c2 and c5 at (2,0,0).
# Two separate coincidence groups → interval_sanitation (Branch 6).

t0 = m.triangle(c6, c0, c1)  # 0
t1 = m.triangle(c6, c1, c2)  # 1 — shares (c6,c1) with t0
t2 = m.triangle(c6, c2, c3)  # 2 — shares (c6,c2) with t1
t3 = m.triangle(c6, c3, c4)  # 3 — shares (c6,c3) with t2
t4 = m.triangle(c6, c4, c5)  # 4 — shares (c6,c4) with t3

# Interior shared edges (n=2).
m.assert_edge_shared(c6, c1, 2)  # t0 and t1
m.assert_edge_shared(c6, c2, 2)  # t1 and t2
m.assert_edge_shared(c6, c3, 2)  # t2 and t3
m.assert_edge_shared(c6, c4, 2)  # t3 and t4

# Boundary edges (n=1).
m.assert_edge_shared(c6, c0, 1)  # t0 left spoke
m.assert_edge_shared(c6, c5, 1)  # t4 right spoke
m.assert_edge_shared(c0, c1, 1)  # t0 bottom-left
m.assert_edge_shared(c1, c2, 1)  # t1 bottom
m.assert_edge_shared(c2, c3, 1)  # t2 bottom
m.assert_edge_shared(c3, c4, 1)  # t3 bottom
m.assert_edge_shared(c4, c5, 1)  # t4 bottom-right

# Group A: c1 and c4 at (1,0,0).
m.assert_vertex_pair_distance_lt(c1, c4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(c1, c4)

# Group B: c2 and c5 at (2,0,0).
m.assert_vertex_pair_distance_lt(c2, c5, 1e-9)
m.assert_vertex_pair_no_shared_triangle(c2, c5)

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
