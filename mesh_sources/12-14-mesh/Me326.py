"""Me326 — with_third_points_cdt2_path_conditional: CDT path taken when use_cdt true and not compile-disabled (Branch 7).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 7 (*cdt2_path_conditional*) @ line 767:
  'if (use_cdt) {'
  '  … triangulate_hole_polyline_with_cdt(points, third_points, out, …, max_squared_distance);'
  '  if (success) return out;  // early exit'
  When use_cdt is true (and not compile-time disabled), CGAL computes the bbox
  to derive max_squared_distance, then calls the CDT-based hole filler.
  On success it returns immediately without reaching the DT3/cubic path.

Defect pattern: a triangular interior hole with all three boundary edges
  incident on exactly one existing triangle (true open boundary in the mesh).
  This is the archetypal CDT input: a closed planar hole bounded by mesh edges
  whose other half-edges have no triangle.

Geometry: a diamond/rhombus mesh with a central triangular hole.
  Outer diamond: v0=(1,0,0), v1=(0,1,0), v2=(-1,0,0), v3=(0,-1,0).
  Hole vertices: v4=(0.3,0,0), v5=(0,0.3,0), v6=(0,0,0.3) (near-hub).
  The outer diamond is triangulated into 4 outer triangles plus 3 "shell"
  triangles surrounding the hole; the hole (v4,v5,v6) is unfilled.

  Simpler design: 3-triangle ring around the hole.
  Outer ring vertices: v0=(1,0,0), v1=(0,1,0), v2=(-0.5,-0.5,0).
  Hole boundary vertices: v3=(0.2,0,0), v4=(0,0.2,0), v5=(-0.1,-0.1,0).
  3 "wedge" triangles: t0=(v0,v1,v3), t1=(v1,v2,v4), t2=(v2,v0,v5).
  — These don't share hole-boundary edges cleanly.

  Cleanest: use a triangulated hexagon with a central triangular hole.
  Outer triangle: v0=(0,2,0), v1=(-1.732,-1,0), v2=(1.732,-1,0).
  Middle ring: v3=(0,1,0), v4=(-0.866,-0.5,0), v5=(0.866,-0.5,0).
  3 outer triangles: t0=(v0,v3,v5), t1=(v0,v1,v3)... actually complex.

  SIMPLEST: just use a 3-spoke wheel where the hub is the hole center.
  Inner triangle (hole): v0=(0,0,0), v1=(0.3,0.3,0), v2=(0.3,-0.3,0).
  Outer spokes: v3=(0,-1,0), v4=(1.5,1.5,0), v5=(1.5,-1.5,0).
  6 triangles forming the ring — 3 inner edges form hole boundary.

  Even simpler: single annular ring with 3 inner boundary edges.
  Inner hole tri verts: v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.866,0).
  Outer rim: v3=(-0.5,-0.5,0), v4=(1.5,-0.5,0), v5=(0.5,1.366,0).
  3 "wedge" triangles: t0=(v0,v1,v3)... tricky to get boundary right.

  Go with: just 3 "hat" triangles sitting on top of 3 inner hole edges.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,0.866,0) — inner hole.
  v3=(-0.3,-0.3,0), v4=(1.3,-0.3,0), v5=(0.5,1.2,0) — outer hat vertices.
  Triangles: t0=(v0,v3,v1), t1=(v1,v4,v2), t2=(v2,v5,v0).
  Inner hole edges: v0-v1 (shared by t0), v1-v2 (shared by t1), v0-v2 (shared by t2).
  Each inner edge is in exactly 1 triangle → valid hole boundary [v0,v1,v2].
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me326",
             title="with_third_points_cdt2_path_conditional: CDT path fills planar triangular hole with all boundary edges present (Branch 7)",
             defect_class="hole_in_hull")

# Inner hole vertices.
v0 = m.vertex(0.0,   0.0,   0.0)   # 0
v1 = m.vertex(1.0,   0.0,   0.0)   # 1
v2 = m.vertex(0.5,   0.866, 0.0)   # 2

# Outer "hat" vertices — each hat triangle covers one inner hole edge.
v3 = m.vertex(-0.3, -0.3,   0.0)   # 3 — hat opposite to v0-v1
v4 = m.vertex( 1.3, -0.3,   0.0)   # 4 — hat opposite to v1-v2
v5 = m.vertex( 0.5,  1.2,   0.0)   # 5 — hat opposite to v0-v2

# Three "hat" triangles, each touching one inner hole edge.
t0 = m.triangle(v0, v3, v1)   # 0 — outer side of edge v0-v1
t1 = m.triangle(v1, v4, v2)   # 1 — outer side of edge v1-v2
t2 = m.triangle(v2, v5, v0)   # 2 — outer side of edge v2-v0

# Inner hole edges — each in exactly 1 triangle (the hat on that side).
m.assert_edge_shared(v0, v1, 1)   # boundary of hole (in t0)
m.assert_edge_shared(v1, v2, 1)   # boundary of hole (in t1)
m.assert_edge_shared(v0, v2, 1)   # boundary of hole (in t2)

# Hole boundary: the triangular gap that CDT fills.
m.assert_hole_boundary([v0, v1, v2])

# Outer hat edges — each in exactly 1 triangle.
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v0, v5, 1)

# Euler: V=6, E=9 (3 inner + 6 outer hat), F=3.
# chi = 6 - 9 + 3 = 0 (annular topology: disk with a triangular hole).
m.assert_euler_characteristic(6, 9, 3, 0)
