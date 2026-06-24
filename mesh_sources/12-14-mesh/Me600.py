"""Me600 — merge_duplicated_vertices_in_boundary_cycle boundary_cycle_traversal: start halfedge validation, CGAL_precondition guard fires (Branch 1).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycle` Branch 1
(*boundary_cycle_traversal*) @ line 305:
  'CGAL_precondition(is_valid_halfedge_descriptor(h, pm));'
  — on entry the algorithm asserts the caller-supplied halfedge is a valid
  descriptor for the polygon mesh. This precondition fires for every valid
  invocation; if the descriptor were invalid the assert would abort. The
  branch covers the common case where the guard passes silently.

Defect pattern: two triangles sharing one interior edge, producing a
  quadrilateral open boundary cycle. The mesh is a valid polygon mesh with
  a single boundary component. On entry the caller supplies any halfedge on
  that boundary; is_valid_halfedge_descriptor returns true → Branch 1 fires
  (precondition satisfied, traversal proceeds).

Geometry:
  p0=(0,0,0), p1=(1,0,0), p2=(0.5,1,0), p3=(1.5,1,0)
  t0=(p0,p1,p2), t1=(p1,p3,p2) sharing interior edge (p1,p2).
  Boundary cycle: p0 → p1 → p3 → p2 → p0 (4 boundary edges).
  No coincident vertices — purely tests that the precondition guard
  passes on a well-formed boundary cycle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me600",
    title="merge_duplicated_vertices_in_boundary_cycle boundary_cycle_traversal: CGAL_precondition guard passes on valid boundary halfedge; 4-edge cycle traversal begins (Branch 1)",
    defect_class="near_coincident_vertex",
)

p0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left base
p1 = m.vertex(1.0, 0.0, 0.0)   # 1 — right base
p2 = m.vertex(0.5, 1.0, 0.0)   # 2 — left apex
p3 = m.vertex(1.5, 1.0, 0.0)   # 3 — right apex

# Two triangles sharing interior edge (p1, p2).
t0 = m.triangle(p0, p1, p2)    # 0: left triangle
t1 = m.triangle(p1, p3, p2)    # 1: right triangle

# Interior shared edge (p1, p2) — n=2.
m.assert_edge_shared(p1, p2, 2)

# Boundary edges — n=1 each (4 boundary edges in the cycle).
m.assert_edge_shared(p0, p1, 1)   # t0 bottom
m.assert_edge_shared(p0, p2, 1)   # t0 left
m.assert_edge_shared(p2, p3, 1)   # t1 top
m.assert_edge_shared(p1, p3, 1)   # t1 right

# Euler: V=4, E=5, F=2, chi=1 (open disk topology).
m.assert_euler_characteristic(4, 5, 2, 1)
