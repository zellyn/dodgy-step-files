"""Me400 — detect_identical_mergeable_vertices sorting_by_point: boundary halfedges sorted by target coordinate (Branch 1).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 1 (*sorting_by_point*) @ line 159:
  'std::sort(cycle_hedges.begin(), cycle_hedges.end(), Less_on_point_of_target(vpm));'
  — for each boundary cycle the algorithm collects all halfedges and sorts them by
  target vertex coordinate. This sort fires for any cycle that may contain coincident
  vertices; it is the entry point to the entire detection logic.

Defect pattern: two triangles sharing an interior edge, forming a quadrilateral
  boundary cycle. Two boundary vertices (v1 and v3) share identical coordinates
  (1.0, 0.0, 0.0) but are topologically distinct indices. When the boundary cycle
  is processed, std::sort arranges the halfedges so that the halfedge targeting v1
  and the halfedge targeting v3 become adjacent — Branch 1 fires.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1,0,0) [coincident with v1]
  t0=(v0,v1,v2), t1=(v0,v2,v3) sharing interior edge (v0,v2).
  Boundary cycle: v0 → v1 → v2 → v3 → v0.
  v1 and v3 at identical coordinates trigger sorting_by_point.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me400",
    title="detect_identical_mergeable_vertices sorting_by_point: boundary cycle halfedges sorted by target coordinate; coincident v1==v3 at (1,0,0) (Branch 1)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary vertex, coincident with v3
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex
v3 = m.vertex(1.0, 0.0, 0.0)  # 3 — boundary vertex, coincident with v1

# Two triangles sharing interior edge (v0, v2).
t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v0, v2, v3)  # 1: right triangle

# Shared interior edge (v0, v2) — n=2.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)  # t0 bottom-left
m.assert_edge_shared(v1, v2, 1)  # t0 right
m.assert_edge_shared(v2, v3, 1)  # t1 right
m.assert_edge_shared(v0, v3, 1)  # t1 bottom-right

# v1 and v3 are coincident on the boundary cycle — triggers sorting_by_point.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
