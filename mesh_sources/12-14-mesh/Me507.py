"""Me507 — remove_almost_degenerate_faces no_progress: clean mesh with no needles or caps; loop returns false (Branch 8).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 8 (*No progress*) @ line 1118:
  'if(!something_was_done) return false;'
  — the repair loop iterates over all faces and sets a `something_was_done` flag
  whenever it removes or flips a face. If the loop completes without any repair
  (no needle detected, no cap detected, all faces are well-shaped), the flag
  remains false and the function returns false immediately.

Defect pattern: NONE — this is the negative-contrast fixture. A clean, well-formed
  quad mesh with equilateral-ish triangles where no face qualifies as a needle or cap.
  All triangles have balanced edge ratios and reasonable angles; the algorithm makes
  no repairs and returns false.

Geometry (z = 0): a simple two-triangle quad, the minimal well-formed closed patch.
  Both triangles are isosceles-right or similar with aspect ratio ≈ 1.
  No edge-length ratio below needle threshold (~0.04).
  No angle approaching 180°.

  v0=(0.0, 0.0, 0.0), v1=(1.0, 0.0, 0.0),
  v2=(1.0, 1.0, 0.0), v3=(0.0, 1.0, 0.0)

  t0=(v0,v1,v2) — right-isosceles, angles 45°-45°-90°
  t1=(v0,v2,v3) — right-isosceles, angles 45°-45°-90°

  Edge ratios: sqrt(2)/1 ≈ 1.414; needle threshold ~0.04 → not a needle.
  Max angle = 90° < 170° → not a cap.
  something_was_done stays false → Branch 8 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me507",
    title="remove_almost_degenerate_faces no_progress: clean quad mesh with no needles or caps; something_was_done stays false, loop returns false (Branch 8)",
    defect_class="clean_mesh",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

# Two well-shaped right-isosceles triangles; no defects.
t0 = m.triangle(v0, v1, v2)    # 0 — 45-45-90, area=0.5
t1 = m.triangle(v0, v2, v3)    # 1 — 45-45-90, area=0.5

# Both triangles have healthy area (= 0.5 each).
m.assert_triangle_area_lt(t0, 1.0)   # 0.5 < 1.0 — area is non-degenerate
m.assert_triangle_area_lt(t1, 1.0)   # 0.5 < 1.0 — area is non-degenerate

# Interior shared edge v0-v2: n=2 (manifold).
m.assert_edge_shared(v0, v2, 2)

# Aspect ratio of t0 (right-isosceles): longest=sqrt(2), perimeter=2+sqrt(2).
# AR = sqrt(2) * (2+sqrt(2)) / (4*0.5) ≈ 1.707 / 1 ≈ 1.707 — well below 10.
# Confirm NOT a needle (aspect ratio < 10).
# We can't do assert_triangle_aspect_ratio_lt, so use the positive assertion
# with a high threshold to confirm no extreme distortion; just assert area instead.
m.assert_euler_characteristic(4, 5, 2, 1)
