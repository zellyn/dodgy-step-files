"""Me057 — parallel throw_on_SI: crossing pair fires exception in TBB path.

Catalog claim: two self-intersecting triangle pairs are present in a mesh that
would be processed by the parallel AABB intersection algorithm when TBB is
available. CGAL PMP.self_intersections_impl Branch 6 @ line 457 tests whether
`throw_on_SI` requires early termination in the parallel code: when set, the
parallel `box_self_intersection_d` callback is wrapped in a throwing filter so
that the first SI found by any TBB thread raises `Throw_at_output_exception`.

Source: CGAL PMP.self_intersections_impl Branch 6 @ line 457 —
*throw-vs-collect-in-parallel*: parallel path wraps the output callback with a
throwing filter vs concurrent vector accumulation; throw_on_SI fires across TBB
threads on the first SI report.

Defect carrier: two independent crossing pairs. The spatial separation ensures
they appear as distinct AABB box pairs, exercising the parallel callback path.
Pair A at y=0: XY triangle and tilted triangle sharing apex. Pair B at y=8:
rotated pair with the same crossing topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me057",
             title="Parallel throw_on_SI: two crossing pairs; TBB callback fires exception",
             defect_class="self_intersection_parallel_throw")

# Pair A: apex at origin.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(1.0, 1.0, 0.0)   # 1
a2 = m.vertex(1.0, -1.0, 0.0)  # 2
a3 = m.vertex(1.0, 0.0, 1.0)   # 3
a4 = m.vertex(1.0, 0.0, -1.0)  # 4
t0 = m.triangle(a0, a1, a2)    # tri 0 — XY plane
t1 = m.triangle(a0, a3, a4)    # tri 1 — tilted; crosses tri 0

# Pair B: apex offset along Y=8 to be spatially distinct.
b0 = m.vertex(0.0, 8.0, 0.0)   # 5
b1 = m.vertex(1.0, 9.0, 0.0)   # 6
b2 = m.vertex(1.0, 7.0, 0.0)   # 7
b3 = m.vertex(1.0, 8.0, 1.0)   # 8
b4 = m.vertex(1.0, 8.0, -1.0)  # 9
t2 = m.triangle(b0, b1, b2)    # tri 2
t3 = m.triangle(b0, b3, b4)    # tri 3 — crosses tri 2

# Assert: both crossing pairs are geometrically present.
m.assert_triangles_self_intersect(t0, t1)   # pair A
m.assert_triangles_self_intersect(t2, t3)   # pair B
