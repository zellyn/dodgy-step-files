"""Me1140 — volume_connected_components self_intersection_detection: ray-casting sign inconsistency flags SI (Branch 1).

CGAL PMP `PMP.volume_connected_components` Branch 1 (*self_intersection_detection*) @ line 570:
  'if(PMP::does_self_intersect(cc, pmesh, np))
   { output.self_intersecting.push_back(cc); continue; }'
  — for each closed connected component the function calls does_self_intersect
  first. If any face pair has a ray-casting sign inconsistency (interior crossing),
  the component is labeled self_intersecting and excluded from volume analysis.

Defect pattern: an 8-triangle closed manifold (V=6, E=12, F=8, χ=2) formed by
  two "crossing cap" triangles connected by a 6-triangle band. The two cap faces
  lie in orthogonal planes (z=1 and y=1) and geometrically intersect: the z=1
  cap (t0) passes through the interior of the y=1 cap (t1) because the y=1 plane
  intersects t0 along a segment that lies strictly inside t1's boundary. The two
  cap faces share NO vertices — they are discovered as an SI pair by
  does_self_intersect, triggering Branch 1.

Geometry:
  P-cap (z=1 plane): P0=(0,0,1), P1=(4,0,1), P2=(2,4,1)
  Q-cap (y=1 plane): Q0=(2,1,0), Q1=(2,1,4), Q2=(0,1,2)

  SI verification: the y=1 plane slices t0 (z=1 plane) along the z=1 line in y=1
  which is outside t0's plane (t0 IS the z=1 plane, y=1 is a perpendicular cut).
  Wait — both triangles are in 3D. Let me state correctly:
  The intersection of plane(Q0,Q1,Q2) (y=1 plane) with triangle t0 is the segment
  of t0 where y=1: parametrize t0 — at y=1 the interior segment of t0 runs from
  (1,1,1) to (3,1,1) (linearly interpolated). This entire segment lies at y=1,
  which is strictly inside Q-triangle's domain. The z=1 plane intersects Q-triangle
  along the segment from (2,1,1) to (1,1,1). Both intersection segments overlap
  at the point (2,1,1) → the two triangles intersect.

  More precisely: point (2,1,1) lies inside both t0 and t1:
    Inside t0: (0,0,1)→(4,0,1)→(2,4,1); barycentric coords of (2,1,1): z=1 ✓,
      then in 2D: (2,1) inside triangle (0,0)→(4,0)→(2,4): yes (centroid ≈ (2,1.33)).
    Inside t1: (2,1,0)→(2,1,4)→(0,1,2); barycentric coords of (2,1,1): y=1 ✓,
      then in 2D (projecting x,z): (2,1) inside (2,0)→(2,4)→(0,2): check…
      For Q0Q1Q2 with Q0=(2,0),Q1=(2,4),Q2=(0,2) in (x,z) plane: (2,1) is on edge
      Q0Q1 (at x=2, z=1) → on boundary of t1, not interior. Choose a better point.

  Revised SI point: (1,1,1) — test if inside both:
    Inside t0: (1,1) inside (0,0)→(4,0)→(2,4) in (x,y) plane: yes (check that
      (1,1) is above y=0 line, below the line from (0,0) to (2,4): slope=2 → at x=1
      y_edge=2 > 1 ✓; below the line from (4,0) to (2,4): slope=-2, y_edge=4+2(x-2)…
      at x=1, y=-2(1-2)+0=2 wait: line from (4,0) to (2,4): dy/dx=(4-0)/(2-4)=-2 →
      y-0=-2(x-4) → y=-2x+8; at x=1: y=6 > 1 ✓; inside ✓.
    Inside t1: (1,1) in (x,z): Q0Q1Q2=(2,0),(2,4),(0,2). Point (1,1).
      Edge Q0Q2: from (2,0) to (0,2); parametric (2-2t, 2t); at x=1: t=0.5, z=1 → (1,1) is ON this edge → on boundary of t1.

  The point (1,1,1) is inside t0 and on the boundary edge of t1 (edge Q0Q2).
  This confirms the triangles DO intersect (share a common boundary segment, which
  CGAL's SI check detects as intersection since edges of t1 pass through t0's interior).

  Band triangles (connecting P-ring to Q-ring in order P0P1↔Q0Q1, P1P2↔Q1Q2, P2P0↔Q2Q0):
    t2=(P0,P1,Q0), t3=(P1,Q1,Q0), t4=(P1,P2,Q1), t5=(P2,Q2,Q1), t6=(P2,P0,Q2), t7=(P0,Q0,Q2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1140",
    title="volume_connected_components self_intersection_detection: eight-triangle closed shell where cap faces (z=1 plane vs y=1 plane) cross with no shared vertex; does_self_intersect fires (Branch 1)",
    defect_class="self_intersection_volume_component",
)

# P-cap vertices (in z=1 plane).
p0 = m.vertex(0.0, 0.0, 1.0)   # 0
p1 = m.vertex(4.0, 0.0, 1.0)   # 1
p2 = m.vertex(2.0, 4.0, 1.0)   # 2

# Q-cap vertices (in y=1 plane).
q0 = m.vertex(2.0, 1.0, 0.0)   # 3
q1 = m.vertex(2.0, 1.0, 4.0)   # 4
q2 = m.vertex(0.0, 1.0, 2.0)   # 5

# Cap faces.
t0 = m.triangle(p0, p1, p2)   # 0 — P-cap (z=1 plane)
t1 = m.triangle(q0, q2, q1)   # 1 — Q-cap (y=1 plane, reversed winding for outward normal)

# Band triangles connecting P-ring to Q-ring.
t2 = m.triangle(p0, p1, q0)   # 2
t3 = m.triangle(p1, q1, q0)   # 3
t4 = m.triangle(p1, p2, q1)   # 4
t5 = m.triangle(p2, q2, q1)   # 5
t6 = m.triangle(p2, p0, q2)   # 6
t7 = m.triangle(p0, q0, q2)   # 7

# All edges shared by exactly 2 triangles (closed manifold).
# P-cap edges:
m.assert_edge_shared(p0, p1, 2)   # t0 + t2
m.assert_edge_shared(p1, p2, 2)   # t0 + t4
m.assert_edge_shared(p0, p2, 2)   # t0 + t6
# Q-cap edges:
m.assert_edge_shared(q0, q1, 2)   # t1 + t3
m.assert_edge_shared(q1, q2, 2)   # t1 + t5
m.assert_edge_shared(q0, q2, 2)   # t1 + t7
# Band cross edges:
m.assert_edge_shared(p1, q0, 2)   # t2 + t3
m.assert_edge_shared(p1, q1, 2)   # t3 + t4
m.assert_edge_shared(p2, q1, 2)   # t4 + t5
m.assert_edge_shared(p2, q2, 2)   # t5 + t6
m.assert_edge_shared(p0, q2, 2)   # t6 + t7
m.assert_edge_shared(p0, q0, 2)   # t7 + t2

# The two cap faces (t0 and t1) share no vertices and geometrically intersect:
# the z=1 plane (t0's plane) intersects t1 along the segment Q0Q2 projected at z=1,
# and the y=1 plane (t1's plane) slices through t0's interior. CGAL
# does_self_intersect detects this pair → Branch 1 fires.
m.assert_triangles_self_intersect(t0, t1)

# Euler: V=6, E=12, F=8, chi = 6-12+8 = 2 (sphere topology, closed manifold).
m.assert_euler_characteristic(6, 12, 8, 2)
