"""Me052 — zero-limit trivial rejection: maximum_number == 0 returns immediately.

Catalog claim: the mesh contains a self-intersecting pair, but if
`maximum_number` is supplied as 0, CGAL PMP.self_intersections_impl Branch 2
@ line 373 returns immediately without processing any faces — an empty output
is produced even though the geometry has a real intersection. The fixture
demonstrates the geometry that WOULD trigger a hit under any positive limit.

Source: CGAL PMP.self_intersections_impl Branch 2 @ line 373 —
*zero-limit-trivial-rejection*: `do_limit && maximum_number == 0` → return
immediately without processing; guards against vacuous maximum_number=0 call.

Defect carrier: one crossing triangle pair (XY triangle crossed by a diagonal
triangle sharing an edge endpoint). Single SI pair is sufficient to demonstrate
that an output would exist under limit > 0, and the zero-limit branch would
suppress it. The two triangles share no vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me052",
             title="Zero-limit trivial rejection: SI present but count=0 skips all detection",
             defect_class="self_intersection_zero_limit")

# One SI pair: a horizontal XY triangle pierced by a tilted triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
# Piercing triangle: its base is above the XY-plane at z=-1 and z=+1,
# crossing the XY plane inside tri 0's interior.
v3 = m.vertex(1.0, 0.5, -1.0)  # 3
v4 = m.vertex(1.0, 0.5,  1.0)  # 4
v5 = m.vertex(3.0, 0.5,  0.0)  # 5

m.triangle(v0, v1, v2)   # tri 0 — XY plane
m.triangle(v3, v4, v5)   # tri 1 — tilted; edge v3–v4 pierces tri 0

# Assert: the SI pair exists in the geometry (the zero-limit branch would
# skip returning it, but the geometry is real).
m.assert_triangles_self_intersect(0, 1)
