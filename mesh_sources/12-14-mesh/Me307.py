"""Me307 — retriangulateSelectedRegion_hole_triangulation: Delaunay re-triangulation with Steiner points.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 8 (*hole_triangulation*) @ line 983:
  `TriangulateHole(e, vl)` — performs Delaunay hole-filling on the boundary edge `e`
  with the internal vertex list `vl`. This is the core re-triangulation step: after
  the selected triangles have been unlinked, the hole is re-filled using the boundary
  loop and any interior Steiner points.

The result of `TriangulateHole(e, vl)` is a new triangulation of the region that
replaces the original triangles. With Steiner points, the re-triangulation can produce
a better-quality mesh than the original configuration.

Defect carrier: a triangular region that has been re-triangulated. The hole boundary
is a triangle (3 boundary edges). One Steiner point `vs` was inserted at the centroid,
producing three new well-shaped triangles — the output of `TriangulateHole`.

This models the POST re-triangulation state:
  Before: hole boundary (v0, v1, v2) with Steiner point vs at centroid
  After: 3 Delaunay triangles: t0=(v0,v1,vs), t1=(v1,v2,vs), t2=(v2,v0,vs)

The three new triangles all share `vs` as an interior vertex (all edges from vs
are interior), confirming the Steiner-point re-triangulation occurred.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me307",
    title="retriangulateSelectedRegion_hole_triangulation: TriangulateHole with Steiner point (Branch 8)",
    defect_class="retriangulate_region_hole_fill",
)

# Boundary vertices of the triangular hole.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 3.0, 0.0)   # 2

# Steiner point: centroid of (v0, v1, v2).
vs = m.vertex(1.5, 1.0, 0.0)   # 3 — internal vertex from vl; TriangulateHole inserts it

# Outer frame (context mesh — not the re-triangulated region).
vo0 = m.vertex(1.5, -2.0, 0.0)   # 4
vo1 = m.vertex(4.5, 3.0, 0.0)    # 5
vo2 = m.vertex(-1.5, 3.0, 0.0)   # 6

# Frame triangles.
tf0 = m.triangle(v0, v1, vo0)    # 0 — bottom frame
tf1 = m.triangle(v1, v2, vo1)    # 1 — right frame
tf2 = m.triangle(v2, v0, vo2)    # 2 — left frame

# Re-triangulated region: 3 Delaunay triangles with Steiner point vs.
t0 = m.triangle(v0, v1, vs)   # 3 — first re-tri triangle
t1 = m.triangle(v1, v2, vs)   # 4 — second re-tri triangle
t2 = m.triangle(v2, v0, vs)   # 5 — third re-tri triangle

# Inner edges from Steiner point vs — all interior (n=2).
m.assert_edge_shared(v0, vs, 2)   # shared by t0 and t2
m.assert_edge_shared(v1, vs, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, vs, 2)   # shared by t1 and t2

# Outer boundary edges of the re-triangulated region — now interior (n=2)
# because they're shared between a frame triangle and a re-tri triangle.
m.assert_edge_shared(v0, v1, 2)   # shared by tf0 and t0
m.assert_edge_shared(v1, v2, 2)   # shared by tf1 and t1
m.assert_edge_shared(v2, v0, 2)   # shared by tf2 and t2

# Euler: V=7, E=9+3=12, F=6, chi = 7-12+6 = 1 (open disk patch).
m.assert_euler_characteristic(v=7, e=12, f=6, chi=1)
