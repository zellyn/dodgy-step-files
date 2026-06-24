"""Me1134 — three independent SI piercers cause iteration to stall (stalling-detection).

Catalog claim: three independent intruding triangles (tris 1, 2, 3) each pierce
the same large base triangle (tri 0) at distinct, separated locations. No single
hole-fill pass resolves all crossings simultaneously. After each individual pass,
the `something_was_done` flag remains false because the topology is unchanged.
The stall-detection branch fires: CGAL's remove_self_intersections calls
`faces_to_treat.swap` to restore the previous face list and exits the iteration
to avoid an infinite loop.

Source: CGAL PMP.remove_self_intersections Branch 15 @ line 2311 —
*iteration-convergence-stalling-detection*: whether the current step changed
mesh topology; restore face list (faces_to_treat.swap) and skip SI recomputation
when topology is unchanged (something_was_done = false).

Defect carrier: tri 0 is a large flat triangle in the z=0 plane. Tris 1, 2 and
3 are three independent intruders whose apices are below z=0 and whose upper
edges straddle z=0, each piercing tri 0 at a well-separated location. No single
repair pass reaches all three crossings, so something_was_done stays false and
the convergence-stall exit triggers. This is a strengthened version of Me025
(which uses two piercers) with three independent crossings to more robustly
exercise the branch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1134",
             title="three independent SI piercers: something_was_done=false convergence stall",
             defect_class="self_intersection_convergence_stall")

# Base triangle in z=0 plane — large enough to be pierced at three locations.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 3.0, 0.0)   # 2
m.triangle(v0, v1, v2)    # tri 0 — large base triangle in z=0

# Intruder 1: pierces tri 0 near left side.
v3 = m.vertex(0.8, 0.5, -1.0)  # 3 — apex below z=0
v4 = m.vertex(0.3, 1.2,  1.0)  # 4 — above z=0
v5 = m.vertex(1.3, 1.2,  1.0)  # 5 — above z=0
m.triangle(v3, v4, v5)    # tri 1 — crosses tri 0 at left

# Intruder 2: pierces tri 0 near center.
v6 = m.vertex(1.5, 1.0, -1.0)  # 6 — apex below z=0
v7 = m.vertex(1.0, 0.4,  1.0)  # 7 — above z=0
v8 = m.vertex(2.0, 0.4,  1.0)  # 8 — above z=0
m.triangle(v6, v7, v8)    # tri 2 — crosses tri 0 at center

# Intruder 3: pierces tri 0 near right side.
v9  = m.vertex(2.3, 0.5, -0.8)  # 9  — apex below z=0
v10 = m.vertex(1.8, 1.1,  0.8)  # 10 — above z=0
v11 = m.vertex(2.8, 1.1,  0.8)  # 11 — above z=0
m.triangle(v9, v10, v11)  # tri 3 — crosses tri 0 at right

# Assert: all three self-intersections present.
m.assert_triangles_self_intersect(0, 1)
m.assert_triangles_self_intersect(0, 2)
m.assert_triangles_self_intersect(0, 3)
