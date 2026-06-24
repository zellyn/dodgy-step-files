"""Me491 — sanitize_candidates outer_group_iteration: for(fr_id=0, fr_end=n-1); 2+ disjoint groups (Branch 2).

CGAL PMP `PMP.internal.sanitize_candidates` Branch 2 (*outer_group_iteration*) @ line 81:
  'for(std::size_t fr_id=0, fr_end=nm_vertices_n-1; fr_id != fr_end; ++fr_id)'
  — the outer loop over candidate groups fires when candidate_hedges_with_id
  has at least 2 entries (n >= 2). The loop variable fr_id runs from 0 to
  nm_vertices_n-2 (inclusive). Branch 2 captures the loop header executing
  for the first group (fr_id == 0).

Defect pattern: a single boundary cycle containing exactly TWO disjoint
  coincident-vertex groups with non-overlapping index ranges. Group A uses
  sorted boundary halfedge indices [i, j]; Group B uses [k, l] where i < j < k < l.
  Both groups are valid (no interleaving) so sanitize_candidates keeps both, but
  the outer loop still executes → Branch 2 fires.

Geometry:
  Fan of 5 triangles from apex f6=(1.5,2,0); open boundary cycle visits
  f0,f1,f2,f3,f4,f5 along the bottom and two open spokes to f6 on the sides.
  Coincident groups:
    Group A: f1 and f3 both at (1,0,0) — sorted indices [i_f1, i_f3].
    Group B: f2 and f4 both at (2,0,0) — sorted indices [i_f2, i_f4].
  Index ranges in the sorted halfedge array (positions determined by coordinate
  ordering):
    f0=(0,0,0), f1=(1,0,0)[=f3], f2=(2,0,0)[=f4], f3=(1,0,0), f4=(2,0,0),
    f5=(3,0,0), f6=(1.5,2,0).
  After coordinate sort the order is: f0 < f1=f3 < f2=f4 < f5 < f6.
  Group A occupies consecutive sorted positions for coordinate (1,0,0):
    positions p and p+1 (where p ~ 1 in the sorted array).
  Group B occupies consecutive sorted positions for coordinate (2,0,0):
    positions q and q+1 (where q ~ 3).
  Because p+1 < q the two groups are disjoint → both survive sanitization.
  The outer loop iterates fr_id=0 (Group A) → Branch 2 fires.

  Five triangles: t0=(f6,f0,f1), t1=(f6,f1,f2), t2=(f6,f2,f3),
                  t3=(f6,f3,f4), t4=(f6,f4,f5).
  Interior: (f6,f1),(f6,f2),(f6,f3),(f6,f4) each n=2.
  Boundary: (f6,f0),(f6,f5),(f0,f1),(f1,f2),(f2,f3),(f3,f4),(f4,f5) each n=1.
  Euler: V=7, E=11, F=5, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me491",
    title="sanitize_candidates outer_group_iteration: two disjoint coincident groups (f1==f3 at (1,0,0), f2==f4 at (2,0,0)); outer for-loop fires for fr_id=0 (Branch 2)",
    defect_class="near_coincident_vertex",
)

f0 = m.vertex(0.0, 0.0, 0.0)  # 0 — boundary; distinct
f1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary; Group A at (1,0,0)
f2 = m.vertex(2.0, 0.0, 0.0)  # 2 — boundary; Group B at (2,0,0)
f3 = m.vertex(1.0, 0.0, 0.0)  # 3 — boundary; Group A at (1,0,0), coincident with f1
f4 = m.vertex(2.0, 0.0, 0.0)  # 4 — boundary; Group B at (2,0,0), coincident with f2
f5 = m.vertex(3.0, 0.0, 0.0)  # 5 — boundary; distinct
f6 = m.vertex(1.5, 2.0, 0.0)  # 6 — apex; distinct

# Five-triangle fan from apex f6.
t0 = m.triangle(f6, f0, f1)  # 0
t1 = m.triangle(f6, f1, f2)  # 1 — shares (f6,f1) with t0
t2 = m.triangle(f6, f2, f3)  # 2 — shares (f6,f2) with t1
t3 = m.triangle(f6, f3, f4)  # 3 — shares (f6,f3) with t2
t4 = m.triangle(f6, f4, f5)  # 4 — shares (f6,f4) with t3

# Interior shared edges (n=2).
m.assert_edge_shared(f6, f1, 2)  # t0 and t1
m.assert_edge_shared(f6, f2, 2)  # t1 and t2
m.assert_edge_shared(f6, f3, 2)  # t2 and t3
m.assert_edge_shared(f6, f4, 2)  # t3 and t4

# Boundary edges (n=1).
m.assert_edge_shared(f6, f0, 1)  # t0 left spoke
m.assert_edge_shared(f6, f5, 1)  # t4 right spoke
m.assert_edge_shared(f0, f1, 1)  # t0 bottom-left
m.assert_edge_shared(f1, f2, 1)  # t1 bottom
m.assert_edge_shared(f2, f3, 1)  # t2 bottom
m.assert_edge_shared(f3, f4, 1)  # t3 bottom
m.assert_edge_shared(f4, f5, 1)  # t4 bottom-right

# Group A: f1 and f3 at (1,0,0) — sorted positions adjacent; no shared triangle.
m.assert_vertex_pair_distance_lt(f1, f3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(f1, f3)

# Group B: f2 and f4 at (2,0,0) — sorted positions adjacent; no shared triangle.
m.assert_vertex_pair_distance_lt(f2, f4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(f2, f4)

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
