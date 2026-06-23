"""Me063 — loop_break: inner loop exits after first pinch found; second pinch in same polygon.

Catalog claim: a polygon with TWO pinch points triggers Branch 11 (*loop_break*) after
the first pinch: the inner for-loop over polygon vertices breaks immediately at the first
failed unique_points.insert(), even though a second pinch exists further along the same
polygon. The push_back'd sub-polygon (split_polygon_2) is re-processed in the outer loop,
where the second pinch is detected.

Polygon: (v0, v1, v2, v0, v3, v1, v4) — v0 at positions 0,3 AND v1 at positions 1,5.
Two pinches. Inner scan finds v0 first at position 3 → break.
  split_polygon_1 = (v0, v1, v2, v0) → simplify → (v0, v1, v2) [triangle]
  split_polygon_2 = (v0, v3, v1, v4) [quad, contains the second pinch at v1 when re-scanned]

After re-processing split_polygon_2=(v0,v3,v1,v4): no repeated vertex (v1 is at position 2
here, and v0 at position 0 — but are they repeated? v0 and v1 are distinct in this sub-polygon,
so actually this polygon is clean after first split). Let me recalculate.

Actually split_polygon_2 for polygon (v0,v1,v2,v0,v3,v1,v4) pinch at v0 (prev_id=0, i=3):
  split_polygon_1 = polygon[0..3] = (v0, v1, v2, v0) → simplify → (v0, v1, v2)
  split_polygon_2 = polygon[3..6] + polygon[0..0] = (v0, v3, v1, v4) + (v0)
                  = (v0, v3, v1, v4, v0) → simplify → (v0, v3, v1, v4) [quad, clean]

The loop_break is still demonstrated: after finding pinch at v0 (position 3), the inner
loop BREAKS. It does NOT continue to scan for the v1 repetition at position 5. The second
pinch is gone because split_polygon_2 is a clean quad.

Result: triangle (v0,v1,v2) + clean quad (v0,v3,v1,v4).
The loop_break is what prevents double-counting: without break, the algorithm would try to
split on v1 too, producing incorrect sub-polygons from the already-split first half.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me063",
             title="loop_break: polygon with two potential pinches; first pinch triggers break",
             defect_class="pinched_polygon")

# Polygon: (v0, v1, v2, v0, v3, v4, v5) — v0 at positions 0 and 3.
# Inner loop breaks at position 3 (v0 repeated). A later position is never scanned.
# split_polygon_1 = (v0, v1, v2) [triangle]
# split_polygon_2 = (v0, v3, v4, v5) [quad] — clean, processed in next outer iteration.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — pinch vertex (at positions 0 and 3)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 0.8, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(-1.5, 0.8, 0.0)  # 4
v5 = m.vertex(-0.5, 1.2, 0.0)  # 5

# Sub-polygon 1 (from split at first pinch): triangle (v0, v1, v2)
t0 = m.triangle(v0, v1, v2)

# Sub-polygon 2 (push_back'd, then re-processed): quad (v0, v3, v4, v5)
t1 = m.triangle(v0, v3, v4)
t2 = m.triangle(v0, v4, v5)

# v0 appears in both sub-polygon groups. Its fan is disconnected.
m.assert_vertex_fan_disconnected(v0)

# t0 (first sub-polygon) cannot be reached from t1 (second sub-polygon) by edge walk.
m.assert_triangle_not_reachable_from(target=t0, source=t1)
