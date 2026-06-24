"""Me601 — merge_duplicated_vertices_in_boundary_cycle vertex_detection: detect_identical_mergeable_vertices called on boundary cycle with coincident vertex pair (Branch 2).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycle` Branch 2
(*vertex_detection*) @ line 312:
  'auto hedges_with_identical_point_target =
     detect_identical_mergeable_vertices(h, pm, vpm);'
  — after validating the start halfedge the algorithm collects all
  halfedges in the boundary cycle and calls detect_identical_mergeable_vertices
  to find groups of halfedges whose target vertices have identical coordinates.
  Branch 2 fires whenever the cycle contains at least one coincident-vertex pair.

Defect pattern: three triangles with a pentagonal boundary cycle containing
  one coincident vertex pair. Vertices e1 and e4 both sit at (2,0,0) but are
  topologically distinct. detect_identical_mergeable_vertices traverses the
  boundary cycle, sorts halfedges by target coordinate, and identifies the
  {e1, e4} pair → Branch 2 fires.

Geometry:
  e0=(0,0,0), e1=(2,0,0), e2=(3,1,0), e3=(0,2,0), e4=(2,0,0) [=e1]
  t0=(e0,e1,e3), t1=(e1,e2,e3) [wait — need connected ring]
  Actually: e0=(0,0,0), e1=(2,0,0), e2=(4,0,0), e3=(2,2,0), e4=(2,0,0) [=e1]
  t0=(e0,e1,e3), t1=(e1,e2,e3), t2=(e0,e3,e4)
  sharing interior edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me601",
    title="merge_duplicated_vertices_in_boundary_cycle vertex_detection: detect_identical_mergeable_vertices finds coincident pair e1==e4 at (2,0,0) on boundary cycle (Branch 2)",
    defect_class="near_coincident_vertex",
)

e0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left corner
e1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom-mid, coincident with e4
e2 = m.vertex(4.0, 0.0, 0.0)   # 2 — right corner
e3 = m.vertex(2.0, 2.0, 0.0)   # 3 — top apex
e4 = m.vertex(2.0, 0.0, 0.0)   # 4 — coincident with e1

# Three triangles: t0 and t1 share edge (e1,e3); t0 and t2 share edge (e0,e3).
t0 = m.triangle(e0, e1, e3)    # 0: left
t1 = m.triangle(e1, e2, e3)    # 1: right
t2 = m.triangle(e0, e3, e4)    # 2: far-left (e4 is duplicate of e1)

# Interior shared edges.
m.assert_edge_shared(e0, e3, 2)   # shared by t0 and t2
m.assert_edge_shared(e1, e3, 2)   # shared by t0 and t1

# Boundary edges — n=1 each.
m.assert_edge_shared(e0, e1, 1)   # t0 bottom
m.assert_edge_shared(e1, e2, 1)   # t1 bottom
m.assert_edge_shared(e2, e3, 1)   # t1 right
m.assert_edge_shared(e3, e4, 1)   # t2 top-left
m.assert_edge_shared(e0, e4, 1)   # t2 left

# e1 and e4 are coincident on the boundary cycle.
m.assert_vertex_pair_distance_lt(e1, e4, 1e-9)
m.assert_vertex_pair_no_shared_triangle(e1, e4)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
