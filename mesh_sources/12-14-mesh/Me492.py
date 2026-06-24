"""Me492 — sanitize_candidates inner_group_iteration: for(sr_id=i+1, sr_end=n); 3+ groups; inner loop >1 iteration (Branch 3).

CGAL PMP `PMP.internal.sanitize_candidates` Branch 3 (*inner_group_iteration*) @ line 92:
  'for(std::size_t sr_id=fr_id+1, sr_end=nm_vertices_n; sr_id != sr_end; ++sr_id)'
  — the inner loop iterates the second group starting at fr_id+1. When there are
  3+ candidate groups the inner loop runs more than once per outer-loop iteration
  (e.g. for fr_id=0 it runs for sr_id=1 and sr_id=2). Branch 3 fires when
  sr_id advances past the first inner step (sr_id != sr_end with sr_id >= fr_id+2).

Defect pattern: a single boundary cycle with THREE disjoint coincident-vertex groups,
  each at a distinct coordinate value, so no pair is interleaved. With 3 groups
  (n=3), the outer loop runs for fr_id=0; the inner loop runs for sr_id=1
  (comparing Group A vs Group B) and sr_id=2 (comparing Group A vs Group C),
  demonstrating 2+ inner iterations → Branch 3 fires.

Index ranges of coincident groups in the sorted halfedge array:
  Coordinates in ascending (x,y,z) order:
    Group A: g1,g4 both at (1,0,0) — sorted positions 1 and 2.
    Group B: g2,g5 both at (2,0,0) — sorted positions 3 and 4.
    Group C: g3,g6 both at (3,0,0) — sorted positions 5 and 6.
  The intervals [1,2], [3,4], [5,6] are fully disjoint so all three groups survive.
  The outer loop (fr_id=0) drives the inner loop twice (sr_id=1, sr_id=2).

Geometry:
  Fan of 7 triangles from apex g0=(1.5,2,0); boundary cycle visits
  g7=(0,0,0), g1=(1,0,0), g2=(2,0,0), g3=(3,0,0), g4=(1,0,0),
  g5=(2,0,0), g6=(3,0,0) plus the two open spokes to g0.
  Interior: (g0,g1),(g0,g2),(g0,g3),(g0,g4),(g0,g5),(g0,g6) each n=2.
  Boundary: (g0,g7),(g0,g6)[only in t6], bottom edges n=1.
  Euler: V=9, E=15, F=7, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me492",
    title="sanitize_candidates inner_group_iteration: three disjoint coincident groups (g1==g4, g2==g5, g3==g6); inner for-loop runs >1 iteration per outer step (Branch 3)",
    defect_class="near_coincident_vertex",
)

g7 = m.vertex(0.0, 0.0, 0.0)  # 0 — boundary; distinct
g1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary; Group A at (1,0,0)
g2 = m.vertex(2.0, 0.0, 0.0)  # 2 — boundary; Group B at (2,0,0)
g3 = m.vertex(3.0, 0.0, 0.0)  # 3 — boundary; Group C at (3,0,0)
g4 = m.vertex(1.0, 0.0, 0.0)  # 4 — boundary; Group A, coincident with g1
g5 = m.vertex(2.0, 0.0, 0.0)  # 5 — boundary; Group B, coincident with g2
g6 = m.vertex(3.0, 0.0, 0.0)  # 6 — boundary; Group C, coincident with g3
g0 = m.vertex(1.5, 2.0, 0.0)  # 7 — apex; distinct

# Six-triangle open fan from apex g0 (NOT closed — no t6).
# If a 7th triangle (g0,g6,g7) were added, (g0,g7) would appear in both
# t0 and t7 making the mesh closed with no boundary. We stop at t5.
t0 = m.triangle(g0, g7, g1)  # 0
t1 = m.triangle(g0, g1, g2)  # 1 — shares (g0,g1) with t0
t2 = m.triangle(g0, g2, g3)  # 2 — shares (g0,g2) with t1
t3 = m.triangle(g0, g3, g4)  # 3 — shares (g0,g3) with t2
t4 = m.triangle(g0, g4, g5)  # 4 — shares (g0,g4) with t3
t5 = m.triangle(g0, g5, g6)  # 5 — shares (g0,g5) with t4

# Interior shared edges (n=2).
m.assert_edge_shared(g0, g1, 2)  # t0 and t1
m.assert_edge_shared(g0, g2, 2)  # t1 and t2
m.assert_edge_shared(g0, g3, 2)  # t2 and t3
m.assert_edge_shared(g0, g4, 2)  # t3 and t4
m.assert_edge_shared(g0, g5, 2)  # t4 and t5

# Boundary edges (n=1).
m.assert_edge_shared(g0, g7, 1)  # t0 left spoke
m.assert_edge_shared(g0, g6, 1)  # t5 right spoke
m.assert_edge_shared(g7, g1, 1)  # t0 bottom-left
m.assert_edge_shared(g1, g2, 1)  # t1 bottom
m.assert_edge_shared(g2, g3, 1)  # t2 bottom
m.assert_edge_shared(g3, g4, 1)  # t3 bottom
m.assert_edge_shared(g4, g5, 1)  # t4 bottom
m.assert_edge_shared(g5, g6, 1)  # t5 bottom-right

# Group A: g1 and g4 at (1,0,0).
m.assert_vertex_pair_distance_lt(g1, g4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(g1, g4)

# Group B: g2 and g5 at (2,0,0).
m.assert_vertex_pair_distance_lt(g2, g5, 1e-9)
m.assert_vertex_pair_no_shared_triangle(g2, g5)

# Group C: g3 and g6 at (3,0,0).
m.assert_vertex_pair_distance_lt(g3, g6, 1e-9)
m.assert_vertex_pair_no_shared_triangle(g3, g6)

# Euler: V=8, E=13, F=6, chi=1 (open disk; 6 triangles t0-t5).
m.assert_euler_characteristic(8, 13, 6, 1)
