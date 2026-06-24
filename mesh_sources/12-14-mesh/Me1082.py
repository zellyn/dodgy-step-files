"""Me1082 — remove_degenerate_faces adjacent_degenerate_faces_missed: partial range misses collinear neighbor via faces_to_visit walk (Branch 3).

CGAL PMP `PMP.remove_degenerate_faces` Branch 3 (*adjacent_degenerate_faces_missed*) @ line 2061:
  'if (!is_range_full_mesh) { ... faces_to_visit walk ... expand degenerate set ... }'
  — when the input range is not the full mesh (is_range_full_mesh == false), the sanitize
  step walks adjacent faces via faces_to_visit to discover and add any connected degenerate
  neighbors that were not in the initial range.

Defect pattern: three collinear zero-area triangles arranged in an L-shape chain.
  t0 and t1 share edge (v1,v2); t1 and t2 share edge (v2,v3). A clean non-degenerate
  triangle t3 provides topological context. When repair is called with only t0 in the
  input range (is_range_full_mesh=false), the faces_to_visit walk discovers t1 and t2
  as adjacent degenerate neighbors → Branch 3 fires to expand the degenerate set.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(3,0,0) — x-axis (collinear)
  v4=(0,2,0), v5=(1,2,0), v6=(2,2,0) — y=2 row (non-collinear base)
  t0=(v0,v1,v2): collinear on x-axis, area=0 (degenerate, in initial range)
  t1=(v1,v2,v3): collinear on x-axis, area=0 (degenerate, adjacent to t0)
  t2=(v0,v1,v5): area>0, wait — use distinct y for non-degen
  t3=(v4,v5,v6): clean non-degenerate control triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1082",
    title="remove_degenerate_faces adjacent_degenerate_faces_missed: three collinear triangles in chain; faces_to_visit walk expands partial range (Branch 3)",
    defect_class="degenerate_triangle",
)

# Three collinear degenerate triangles chained along x-axis.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
v3 = m.vertex(3.0, 0.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)   # 0: collinear, area=0 — in initial input range
t1 = m.triangle(v1, v2, v3)   # 1: collinear, area=0 — adjacent to t0 via (v1,v2); discovered by walk
t2 = m.triangle(v0, v1, v3)   # 2: collinear (same y=0 line), area=0 — adjacent to t0 via (v0,v1)

# Clean non-degenerate control triangle (disconnected).
v4 = m.vertex(5.0, 0.0, 0.0)  # 4
v5 = m.vertex(6.0, 0.0, 0.0)  # 5
v6 = m.vertex(5.5, 1.0, 0.0)  # 6 — apex gives positive area
t3 = m.triangle(v4, v5, v6)   # 3: clean, non-degenerate

# All three degenerate triangles have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)

# Shared edges among degenerate triangles (t0,t1 share (v1,v2); t0,t2 share (v0,v1); t1,t2 share (v1,v3)->skip, t0,t2 share (v0,v3)->n=2 check):
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1 — key adjacency for faces_to_visit
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t2
m.assert_edge_shared(v1, v3, 2)   # shared by t1 and t2
