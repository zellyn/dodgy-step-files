"""Me506 — remove_almost_degenerate_faces cap_flip_fails: cap flip violates link condition; collapse fallback (Branch 7).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 7 (*Cap flip fails*) @ line 1059:
  'if(!CGAL::Euler::does_satisfy_link_condition(flip_halfedge, tmesh))'
  — after a cap is detected and its opposite edge is NOT a border, the algorithm
  attempts to flip the edge to heal the cap. If the flip itself violates the link
  condition (i.e. there is already an edge between the two "across" vertices), the
  flip is forbidden and the algorithm falls back to collapsing an edge of the cap
  instead.

Defect pattern: a cap triangle whose flip is blocked by an existing edge. The cap t0
  has vertices v0, v1 (base), v2 (cap vertex). The neighbor t1 shares edge v0-v1
  (making it interior). The flip would connect v2 to v3 (the opposite vertex in t1),
  but edge v2-v3 already exists (via blocking triangle t2). Link condition fails for
  the flip → collapse fallback.

Geometry (z = 0):
  v0=(0.0, 0.0,    0.0)  — left base of cap
  v1=(2.0, 0.0,    0.0)  — right base; base edge = 2.0
  v2=(1.0, 0.0001, 0.0)  — cap vertex (almost on base)
  v3=(1.0, -1.0,   0.0)  — neighbor below; opposite v2 in t1
  v4=(0.5, -0.5,   0.0)  — extra vertex forming blocking edge v2-v3

  Wait: edge v2-v3 exists if there is a triangle containing both v2 and v3.
  t2=(v2, v3, v4) creates edge v2-v3.

  t0=(v0,v1,v2)  — cap triangle (angle at v2 ≈ 180°)
  t1=(v1,v0,v3)  — shares interior edge v0-v1; opposite vertex is v3
  t2=(v2,v3,v4)  — creates existing edge v2-v3 → flip blocked
  t3=(v0,v4,v2)  — extra context triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me506",
    title="remove_almost_degenerate_faces cap_flip_fails: existing edge v2-v3 blocks flip; collapse fallback for cap v2=(1,0.0001,0) (Branch 7)",
    defect_class="cap_triangle",
)

v0 = m.vertex(0.0, 0.0,    0.0)   # 0 — cap left base
v1 = m.vertex(2.0, 0.0,    0.0)   # 1 — cap right base (long edge 2.0)
v2 = m.vertex(1.0, 0.0001, 0.0)   # 2 — cap vertex (nearly on base)
v3 = m.vertex(1.0, -1.0,   0.0)   # 3 — neighbor below; v3 is opposite v2 in t1
v4 = m.vertex(0.5, -0.5,   0.0)   # 4 — vertex completing blocking triangle

# Cap triangle (index 0).
t_cap = m.triangle(v0, v1, v2)    # 0

# Below-neighbor: shares edge v0-v1 (interior); opposite vertex v3.
m.triangle(v1, v0, v3)             # 1

# Blocking triangle: edge v2-v3 already exists.
# Flipping v0-v1 in t0/t1 pair would create new edge v2-v3, but it already exists.
m.triangle(v2, v3, v4)             # 2

# Additional context triangle to close the fan around v4.
m.triangle(v0, v4, v2)             # 3

# Cap's long base v0-v1 is interior (shared by t0 and t1).
m.assert_edge_shared(v0, v1, 2)

# The flip-target edge v2-v3 already exists (in t2 and also shared with t3? No:
# t3=(v0,v4,v2) edges: v0-v4, v4-v2, v2-v0. No v2-v3 in t3.
# t2=(v2,v3,v4) edges: v2-v3, v3-v4, v4-v2.
# v2-v3 appears only in t2 → n=1 (boundary). Exists → flip is blocked.
m.assert_edge_shared(v2, v3, 1)

# Cap area: 0.5 * 2.0 * 0.0001 = 1e-4.
m.assert_triangle_area_lt(t_cap, 0.001)

# Extreme aspect ratio.
m.assert_triangle_aspect_ratio_gt(t_cap, 1000.0)
