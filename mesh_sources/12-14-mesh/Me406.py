"""Me406 — detect_identical_mergeable_vertices output_conversion: sanitized candidate IDs converted back to halfedge descriptors (Branch 7).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 7 (*output_conversion*) @ line 198:
  'for(const std::vector<std::size_t>& candidates : candidate_hedges_with_id)
   { hedges_with_identical_point_target.push_back({}); ...; }'
  — after sanitize_candidates resolves any conflicts, the remaining candidate groups
  are iterated and each sorted index is mapped back to an actual halfedge descriptor
  via cycle_hedges[id]. The result is appended to hedges_with_identical_point_target.
  This branch fires for any mesh where at least one valid coincident-vertex group
  survives sanitization.

Defect pattern: a minimal polygon mesh with one boundary cycle containing a single
  coincident-vertex pair. The pair forms a single candidate group that survives
  sanitize_candidates unchanged. The output conversion loop runs exactly once, mapping
  the two sorted indices back to halfedge descriptors → Branch 7 fires.

Geometry:
  d0=(0,0,0), d1=(2,0,0), d2=(1,2,0), d3=(2,0,0) [coincident with d1]
  t0=(d0,d1,d2), t1=(d0,d2,d3) sharing interior edge (d0,d2).
  Boundary cycle: d0→d1→d2→d3→d0. d1 and d3 at (2,0,0).
  One group {d1,d3} survives → output_conversion populates result.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me406",
    title="detect_identical_mergeable_vertices output_conversion: single coincident group (d1==d3 at (2,0,0)) survives sanitization; mapped to halfedge descriptors (Branch 7)",
    defect_class="near_coincident_vertex",
)

d0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left corner
d1 = m.vertex(2.0, 0.0, 0.0)  # 1 — boundary at (2,0,0); coincident with d3
d2 = m.vertex(1.0, 2.0, 0.0)  # 2 — apex
d3 = m.vertex(2.0, 0.0, 0.0)  # 3 — boundary at (2,0,0); coincident with d1

# Two triangles sharing interior edge (d0, d2).
t0 = m.triangle(d0, d1, d2)  # 0: left triangle
t1 = m.triangle(d0, d2, d3)  # 1: right triangle

# Interior shared edge (d0, d2) — n=2.
m.assert_edge_shared(d0, d2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(d0, d1, 1)
m.assert_edge_shared(d1, d2, 1)
m.assert_edge_shared(d2, d3, 1)
m.assert_edge_shared(d0, d3, 1)

# Coincident pair d1 and d3 on the boundary cycle.
# Single candidate group {d1,d3} survives sanitization → output_conversion fires.
m.assert_vertex_pair_distance_lt(d1, d3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(d1, d3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
