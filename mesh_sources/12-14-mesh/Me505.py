"""Me505 — remove_almost_degenerate_faces cap_border_edge: cap triangle whose long opposite edge is on boundary; remove_face path (Branch 6).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 6 (*Cap with border edge*) @ line 1031:
  'if(is_border(opposite(halfedge(cap_v, tmesh), tmesh), tmesh))'
  — after a cap triangle is detected, the algorithm checks whether the cap's long
  "opposite" edge (the edge opposite the cap vertex, connecting the other two vertices)
  is a border edge. If it is, removing the face is safe; otherwise flipping would risk
  creating a non-manifold vertex. The remove_face path is taken.

Defect pattern: an open-boundary mesh where the cap triangle sits at the edge — its
  long base edge (the edge opposite the cap vertex v2) is a boundary edge. The cap
  vertex v2 is nearly on the base line, and the base v0-v1 has no incident triangle
  on the other side.

Geometry (z = 0):
  v0=(0.0, 0.0,    0.0)  — left base
  v1=(2.0, 0.0,    0.0)  — right base; base edge v0-v1 = 2.0 ON BOUNDARY (n=1)
  v2=(1.0, 0.0001, 0.0)  — cap vertex; almost on v0-v1 line

  Cap triangle t0=(v0,v1,v2): edge v0-v1 is the long opposite-cap edge (n=1 → border).
  Support triangles on the cap vertex side:
  v3=(0.0, 1.0, 0.0), v4=(2.0, 1.0, 0.0)
  t1=(v0, v2, v3) — shares edge v0-v2 (interior, n=2) with cap
  t2=(v3, v2, v4) — interior strip
  t3=(v2, v1, v4) — shares edge v1-v2 (interior, n=2) with cap

  The long base v0-v1 has n=1 → is_border → Branch 6 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me505",
    title="remove_almost_degenerate_faces cap_border_edge: cap v2=(1,0.0001,0); long base v0-v1 on boundary (n=1); remove_face path (Branch 6)",
    defect_class="cap_triangle",
)

v0 = m.vertex(0.0, 0.0,    0.0)   # 0 — left base
v1 = m.vertex(2.0, 0.0,    0.0)   # 1 — right base; base edge = 2.0 on boundary
v2 = m.vertex(1.0, 0.0001, 0.0)   # 2 — cap vertex (almost on v0-v1)

# Support vertices above the base.
v3 = m.vertex(0.0, 1.0,    0.0)   # 3
v4 = m.vertex(2.0, 1.0,    0.0)   # 4

# Cap triangle (index 0): long base v0-v1 has n=1 (boundary).
t_cap = m.triangle(v0, v1, v2)    # 0

# Support triangles on the upper side; share the long edges of the cap.
m.triangle(v0, v2, v3)             # 1 — shares edge v0-v2 with cap
m.triangle(v3, v2, v4)             # 2 — interior strip above
m.triangle(v2, v1, v4)             # 3 — shares edge v1-v2 with cap

# Long base v0-v1 is a boundary edge: only t0 uses it.
m.assert_edge_shared(v0, v1, 1)

# The long edges of the cap are interior.
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)

# Cap area: 0.5 * 2.0 * 0.0001 = 1e-4.
m.assert_triangle_area_lt(t_cap, 0.001)

# Extreme aspect ratio (long base vs tiny height).
m.assert_triangle_aspect_ratio_gt(t_cap, 1000.0)
