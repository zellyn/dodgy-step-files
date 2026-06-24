"""Me504 — remove_almost_degenerate_faces cap_triangle: angle near 180° triggers is_cap_triangle_face (Branch 5).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 5 (*Cap triangle*) @ line 1005:
  'if(is_cap_triangle_face(...))'
  — a cap triangle has one very obtuse angle (near 180°): the "cap vertex" lies almost
  on the line segment between the other two vertices. The cap threshold defaults to
  cos(170°) ≈ -0.985. When max_angle > cap_threshold, the face is a cap and is
  marked for edge flip.

Defect pattern: a nearly-flat triangle where the apex vertex v2 is only 0.0001 above
  the base midpoint. The angle at v2 is arccos(≈-1) ≈ 180°. Four support triangles
  surround the cap to give it topological context.

Geometry (z = 0):
  v0=(0.0, 0.0,    0.0)  — left base
  v1=(2.0, 0.0,    0.0)  — right base; base edge = 2.0 (the "opposite" long edge)
  v2=(1.0, 0.0001, 0.0)  — cap vertex; 0.0001 above midpoint

  Angle at v2:
    vec v2→v0 = (-1.0, -0.0001, 0), |·| ≈ 1.000000005
    vec v2→v1 = (+1.0, -0.0001, 0), |·| ≈ 1.000000005
    dot = -1.0 + 1e-8 ≈ -1.0 → cos ≈ -1 → angle ≈ 180° → is_cap!

  Area = 0.5 * 2.0 * 0.0001 = 0.0001.
  Aspect ratio ≈ 2.0 * (2.0+1+1) / (4 * 0.0001) = 2*4/0.0004 = 20000.

  Support triangles (below the base):
  v3=(0.0, -1.0, 0.0), v4=(2.0, -1.0, 0.0)
  t1=(v0, v3, v4), t2=(v0, v4, v1) — healthy lower strip
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me504",
    title="remove_almost_degenerate_faces cap_triangle: v2=(1,0.0001,0) almost on base v0-v1; angle at v2 ≈180° triggers is_cap_triangle_face (Branch 5)",
    defect_class="cap_triangle",
)

v0 = m.vertex(0.0, 0.0,    0.0)   # 0 — left base
v1 = m.vertex(2.0, 0.0,    0.0)   # 1 — right base (long edge v0-v1 = 2.0)
v2 = m.vertex(1.0, 0.0001, 0.0)   # 2 — cap vertex; just 0.0001 above midpoint

# Support vertices below the base.
v3 = m.vertex(0.0, -1.0,   0.0)   # 3
v4 = m.vertex(2.0, -1.0,   0.0)   # 4

# Cap triangle (index 0): angle at v2 ≈ 180°.
t_cap = m.triangle(v0, v1, v2)    # 0

# Healthy support triangles below.
m.triangle(v0, v3, v4)             # 1
m.triangle(v0, v4, v1)             # 2

# Cap area: 0.5 * 2.0 * 0.0001 = 1e-4.
m.assert_triangle_area_lt(t_cap, 0.001)

# Cap vertex v2 is extremely close to the base line (y=0); the distance
# from v2=(1,0.0001,0) to v0=(0,0,0) is sqrt(1+1e-8) ≈ 1.000000005.
# Proxy: v2 is much closer to the midpoint of v0-v1 than either base vertex.
# Use vertex_pair_distance_lt(v2 projected) — but we cannot project in oracle.
# Instead use the fact that the height (y-coordinate) of v2 is tiny relative to
# the base (0.0001 / 2.0 = 0.005%), captured by the extreme aspect ratio.
m.assert_triangle_aspect_ratio_gt(t_cap, 1000.0)
