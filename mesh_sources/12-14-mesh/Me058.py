"""Me058 — parallel output-count limit: 4 SI pairs, atomic counter fires in TBB path.

Catalog claim: the mesh contains four self-intersecting triangle pairs. CGAL
PMP.self_intersections_impl Branch 7 @ line 459 wraps the parallel output with a
counter functor using an `atomic_counter` when `do_limit` is true; when the
parallel AABB traversal accumulates `maximum_number` pairs, the counter functor
throws `Throw_at_output_exception` from whichever TBB thread hits the limit.
This fixture provides four pairs and a limit of 3 to exercise the atomic path.

Source: CGAL PMP.self_intersections_impl Branch 7 @ line 459 —
*output-limit-in-parallel*: wrap parallel output with Throw_functor + atomic_counter
vs direct callback; counter fires atomically across TBB threads.

Defect carrier: four spatially separated crossing pairs along the Z-axis at
z=0, z=10, z=20, z=30. Each pair is a minimal XY/XZ crossing sharing an apex.
The Z-axis spread gives the parallel AABB distinct boxes for each pair,
exercising the multi-thread counter scenario.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me058",
             title="Parallel count-limit: 4 SI pairs; atomic counter fires at limit 3",
             defect_class="self_intersection_parallel_count_limit")

def _pair(m, oz):
    """Add a minimal XY/XZ crossing pair at z-offset oz; return (t_xy, t_xz)."""
    apex = m.vertex(0.0, 0.0, oz)
    p1   = m.vertex(1.0, 1.0, oz)
    p2   = m.vertex(1.0, -1.0, oz)
    p3   = m.vertex(1.0, 0.0, oz + 1.0)
    p4   = m.vertex(1.0, 0.0, oz - 1.0)
    ta = m.triangle(apex, p1, p2)
    tb = m.triangle(apex, p3, p4)
    return ta, tb

t0, t1 = _pair(m, 0.0)    # pair A — z=0
t2, t3 = _pair(m, 10.0)   # pair B — z=10
t4, t5 = _pair(m, 20.0)   # pair C — z=20
t6, t7 = _pair(m, 30.0)   # pair D — z=30; triggers atomic counter at limit=3

# Assert: all four crossing pairs are geometrically present.
m.assert_triangles_self_intersect(t0, t1)
m.assert_triangles_self_intersect(t2, t3)
m.assert_triangles_self_intersect(t4, t5)
m.assert_triangles_self_intersect(t6, t7)
