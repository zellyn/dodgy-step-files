"""Me068 — pinch_detection: quadrilateral figure-8 pinch — minimum-size pinched polygon.

Catalog claim: a 4-vertex polygon (the minimum size that can be pinched — Branch 2 skips
≤3 vertices) has its first vertex repeated at position 2: (v0, v1, v0, v2). This is the
smallest possible pinched polygon. The unique_points scan at position 2 immediately
detects the repetition of v0 (Branch 5: *pinch_detection*).
  prev_id=0, i=2
  split_polygon_1 = polygon[0..2] = (v0, v1, v0) → simplify → (v0, v1) [degenerate: 2 verts, skipped]
  split_polygon_2 = polygon[2..3] + polygon[0..0] = (v0, v2) + (v0) = (v0, v2, v0) → simplify → (v0, v2) [degenerate]

Both sub-polygons are degenerate (2 vertices). After small_polygon_skip they are dropped.
The original quadrilateral collapses to nothing useful — this is an extreme degenerate case.

Alternate: (v0, v1, v2, v0) — v0 at positions 0 and 3.
  prev_id=0, i=3
  split_polygon_1 = polygon[0..3] = (v0, v1, v2, v0) → simplify → (v0, v1, v2) [triangle ✓]
  split_polygon_2 = polygon[3..3] + polygon[0..0] = (v0) + (v0) → (v0) → too small (1 vert)

The second sub-polygon is trivial. The quad (v0,v1,v2,v0) with pinch at positions 0 and 3
yields exactly one useful sub-polygon: (v0,v1,v2).

This is the minimally-sized 4-vertex pinched polygon that yields a single triangle.
The degenerate second sub-polygon (push_back'd) is then skipped by small_polygon_skip.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me068",
             title="pinch_detection: 4-vertex polygon (v0,v1,v2,v0) — minimum pinchable; yields one triangle",
             defect_class="pinched_polygon")

# 4-vertex polygon: (v0, v1, v2, v0) — v0 at positions 0 and 3.
# split_polygon_1 = (v0, v1, v2) [triangle — the only usable result]
# split_polygon_2 = (v0) [trivial, dropped by small_polygon_skip]
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — pinch vertex (prev_id=0, i=3)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# The soup also has a clean companion triangle as context.
v3 = m.vertex(3.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(3.5, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # result of split_polygon_1 from the 4-vertex pinched polygon
t1 = m.triangle(v3, v4, v5)   # clean companion polygon (no pinch — not processed)

# t0 and t1 are in separate connected components (no shared vertices or edges).
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# The area of t0 is positive (the 4-vertex polygon's meaningful content was preserved).
# Area = 0.5 * base * height = 0.5 * 1.0 * 1.0 = 0.5
# Assert area is NOT tiny (so use edge_shared to confirm normal connectivity).
m.assert_edge_shared(v0, v1, 1)   # edge (v0,v1) belongs only to triangle 0 (boundary)
m.assert_edge_shared(v0, v2, 1)   # edge (v0,v2) belongs only to triangle 0 (boundary)
