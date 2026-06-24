"""Me604 — merge_duplicated_vertices_in_boundary_cycle halfedge_advance: while(start!=h) cycle-completeness check; loop traverses full 6-edge boundary cycle (Branch 5).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycle` Branch 5
(*halfedge_advance*) @ line 307:
  'h = next(h, pm); } while(start != h);'
  — the do-while loop advances h to next(h) after each step and tests
  whether the cycle has completed (h has returned to start). Branch 5 is
  the loop-back condition: it fires at every step except the last (where
  start==h terminates), and the final check fires when the full cycle
  has been walked. A longer boundary cycle with measurable length makes
  the multiple iterations observable.

Defect pattern: four triangles with a hexagonal boundary cycle (6 boundary
  edges). Vertices h1 and h4 are coincident at (2,0,0) — a coincident pair
  on the boundary ensures the cycle-repair algorithm actually processes the
  cycle. The do-while loop fires 6 times (once per boundary halfedge),
  advancing through the full cycle before detect_identical_mergeable_vertices
  is called → Branch 5 fires repeatedly.

Geometry:
  h0=(0,0,0), h1=(2,0,0), h2=(4,0,0), h3=(3,2,0), h4=(2,0,0)[=h1], h5=(1,2,0)
  Four triangles: t0=(h0,h1,h5), t1=(h1,h2,h3), t2=(h1,h3,h5), t3=(h3,h4,h5)
  sharing interior edges (h1,h5) and (h1,h3) and (h3,h5).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me604",
    title="merge_duplicated_vertices_in_boundary_cycle halfedge_advance: do-while traverses 6-edge boundary cycle (h1==h4 at (2,0,0)); start!=h check fires 6 times (Branch 5)",
    defect_class="near_coincident_vertex",
)

h0 = m.vertex(0.0, 0.0, 0.0)   # 0 — far-left
h1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom-center, coincident with h4
h2 = m.vertex(4.0, 0.0, 0.0)   # 2 — far-right
h3 = m.vertex(3.0, 2.0, 0.0)   # 3 — top-right
h4 = m.vertex(2.0, 0.0, 0.0)   # 4 — coincident with h1
h5 = m.vertex(1.0, 2.0, 0.0)   # 5 — top-left

# Four triangles.
t0 = m.triangle(h0, h1, h5)    # 0: bottom-left
t1 = m.triangle(h1, h2, h3)    # 1: bottom-right
t2 = m.triangle(h1, h3, h5)    # 2: center
t3 = m.triangle(h3, h4, h5)    # 3: top (h4 is duplicate of h1)

# Interior shared edges — n=2.
m.assert_edge_shared(h1, h5, 2)   # shared by t0 and t2
m.assert_edge_shared(h1, h3, 2)   # shared by t1 and t2
m.assert_edge_shared(h3, h5, 2)   # shared by t2 and t3

# Boundary edges — n=1 each (6 boundary edges).
m.assert_edge_shared(h0, h1, 1)   # t0 bottom
m.assert_edge_shared(h0, h5, 1)   # t0 left
m.assert_edge_shared(h1, h2, 1)   # t1 bottom
m.assert_edge_shared(h2, h3, 1)   # t1 right
m.assert_edge_shared(h3, h4, 1)   # t3 right
m.assert_edge_shared(h4, h5, 1)   # t3 top

# h1 and h4 are coincident on the boundary — confirms cycle contains a defect.
m.assert_vertex_pair_distance_lt(h1, h4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(h1, h4)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
