"""Me402 — detect_identical_mergeable_vertices candidate_group_creation: new identical-point group started; resize and push (Branch 3).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 3 (*candidate_group_creation*) @ line 173:
  'candidate_hedges_with_id.resize(candidate_hedges_with_id.size() + 1);
   candidate_hedges_with_id.back().push_back(i-1);
   candidate_hedges_with_id.back().push_back(i);'
  — when a new identical-point match is found, a new sub-vector is appended to
  candidate_hedges_with_id (resize) and both the previous index (i-1) and current
  index (i) are pushed into it. This is the group-creation step for any coincident pair.

Defect pattern: four triangles (fan from a0) with a hexagonal boundary cycle containing
  exactly ONE pair of coincident boundary vertices (a2 and a5 at (2.0, 0.0, 0.0)).
  The pair forms a single new candidate group — resize is called once (Branch 3).
  The inner while loop does not extend the group (only 2 members, not 3+).

Geometry:
  a0=(0,0,0), a1=(1,0,0), a2=(2,0,0) [coincident with a5], a3=(1.5,1,0),
  a4=(0.5,1,0), a5=(2,0,0)
  t0=(a0,a1,a4), t1=(a1,a3,a4), t2=(a1,a2,a3), t3=(a0,a5,a1).
  Boundary cycle visits a2 and a5 (both at (2,0,0)) — exactly one pair.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me402",
    title="detect_identical_mergeable_vertices candidate_group_creation: single coincident pair a2==a5 at (2,0,0) on boundary; new group created via resize+push_back (Branch 3)",
    defect_class="near_coincident_vertex",
)

a0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base
a1 = m.vertex(1.0, 0.0, 0.0)  # 1 — bottom hub
a2 = m.vertex(2.0, 0.0, 0.0)  # 2 — boundary; coincident with a5
a3 = m.vertex(1.5, 1.0, 0.0)  # 3 — upper right
a4 = m.vertex(0.5, 1.0, 0.0)  # 4 — upper left
a5 = m.vertex(2.0, 0.0, 0.0)  # 5 — boundary; coincident with a2

# Four triangles: t0=(a0,a1,a4), t1=(a1,a3,a4), t2=(a1,a2,a3), t3=(a0,a5,a1)
t0 = m.triangle(a0, a1, a4)  # 0: lower-left
t1 = m.triangle(a1, a3, a4)  # 1: upper, shares (a1,a4) with t0
t2 = m.triangle(a1, a2, a3)  # 2: right, shares (a1,a3) with t1
t3 = m.triangle(a0, a5, a1)  # 3: lower-right, shares (a0,a1) with t0

# Interior shared edges (n=2).
m.assert_edge_shared(a0, a1, 2)  # t0 and t3
m.assert_edge_shared(a1, a4, 2)  # t0 and t1
m.assert_edge_shared(a1, a3, 2)  # t1 and t2

# Boundary edges (n=1).
m.assert_edge_shared(a0, a4, 1)  # t0 outer left
m.assert_edge_shared(a3, a4, 1)  # t1 outer top
m.assert_edge_shared(a2, a3, 1)  # t2 outer right-top
m.assert_edge_shared(a1, a2, 1)  # t2 outer right-bottom
m.assert_edge_shared(a0, a5, 1)  # t3 outer bottom-left
m.assert_edge_shared(a1, a5, 1)  # t3 outer bottom-right

# Coincident pair on boundary — triggers candidate_group_creation (one group, size 2).
m.assert_vertex_pair_distance_lt(a2, a5, 1e-9)
m.assert_vertex_pair_no_shared_triangle(a2, a5)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
