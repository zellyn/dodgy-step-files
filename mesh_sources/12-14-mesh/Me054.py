"""Me054 — sequential throw_on_SI: first of two pairs fires early exit.

Catalog claim: two self-intersecting triangle pairs are present, but in sequential
mode with `throw_on_SI`, CGAL PMP.self_intersections_impl Branch 9 @ line 495
wraps the sequential AABB callback in a throwing filter so that finding the first
intersection raises `Throw_at_output_exception` and exits before the second pair
is ever returned.

Source: CGAL PMP.self_intersections_impl Branch 9 @ line 495 —
*throw-vs-collect-in-sequential*: in the sequential (non-TBB) path, throw_on_SI
wraps the output in a throwing_filter rather than the standard append-to-vector
callback; the exception short-circuits the sequential AABB walk.

Defect carrier: two independent crossing pairs at different Y-offsets. Pair A
(triangles 0,1) at y≈0: XY triangle and XZ triangle sharing apex. Pair B
(triangles 2,3) at y=5: a second XY-offset triangle crossed by a tilted face.
Sequential AABB traversal encounters pair A first; throw_on_SI fires before
pair B is inspected.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me054",
             title="Sequential throw_on_SI: first of two pairs triggers early exit",
             defect_class="self_intersection_sequential_throw")

# Pair A: at origin — apex at (0,0,0), XY and XZ wings.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared apex
a1 = m.vertex(1.0, 1.0, 0.0)   # 1
a2 = m.vertex(1.0, -1.0, 0.0)  # 2
a3 = m.vertex(1.0, 0.0, 1.0)   # 3
a4 = m.vertex(1.0, 0.0, -1.0)  # 4
t0 = m.triangle(a0, a1, a2)    # tri 0 — XY plane, pair A
t1 = m.triangle(a0, a3, a4)    # tri 1 — XZ plane, crosses tri 0

# Pair B: at y=5, offset along Y to be spatially distinct.
b0 = m.vertex(0.0, 5.0, 0.0)   # 5
b1 = m.vertex(1.0, 6.0, 0.0)   # 6
b2 = m.vertex(1.0, 4.0, 0.0)   # 7
b3 = m.vertex(1.0, 5.0, 1.0)   # 8
b4 = m.vertex(1.0, 5.0, -1.0)  # 9
t2 = m.triangle(b0, b1, b2)    # tri 2 — XY-parallel plane, pair B
t3 = m.triangle(b0, b3, b4)    # tri 3 — tilted; crosses tri 2

# Assert: both SI pairs present (throw_on_SI exits after encountering first).
m.assert_triangles_self_intersect(t0, t1)   # pair A — sequential first hit
m.assert_triangles_self_intersect(t2, t3)   # pair B — never reached under throw
