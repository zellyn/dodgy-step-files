"""Me663 — merge_duplicate_points_in_polygon_soup merge_needed_check: unique_points.size()!=ini_points_n; coincident pair reduces unique count; remap triggered (Branch 4).

CGAL PMP `PMP.merge_duplicate_points_in_polygon_soup` Branch 4 (*merge_needed_check*) @ line 563:
  'if(unique_points.size() != ini_points_n) { ... perform remap ... }'
  — After the deduplication scan, the algorithm checks whether any duplicates
  were found by comparing the unique-point count to the original point count.
  If they differ, remapping is needed. This branch is the conditional that
  triggers the remap path (Branches 4 and 5 together); it fires whenever at
  least one duplicate coordinate pair exists in the input.

Defect pattern: four triangles in a strip with one pair of coincident
  boundary vertices. After scanning all 6 input points, unique_points
  contains only 5 entries (the coincident pair mapped to the same id),
  so unique_points.size()==5 != ini_points_n==6 → Branch 4 fires.

Geometry:
  r0=(0,0,0), r1=(1,0,0), r2=(2,0,0), r3=(3,0,0),
  r4=(1,1,0), r5=(2,1,0) — top pair
  t0=(r0,r1,r4), t1=(r1,r2,r4) sharing (r1,r4)
  Wait — simpler: use 6 vertices with one coincident pair among them.

  s0=(0,0,0), s1=(2,0,0), s2=(1,1,0),
  s3=(2,2,0), s4=(2,0,0) [coincident with s1], s5=(3,1,0)
  t0=(s0,s1,s2), t1=(s0,s2,s3) sharing (s0,s2)
  t2=(s3,s4,s5), t3=(s3,s2,s4)? need shared edge
  Keep minimal: 3 triangles, 5 input vertices, 1 coincident pair = 4 unique.
  unique_points.size()==4 != ini_points_n==5 → Branch 4 fires.

Revised geometry:
  u0=(0,0,0), u1=(1,0,0), u2=(0.5,1,0),
  u3=(1.5,1,0), u4=(1,0,0) [coincident with u1]
  t0=(u0,u1,u2), t1=(u2,u4,u3), t2=(u0,u2,u4)
  Shared edges: (u0,u2) in t0,t2 → n=2; (u2,u4) in t1,t2 → n=2.
  V=5, E=7, F=3: 5-7+3=1 → chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me663",
    title="merge_duplicate_points_in_polygon_soup merge_needed_check: 5 input points but 4 unique (u1==u4 at (1,0,0)); unique_points.size()!=ini_points_n triggers remap (Branch 4)",
    defect_class="near_coincident_vertex",
)

u0 = m.vertex(0.0, 0.0, 0.0)  # 0
u1 = m.vertex(1.0, 0.0, 0.0)  # 1 — coincident with u4
u2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex-left
u3 = m.vertex(1.5, 1.0, 0.0)  # 3 — apex-right
u4 = m.vertex(1.0, 0.0, 0.0)  # 4 — coincident with u1

# Three triangles.
t0 = m.triangle(u0, u1, u2)   # 0: left triangle
t1 = m.triangle(u2, u4, u3)   # 1: right triangle
t2 = m.triangle(u0, u2, u4)   # 2: connector

# Interior shared edges (n=2).
m.assert_edge_shared(u0, u2, 2)   # t0 and t2
m.assert_edge_shared(u2, u4, 2)   # t1 and t2

# Boundary edges (n=1).
m.assert_edge_shared(u0, u1, 1)   # t0 bottom
m.assert_edge_shared(u1, u2, 1)   # t0 right
m.assert_edge_shared(u3, u4, 1)   # t1 right
m.assert_edge_shared(u2, u3, 1)   # t1 top
m.assert_edge_shared(u0, u4, 1)   # t2 bottom

# u1 and u4 are coincident — unique count (4) < ini_points_n (5).
# merge_needed_check fires; remap will be performed.
m.assert_vertex_pair_distance_lt(u1, u4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(u1, u4)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
