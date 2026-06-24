"""Me602 — merge_duplicated_vertices_in_boundary_cycle merge_iteration: for-each over hedges_with_identical_point_target with 2 coincident groups (Branch 3).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycle` Branch 3
(*merge_iteration*) @ line 314:
  'for(const std::vector<halfedge_descriptor>& hedges :
       hedges_with_identical_point_target)
   { merge_vertices_in_range(hedges.begin(), hedges.end(), pm); }'
  — after detect_identical_mergeable_vertices returns a list of coincident
  groups, the outer for-each loop iterates over every group and dispatches
  to merge_vertices_in_range. Branch 3 fires once per group; a cycle with
  two distinct groups fires it twice.

Defect pattern: five triangles with a heptagonal boundary cycle containing
  two separate coincident-vertex pairs. Group A: f1==f4 at (1,0,0). Group B:
  f2==f5 at (3,0,0). detect_identical_mergeable_vertices returns two groups
  in hedges_with_identical_point_target. The for-each loop fires twice →
  Branch 3 fires.

Geometry:
  f0=(0,0,0), f1=(1,0,0), f2=(3,0,0), f3=(4,0,0), f4=(1,0,0)[=f1],
  f5=(3,0,0)[=f2], f6=(2,2,0) apex
  Five triangles from apex f6 to consecutive boundary pairs.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me602",
    title="merge_duplicated_vertices_in_boundary_cycle merge_iteration: for-each loop over 2 coincident groups (f1==f4 at (1,0,0) and f2==f5 at (3,0,0)) fires twice (Branch 3)",
    defect_class="near_coincident_vertex",
)

f0 = m.vertex(0.0, 0.0, 0.0)   # 0
f1 = m.vertex(1.0, 0.0, 0.0)   # 1 — coincident with f4
f2 = m.vertex(3.0, 0.0, 0.0)   # 2 — coincident with f5
f3 = m.vertex(4.0, 0.0, 0.0)   # 3
f4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident with f1
f5 = m.vertex(3.0, 0.0, 0.0)   # 5 — coincident with f2
f6 = m.vertex(2.0, 2.0, 0.0)   # 6 — apex

# Five triangles fanning from apex f6.
t0 = m.triangle(f6, f0, f1)    # 0
t1 = m.triangle(f6, f1, f2)    # 1
t2 = m.triangle(f6, f2, f3)    # 2
t3 = m.triangle(f6, f3, f4)    # 3
t4 = m.triangle(f6, f4, f5)    # 4

# Interior edges from apex f6 to each boundary vertex.
m.assert_edge_shared(f6, f1, 2)   # shared by t0 and t1
m.assert_edge_shared(f6, f2, 2)   # shared by t1 and t2
m.assert_edge_shared(f6, f3, 2)   # shared by t2 and t3
m.assert_edge_shared(f6, f4, 2)   # shared by t3 and t4

# Boundary edges (all n=1).
m.assert_edge_shared(f6, f0, 1)   # t0 left
m.assert_edge_shared(f0, f1, 1)   # t0 bottom
m.assert_edge_shared(f1, f2, 1)   # t1 bottom
m.assert_edge_shared(f2, f3, 1)   # t2 bottom
m.assert_edge_shared(f3, f4, 1)   # t3 bottom
m.assert_edge_shared(f4, f5, 1)   # t4 bottom
m.assert_edge_shared(f5, f6, 1)   # t4 right

# Two coincident groups on the boundary cycle.
m.assert_vertex_pair_distance_lt(f1, f4, 1e-9)
m.assert_vertex_pair_distance_lt(f2, f5, 1e-9)
m.assert_vertex_pair_no_shared_triangle(f1, f4)
m.assert_vertex_pair_no_shared_triangle(f2, f5)

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
