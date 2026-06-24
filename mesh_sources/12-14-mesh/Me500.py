"""Me500 — remove_almost_degenerate_faces needle_triangle: extreme edge-length ratio triggers is_needle_triangle_face (Branch 1).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 1 (*Needle triangle*) @ line 1022:
  'if(is_needle_triangle_face(...))'
  — each face is tested for an extreme ratio of shortest to longest edge. When the
  ratio falls below the needle threshold (default ~0.04), the face is a needle and
  the shortest edge is collapsed.

Defect pattern: a needle triangle with one very short edge (0.001) and two long
  edges (~1.0). Edge-length ratio ≈ 0.001 — well below the threshold. Three
  support triangles complete a strip to give the defect topological context.

Geometry (z = 0):
  v0=(0.0,   0.0, 0.0)  — origin
  v1=(0.001, 0.0, 0.0)  — 0.001 units from v0; edge v0-v1 is the needle's short edge
  v2=(0.5,   0.866, 0.0) — apex; |v0-v2| ≈ 1.0, |v1-v2| ≈ 1.0

  Needle triangle t0 = (v0, v1, v2):
    shortest edge v0-v1 = 0.001
    long edges v0-v2 ≈ v1-v2 ≈ 1.0
    aspect ratio ≈ 1.0 / 0.001 = 1000

  Support strip (healthy triangles):
  v3=(0.0, -0.5, 0.0), v4=(0.001, -0.5, 0.0)
  t1=(v0, v3, v1), t2=(v3, v4, v1)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me500",
    title="remove_almost_degenerate_faces needle_triangle: edge v0-v1=0.001 vs long edges ~1.0; ratio 1000:1 triggers is_needle_triangle_face (Branch 1)",
    defect_class="needle_triangle",
)

# Needle triangle vertices.
v0 = m.vertex(0.0,   0.0,   0.0)   # 0
v1 = m.vertex(0.001, 0.0,   0.0)   # 1 — 0.001 from v0; needle short edge
v2 = m.vertex(0.5,   0.866, 0.0)   # 2 — apex; both v0-v2 and v1-v2 ≈ 1.0

# Needle triangle (index 0).
t_needle = m.triangle(v0, v1, v2)  # 0

# Support triangles to give topological context below the needle.
v3 = m.vertex(0.0,   -0.5, 0.0)   # 3
v4 = m.vertex(0.001, -0.5, 0.0)   # 4
m.triangle(v0, v3, v1)             # 1 — healthy
m.triangle(v3, v4, v1)             # 2 — healthy

# Short edge of the needle: v0-v1 distance = 0.001.
m.assert_vertex_pair_distance_lt(v0, v1, 0.002)

# Needle triangle has very small area: 0.5 * 0.001 * 0.866 ≈ 4.33e-4.
m.assert_triangle_area_lt(t_needle, 0.01)

# Extreme aspect ratio: longest_edge * perimeter / (4 * area) ≈ 1.0 * 2.001 / (4 * 4.33e-4) ≈ 1155.
m.assert_triangle_aspect_ratio_gt(t_needle, 100.0)
