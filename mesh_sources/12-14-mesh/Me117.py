"""Me117 — intersects_coplanar_overlap: coplanar triangles with overlapping interiors.

MeshFix `Triangle.intersects` Branch 15 (*COPLANAR_TRIANGLES*):
'if (o11 == 0 && o12 == 0 && o13 == 0)' — all orientation values are zero,
meaning t1's vertices all lie in t2's plane (coplanar case). The code falls
back to 9 edge-pair crossing tests plus 6 point-in-triangle containment tests
to determine 2D overlap.

Geometric signature: two coplanar triangles in z=0 whose 2D projections
overlap with positive area. The standard SAT (Separating Axis Theorem) in 2D
finds no separating axis.

Geometry:
  t0: (0,0,0), (2,0,0), (0,2,0)   — lower-left right triangle in XY
  t1: (1,0,0), (3,0,0), (1,2,0)   — shifted right by 1 → x ∈ [1,3]; overlaps t0

t0 and t1 share the edge (v1=(1,0,0) to vertex at (1,0,0) in t1) — wait,
let me use fresh vertices so they are distinct index entries with overlapping
positions.

Positions chosen so the 2D overlap is the triangle (1,0,0)-(1,2,0)-(2,0,0):
a positive-area region.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me117",
             title="intersects_coplanar_overlap: coplanar triangles with overlapping interiors",
             defect_class="self_intersection_coplanar")

# t0 — lower-left right triangle
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(0.0, 2.0, 0.0)

# t1 — shifted right by 1; overlaps t0's interior in x ∈ [1,2]
v3 = m.vertex(1.0, 0.0, 0.0)
v4 = m.vertex(3.0, 0.0, 0.0)
v5 = m.vertex(1.0, 2.0, 0.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# Coplanar branch fires (all z=0); 2D SAT confirms overlap.
m.assert_triangles_self_intersect(t0, t1)
