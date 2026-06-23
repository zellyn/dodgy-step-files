"""Me274 — autorefine_triangle_soup: segment-intersection-two-point-branch (Branch 5).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 5 @ line 1136:
  'case 2:' — when nbi == 2 the intersection is a line segment (two endpoints);
  if the two points are NOT on a shared edge, the repair creates a new segment
  entry via segments.emplace_back and adds both insertion points to each triangle.

The canonical pattern: two triangles penetrating each other so that their intersection
is a proper line segment (edge penetrates face from one side to the other). The two
intersection points are where the edges of one triangle pierce the face of the other.
Branch 5 checks 'on_same_edge' — if the segment lies on a shared edge it is skipped;
otherwise segments.emplace_back records the crossing.

Geometry: triangle 0 and triangle 1 form an X-shape intersection. t0 is horizontal;
t1 is tilted so that two of its edges pierce t0's face, creating two intersection
points and a crossing segment.

Keywords: case 2:, on_same_edge, segments.emplace_back, two-point intersection.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me274",
             title="autorefine_triangle_soup segment-intersection two-point branch: case 2 segment SI",
             defect_class="autorefine_segment_intersection")

# Triangle 0: horizontal slab.
v0 = m.vertex(-1.0, -1.0, 0.0)  # 0
v1 = m.vertex( 1.0, -1.0, 0.0)  # 1
v2 = m.vertex( 0.0,  1.0, 0.0)  # 2

# Triangle 1: tilted so it crosses t0 (XZ-plane triangle, passing through z=0).
# v3 is below z=0, v4 is below, v5 is above.
# Edge (v3,v5) crosses z=0 inside t0, and edge (v4,v5) crosses z=0 inside t0.
v3 = m.vertex(-0.5,  0.0, -1.0)  # 3 — below plane
v4 = m.vertex( 0.5,  0.0, -1.0)  # 4 — below plane
v5 = m.vertex( 0.0,  0.0,  1.0)  # 5 — above plane

t0 = m.triangle(v0, v1, v2)   # 0 — horizontal
t1 = m.triangle(v3, v4, v5)   # 1 — tilted penetrating triangle

# These two triangles genuinely intersect along a segment.
m.assert_triangles_self_intersect(t0, t1)

# All edges are boundary (soup, no shared edges between t0 and t1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
