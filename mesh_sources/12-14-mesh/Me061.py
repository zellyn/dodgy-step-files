"""Me061 — split_polygon_1: first sub-polygon extracted at split boundary (prev_id..i).

Catalog claim: a 6-point polygon (v0,v1,v2,v3,v2,v4) has vertex v2 repeated at
positions 2 and 4. CGAL PMP.split_pinched_polygons_in_polygon_soup Branch 7
(*split_polygon_1*) fires: the first sub-polygon is constructed as
Polygon_3(polygon.begin() + prev_id, polygon.begin() + i+1), i.e. the slice
from position 2 to position 4 inclusive → (v2, v3, v2) — but wait, pinch is
at position 4 which repeats position 2 (prev_id=2, i=4).

Corrected: polygon = (v0, v1, v2, v3, v2, v4)
  unique_points scan hits position 4 (v2) which was first seen at prev_id=2.
  split_polygon_1 = polygon[prev_id..i] = (v2, v3) — too small (size 2, skipped).

Better construction: polygon = (v0, v1, v2, v1, v3, v4) — v1 repeats at position 3.
  prev_id=1, i=3
  split_polygon_1 = polygon[1..3] = (v1, v2, v1) — still degenerate.

Best: polygon = (v0, v1, v2, v3, v0, v4) — v0 at positions 0 and 4.
  prev_id=0, i=4
  split_polygon_1 = polygon[0..4] = (v0, v1, v2, v3, v0) — 5 vertices with repeated
    first/last, which simplify_polygon would remove the last → (v0, v1, v2, v3).
  split_polygon_2 = polygon[0..0] + polygon[4..end] = (v0) + (v0, v4) → (v0, v4) + wrap.

Re-reading the algorithm:
  split_polygon_1 = Polygon_3(polygon.begin()+prev_id, polygon.begin()+i+1)
                  = polygon[prev_id..i] inclusive
  For polygon=(v0,v1,v2,v3,v0,v4), prev_id=0, i=4:
    split_polygon_1 = (v0,v1,v2,v3,v0) — 5 elements, last==first, simplifies to quad (v0,v1,v2,v3)
  split_polygon_2 = begin..prev_id + i..end:
    = polygon[0..0] + polygon[4..5] = (v0) + (v0,v4) = (v0, v0, v4) → simplifies to (v0,v4) = degenerate

Hmm, the split_polygon_2 wraps beginning..prev_id + i..end. For prev_id=0:
  split_polygon_2 = polygon[i..end] + polygon[begin..prev_id]
  = (v0, v4) + (v0) → but duplicate v0. After simplify: (v0, v4) — too small (2 vertices).

The typical pinch: a polygon like (v0,v1,v2,v3,v1,v4,v5) — v1 at positions 1 and 4.
  prev_id=1, i=4
  split_polygon_1 = (v1, v2, v3, v1) → simplifies to (v1, v2, v3) [triangle]
  split_polygon_2 = polygon[0..1] + polygon[4..6] = (v0,v1) + (v1,v4,v5) → (v0,v1,v1,v4,v5)
    simplifies to (v0,v1,v4,v5) [quad]

This fixture models the above: heptagonal polygon pinched at v1 (positions 1 and 4).
Two results: triangle (v1,v2,v3) and quad (v0,v1,v4,v5).
The quad is then triangulated as (v0,v1,v4) + (v0,v4,v5) for our triangle mesh.

This demonstrates split_polygon_1 (the triangle part) being correctly bounded.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me061",
             title="split_polygon_1: heptagon pinched at v1 (pos 1 and 4) → triangle + quad sub-polygons",
             defect_class="pinched_polygon")

# Heptagon: (v0, v1, v2, v3, v1, v4, v5) — v1 repeated at positions 1 and 4.
# After split_polygon_1 fires: first result = (v1, v2, v3)  [triangle]
# After split_polygon_2:       second result = (v0, v1, v4, v5) [quad → 2 tris]
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — pinch vertex (prev_id=1, i=4)
v2 = m.vertex(1.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, 1.5, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# Sub-polygon 1 (split_polygon_1): triangle (v1, v2, v3)
t0 = m.triangle(v1, v2, v3)

# Sub-polygon 2 (split_polygon_2): quad (v0, v1, v4, v5) → triangulated as:
t1 = m.triangle(v0, v1, v4)
t2 = m.triangle(v0, v4, v5)

# v1 (the pinch vertex) is shared by triangle t0 (sub-polygon 1) and
# triangle t1 (sub-polygon 2). Its fan should be disconnected because
# the two sub-polygons share only the pinch point, not an edge.
m.assert_vertex_fan_disconnected(v1)

# t0 (from split_polygon_1) cannot be reached from t1 (from split_polygon_2)
# by edge-walking because they share no edge — only the pinch vertex.
m.assert_triangle_not_reachable_from(target=t0, source=t1)
