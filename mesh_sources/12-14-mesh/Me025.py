"""Me025 — dual persistent SI piercers stall iteration convergence (stalling-detection branch).

Catalog claim: two independent intruding triangles (triangles 1 and 2) both pierce
the same base triangle (triangle 0). Healing one crossing does not eliminate the
other, so the iteration's something_was_done flag stays false after each individual
pass. The stall-detection branch restores the face list and avoids an infinite loop.

Source: CGAL PMP.remove_self_intersections Branch 15 @ line 2311 —
*iteration-convergence-stalling-detection*: whether the current step changed mesh
topology; restore face list and skip SI recomputation when topology is unchanged.

Defect carrier: triangle 0 is a large flat triangle in the z=0 plane. Triangle 1
is an intruder whose apex (v3) is below z=0 and whose base straddles z=0, piercing
triangle 0. Triangle 2 is a second independent intruder at a different location that
also pierces triangle 0. No single hole-fill pass can simultaneously resolve both
crossings, so convergence stalls.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me025",
             title="dual persistent SI piercers: something_was_done=false convergence stall",
             defect_class="self_intersection_convergence_stall")

# Base triangle in z=0 plane — large enough to be pierced at two locations.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
m.triangle(v0, v1, v2)    # tri 0 — XY base

# Intruder 1: pierces tri 0 near left side.
v3 = m.vertex(1.0, 0.5, -1.0)  # 3 — apex below z=0 (defect)
v4 = m.vertex(0.5, 1.0,  1.0)  # 4 — above z=0
v5 = m.vertex(1.5, 1.0,  1.0)  # 5 — above z=0
m.triangle(v3, v4, v5)    # tri 1 — crosses tri 0

# Intruder 2: pierces tri 0 near right side, independent of intruder 1.
v6 = m.vertex(1.0, 1.0, -0.8)  # 6 — apex below z=0 (second defect)
v7 = m.vertex(0.3, 0.3,  0.8)  # 7 — above z=0
v8 = m.vertex(1.7, 0.3,  0.8)  # 8 — above z=0
m.triangle(v6, v7, v8)    # tri 2 — also crosses tri 0

# Assert: both self-intersections present.
m.assert_triangles_self_intersect(0, 1)
m.assert_triangles_self_intersect(0, 2)
