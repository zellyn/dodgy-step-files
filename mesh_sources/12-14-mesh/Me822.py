"""Me822 — does_polygon_soup_self_intersect branch 3: intersection_detection.

PMP.does_polygon_soup_self_intersect Branch 3 (*intersection_detection*) @ line 50:
  After duplicate-point merging and triangulation, the function calls
  `triangle_soup_self_intersections(points, triangles, …)` to find all pairwise
  intersections in the soup.  Branch 3 fires whenever the soup contains at least
  one pair of geometrically crossing triangles — i.e. the result of
  `triangle_soup_self_intersections` is non-empty.

This branch is the direct sibling of the face-level `do_faces_intersect` check
(Me390-Me396) but operates on the raw polygon soup before it is converted to a
half-edge mesh.  The fixture reproduces the canonical X-shaped crossing pair used
throughout the SI series: two triangles in orthogonal planes that share a common
apex and whose interiors pierce each other along an interior segment.

Geometry:
  v0=(0,0,0) — shared apex
  v1=(1,1,0),  v2=(1,-1,0)  — XY-plane fan (t0)
  v3=(1,0,1),  v4=(1,0,-1)  — XZ-plane fan (t1)
  t0=(v0,v1,v2): triangle in XY plane
  t1=(v0,v3,v4): triangle in XZ plane; pierces t0 along the x-axis segment

  Two clean triangles 20 units away confirm that soup-level SI is localised:
  v5=(0,20,0), v6=(1,20,0), v7=(0,21,0)
  v8=(0,22,0), v9=(1,22,0), v10=(0,23,0)
  t2=(v5,v6,v7), t3=(v8,v9,v10): clean companions
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me822",
    title="does_polygon_soup_self_intersect intersection_detection: crossing XY/XZ triangle pair in soup triggers triangle_soup_self_intersections (Branch 3)",
    defect_class="self_intersection",
)

# Crossing pair — classic SI kernel from Me020/Me390.
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared apex
v1 = m.vertex(1.0,  1.0,  0.0)   # 1
v2 = m.vertex(1.0, -1.0,  0.0)   # 2
v3 = m.vertex(1.0,  0.0,  1.0)   # 3
v4 = m.vertex(1.0,  0.0, -1.0)   # 4

t0 = m.triangle(v0, v1, v2)      # 0: XY-plane triangle
t1 = m.triangle(v0, v3, v4)      # 1: XZ-plane triangle; crosses t0

# Clean companions far away — confirm the SI is localised to the soup pair.
v5  = m.vertex(0.0, 20.0, 0.0)   # 5
v6  = m.vertex(1.0, 20.0, 0.0)   # 6
v7  = m.vertex(0.0, 21.0, 0.0)   # 7
v8  = m.vertex(0.0, 22.0, 0.0)   # 8
v9  = m.vertex(1.0, 22.0, 0.0)   # 9
v10 = m.vertex(0.0, 23.0, 0.0)   # 10

t2 = m.triangle(v5,  v6,  v7)    # 2: clean companion A
t3 = m.triangle(v8,  v9,  v10)   # 3: clean companion B

# The crossing pair is the SI nucleus that causes triangle_soup_self_intersections
# to return a non-empty result (Branch 3 fires).
m.assert_triangles_self_intersect(t0, t1)

# Clean companions have no SI with each other or with the crossing pair.
m.assert_triangles_do_not_intersect(t2, t3)
m.assert_triangle_not_reachable_from(t2, t0)
