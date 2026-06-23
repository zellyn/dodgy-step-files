"""Me056 — sequential catch-limit-exception: recovery after Count_and_throw_filter fires.

Catalog claim: the mesh contains four self-intersecting triangle pairs, and the
sequential count-limit fires mid-stream. CGAL PMP.self_intersections_impl
Branch 11 @ line 510 is the `catch` block that handles `Throw_at_output_exception`
after sequential accumulation reaches `maximum_number`. The catch block copies
accumulated pairs to the output and returns. This fixture provides four crossing
pairs to ensure the counter actually fires (at limit=3) before the last pair.

Source: CGAL PMP.self_intersections_impl Branch 11 @ line 510 —
*catch-limit-exception-recovery-sequential*: catch block copies the accumulated
partial result and returns early vs continue processing; exercises exception
unwinding on the sequential code path.

Defect carrier: four spatially separated crossing pairs. Each pair is a minimal
XY/XZ apex crossing at x=0, x=10, x=20, x=30. The AABB traversal yields all
four; with a limit of 3, the exception fires during pair 4 and the catch block
saves pairs 1–3 to the output iterator.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me056",
             title="Sequential catch-limit: 4 SI pairs; exception caught after limit 3",
             defect_class="self_intersection_sequential_catch_limit")

def _pair(m, ox):
    """Add a minimal XY/XZ crossing pair centered at x=ox; return (t_xy, t_xz)."""
    apex = m.vertex(ox, 0.0, 0.0)
    p1   = m.vertex(ox + 1.0, 1.0, 0.0)
    p2   = m.vertex(ox + 1.0, -1.0, 0.0)
    p3   = m.vertex(ox + 1.0, 0.0, 1.0)
    p4   = m.vertex(ox + 1.0, 0.0, -1.0)
    ta = m.triangle(apex, p1, p2)
    tb = m.triangle(apex, p3, p4)
    return ta, tb

t0, t1 = _pair(m, 0.0)    # pair A — x=0
t2, t3 = _pair(m, 10.0)   # pair B — x=10
t4, t5 = _pair(m, 20.0)   # pair C — x=20
t6, t7 = _pair(m, 30.0)   # pair D — x=30; triggers catch after limit=3

# Assert: all four SI pairs are present.
m.assert_triangles_self_intersect(t0, t1)
m.assert_triangles_self_intersect(t2, t3)
m.assert_triangles_self_intersect(t4, t5)
m.assert_triangles_self_intersect(t6, t7)
