"""Me603 — merge_duplicated_vertices_in_boundary_cycle merge_execution: internal::merge_vertices_in_range topologically merges single coincident-vertex group (Branch 4).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycle` Branch 4
(*merge_execution*) @ line 319:
  'internal::merge_vertices_in_range(hedges.begin(), hedges.end(), pm);'
  — for a single group of coincident halfedge targets the algorithm invokes
  the internal merge primitive, which walks the halfedge range and redirects
  all half-edge links so that all vertices in the group collapse to the first.
  Branch 4 is the topological mutation: it fires exactly once for a cycle with
  exactly one coincident group.

Defect pattern: two triangles with a quadrilateral boundary cycle. Vertices
  g1 and g3 are both at (1,0,0). detect_identical_mergeable_vertices returns
  a single group {g1, g3}. The for-each loop (Branch 3) fires once, and
  merge_vertices_in_range is called for that group → Branch 4 fires.
  This is the minimal single-group execution path.

Geometry:
  g0=(0,0,0), g1=(1,0,0), g2=(0.5,1,0), g3=(1,0,0) [=g1]
  t0=(g0,g1,g2), t1=(g0,g2,g3) sharing interior edge (g0,g2).
  Boundary cycle: g0 → g1 → g2 → g3 → g0.
  Single group {g1,g3} → merge_vertices_in_range called once.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me603",
    title="merge_duplicated_vertices_in_boundary_cycle merge_execution: internal::merge_vertices_in_range called for single group g1==g3 at (1,0,0); topological merge fires (Branch 4)",
    defect_class="near_coincident_vertex",
)

g0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left corner
g1 = m.vertex(1.0, 0.0, 0.0)   # 1 — right base, coincident with g3
g2 = m.vertex(0.5, 1.0, 0.0)   # 2 — apex
g3 = m.vertex(1.0, 0.0, 0.0)   # 3 — right base duplicate, coincident with g1

# Two triangles sharing interior edge (g0, g2).
t0 = m.triangle(g0, g1, g2)    # 0: front triangle
t1 = m.triangle(g0, g2, g3)    # 1: back triangle

# Interior shared edge (g0, g2) — n=2.
m.assert_edge_shared(g0, g2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(g0, g1, 1)   # t0 bottom-left
m.assert_edge_shared(g1, g2, 1)   # t0 right
m.assert_edge_shared(g2, g3, 1)   # t1 right
m.assert_edge_shared(g0, g3, 1)   # t1 bottom-right

# Single coincident group on the boundary cycle → merge_vertices_in_range fires.
m.assert_vertex_pair_distance_lt(g1, g3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(g1, g3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
