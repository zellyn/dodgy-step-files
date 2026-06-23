"""Me059 — parallel catch-limit: exception caught after atomic counter fires in TBB path.

Catalog claim: the mesh contains five self-intersecting triangle pairs. CGAL
PMP.self_intersections_impl Branch 8 @ line 469 is the `catch` block in the
parallel path that handles `Throw_at_output_exception` after the atomic counter
reaches `maximum_number`. The catch block copies the accumulated concurrent-vector
pairs to the output iterator and returns. This fixture provides five crossing
pairs (limit=4) to exercise the parallel catch path.

Source: CGAL PMP.self_intersections_impl Branch 8 @ line 469 —
*catch-limit-exception-recovery*: in the parallel path, catch block copies
pairs from concurrent accumulator to output and exits vs continue parallel
traversal; exercises parallel exception unwinding.

Defect carrier: five spatially separated crossing pairs along the X-axis at
x=0, x=10, x=20, x=30, x=40. The fifth pair (x=40) triggers the parallel catch
block after the atomic counter reaches limit=4. Each pair is a minimal two-triangle
crossing (XY/XZ planes sharing an apex) giving distinct AABB boxes.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me059",
             title="Parallel catch-limit: 5 SI pairs; concurrent exception caught at limit 4",
             defect_class="self_intersection_parallel_catch_limit")

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
t6, t7 = _pair(m, 30.0)   # pair D — x=30
t8, t9 = _pair(m, 40.0)   # pair E — x=40; triggers parallel catch at limit=4

# Assert: all five crossing pairs are geometrically present.
m.assert_triangles_self_intersect(t0, t1)
m.assert_triangles_self_intersect(t2, t3)
m.assert_triangles_self_intersect(t4, t5)
m.assert_triangles_self_intersect(t6, t7)
m.assert_triangles_self_intersect(t8, t9)
