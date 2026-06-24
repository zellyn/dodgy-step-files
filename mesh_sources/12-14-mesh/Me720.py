"""Me720 — Basic_TMesh.safeCoordBackApproximation branch 1: Overlapping-edge detection.

Basic_TMesh.safeCoordBackApproximation Branch 1 (*overlapping-edge detection*) @ line 275:
  'nos = 0; for(e = (Edge *)T.EL.head(); e != NULL; e = e->next()) if(e->overlaps()) nos++;'
  — the algorithm iterates all edges, counts how many overlap, and stores the count in `nos`.
  The fixture demonstrates the geometry that feeds this counter: two coplanar triangles
  (no shared edge) whose interiors overlap after coordinate quantization rounding pushes one
  vertex into the other triangle's area.

Defect pattern: two coplanar triangles in the XY plane whose projected 2D areas overlap.
  t0 is a large triangle; t1 is a smaller triangle whose interior intersects t0's interior
  along a positive-area region. An edge of t1 therefore 'overlaps' t0 according to MeshFix's
  coplanar-intersection test — Branch 1 increments `nos`.

Geometry:
  v0=(0,0,0), v1=(4,0,0), v2=(2,4,0)  — large triangle t0
  v3=(1,1,0), v4=(3,1,0), v5=(2,3,0)  — smaller triangle t1, centred inside t0's area
  t0=(v0,v1,v2), t1=(v3,v4,v5) — t1's interior lies inside t0; their interiors overlap.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me720",
    title="safeCoordBackApproximation overlapping-edge detection: coplanar triangles with overlapping interiors; nos counter incremented (Branch 1)",
    defect_class="self_intersection_coplanar_overlap",
)

# Large triangle in XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(4.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 4.0, 0.0)  # 2 — apex

# Smaller triangle centred inside t0's area; no shared vertices or edges.
v3 = m.vertex(1.0, 1.0, 0.0)  # 3
v4 = m.vertex(3.0, 1.0, 0.0)  # 4
v5 = m.vertex(2.0, 3.0, 0.0)  # 5 — apex

t0 = m.triangle(v0, v1, v2)   # 0: large outer triangle
t1 = m.triangle(v3, v4, v5)   # 1: smaller inner triangle — interiors overlap

# No shared edges between t0 and t1.
m.assert_edge_shared(v0, v1, 1)  # outer edge
m.assert_edge_shared(v1, v2, 1)  # outer edge
m.assert_edge_shared(v0, v2, 1)  # outer edge
m.assert_edge_shared(v3, v4, 1)  # inner edge
m.assert_edge_shared(v4, v5, 1)  # inner edge
m.assert_edge_shared(v3, v5, 1)  # inner edge

# Overlapping coplanar interiors — MeshFix e->overlaps() fires on inner edges.
m.assert_triangles_self_intersect(t0, t1)

# Inner triangle area = 0.5 * |cross| = 0.5 * |(2,0,0)×(1,2,0)| = 0.5 * |(0,0,4)| = 2.0
# Outer triangle area = 0.5 * |(4,0,0)×(2,4,0)| = 0.5 * |(0,0,16)| = 8.0
# t1 is smaller — triangle_area_lt confirms the relative sizing.
m.assert_triangle_area_lt(t1, 3.0)
