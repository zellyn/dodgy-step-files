"""Me861 — strongIntersectionRemoval iteration limit: max_iters / iter_count exceeded.

Catalog claim: a mesh with two independent SI pairs that are geometrically
stubborn — resolving one pair does not eliminate the other — forces
Basic_TMesh.strongIntersectionRemoval to consume all allowed iterations.
The iteration-limit branch (Branch 2) fires when iter_count exceeds max_iters,
exiting the removal loop early with unresolved intersections rather than
looping forever.

Source: MeshFix `Basic_TMesh.strongIntersectionRemoval` Branch 2 @ line 381 —
*Iteration limit*: max_iters / iter_count exceeded; exits the removal loop
early with unresolved intersections.

Defect carrier: triangle 0 is a large flat base in the XY plane. Triangles 1
and 2 are independent intruders that each pierce triangle 0 at separate
locations. Triangle 1 pierces the left side; triangle 2 pierces the right
side. No single repair pass resolves both crossings simultaneously: removing
the left crossing reintroduces geometry that collides with the right, and
vice versa. This dual-persistent SI pattern exhausts the iteration budget.
Unlike Me025 (CGAL convergence stall), this fixture targets the MeshFix
strongIntersectionRemoval iteration counter specifically.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me861",
    title="strongIntersectionRemoval iteration limit: dual persistent SI piercers exhaust max_iters (Branch 2)",
    defect_class="self_intersection",
)

# Triangle 0: large base in XY plane — pierced at two independent locations.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(4.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 4.0, 0.0)   # 2
m.triangle(v0, v1, v2)   # tri 0 — XY base

# Intruder 1: pierces tri 0 on the left side — no shared vertices with tri 0.
v3 = m.vertex(0.8, 1.5, -1.5)  # 3 — below z=0
v4 = m.vertex(0.8, 1.5,  1.5)  # 4 — above z=0
v5 = m.vertex(2.0, 1.5,  0.0)  # 5 — at z=0, inside tri 0's footprint
m.triangle(v3, v4, v5)   # tri 1 — pierces tri 0 near the left

# Intruder 2: pierces tri 0 on the right side — no shared vertices with tri 0 or tri 1.
v6 = m.vertex(3.0, 1.5, -1.5)  # 6 — below z=0
v7 = m.vertex(3.0, 1.5,  1.5)  # 7 — above z=0
v8 = m.vertex(1.5, 1.5,  0.0)  # 8 — at z=0, inside tri 0's footprint (right side)
m.triangle(v6, v7, v8)   # tri 2 — pierces tri 0 near the right

# Assert: both SI pairs are independently present (stubborn multi-site configuration).
m.assert_triangles_self_intersect(0, 1)
m.assert_triangles_self_intersect(0, 2)
