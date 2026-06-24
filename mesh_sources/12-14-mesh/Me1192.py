"""Me1192 — does_polygon_soup_self_intersect intersection_detection:
  triangle_soup_self_intersections fires and returns true (Branch 3).

CGAL PMP `PMP.does_polygon_soup_self_intersect` Branch 3 (*intersection_detection*)
  @ line 50:
  'return !triangle_soup_self_intersections(points, polygons, out, np).empty()' —
  After merging duplicate points (Branch 1) and triangulating mixed polygons
  (Branch 2), Branch 3 calls the pairwise triangle soup intersection check.
  If any pair of triangles intersects, the returned range is non-empty and
  does_polygon_soup_self_intersect returns true.

Defect pattern: two triangles that cross each other in 3D. T0 lies in the XZ
  plane; T1 lies in the YZ plane; they share the Z-axis segment and their
  interiors pierce each other near the origin. This is a classic X-intersection
  pattern. Branch 3 fires when triangle_soup_self_intersections returns the
  crossing pair, making the non-empty check true.

Geometry:
  T0: v0=(-1,0,0), v1=(1,0,0), v2=(0,0,1) — in XZ plane (y=0)
  T1: v3=(0,-1,0), v4=(0,1,0), v5=(0,0,1) — in YZ plane (x=0)
  The two triangles share vertex v2==v5 at (0,0,1) and their interiors cross
  near the origin — self-intersection pattern.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1192",
    title="does_polygon_soup_self_intersect intersection_detection: two crossing triangles trigger triangle_soup_self_intersections returning non-empty; does_self_intersect=true (Branch 3)",
    defect_class="self_intersection",
)

# Triangle T0 in XZ plane (y=0)
v0 = m.vertex(-1.0, 0.0, 0.0)   # 0
v1 = m.vertex( 1.0, 0.0, 0.0)   # 1
v2 = m.vertex( 0.0, 0.0, 1.0)   # 2 — shared apex

# Triangle T1 in YZ plane (x=0)
v3 = m.vertex(0.0, -1.0, 0.0)   # 3
v4 = m.vertex(0.0,  1.0, 0.0)   # 4
v5 = m.vertex(0.0,  0.0, 1.0)   # 5 — shared apex (same position as v2)

t0 = m.triangle(v0, v1, v2)    # 0: XZ triangle
t1 = m.triangle(v3, v4, v5)    # 1: YZ triangle

# These two triangles geometrically intersect
m.assert_triangles_self_intersect(t0, t1)

# The apex positions are coincident (same spatial point, different indices)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# Edge counts: each edge appears in exactly one triangle
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)

# V=6, E=6, F=2, chi=2
m.assert_euler_characteristic(6, 6, 2, 2)
