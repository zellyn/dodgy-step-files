"""Me275 — autorefine_triangle_soup: polygon-intersection-multi-point-branch (Branch 6).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 6 @ line 1155:
  'default:' — when nbi >= 3 the intersection is a polygon; the repair iterates
  over all intersection points via 'ipt_ids1[i]' / 'ipt_ids2[i]' and creates
  polygon boundary segments for all consecutive point pairs.

The input pattern: two coplanar triangles that overlap in a region larger than a
point or segment. The intersection polygon has 3 or more vertices and the default
branch constructs segment entries for every consecutive pair around the polygon.

Geometry: two coplanar triangles in z=0 that partially overlap, forming a quadrilateral
intersection region (4 intersection points = 4 polygon boundary segments). This
coplanar overlap triggers the default case (nbi >= 3, specifically 4 here).

Keywords: default:, ipt_ids1[i], ipt_ids2[i], polygon intersection.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me275",
             title="autorefine_triangle_soup polygon-intersection default branch: nbi>=3 coplanar overlap",
             defect_class="autorefine_polygon_intersection")

# Triangle 0: left-leaning triangle in z=0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 3.0, 0.0)   # 2

# Triangle 1: overlapping triangle in z=0 (same plane).
# Shifted right: intersection is a quadrilateral-ish region.
v3 = m.vertex(1.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(2.0, 3.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v3, v4, v5)   # 1

# These two coplanar triangles overlap in their interiors (polygon intersection).
m.assert_triangles_self_intersect(t0, t1)
