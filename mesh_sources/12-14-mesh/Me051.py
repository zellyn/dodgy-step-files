"""Me051 — multiple SI pairs: output-count-limit parameter is applicable.

Catalog claim: the mesh contains two distinct self-intersecting triangle pairs.
CGAL PMP.self_intersections_impl Branch 1 @ line 371 tests whether the
`maximum_number` named parameter was supplied (is_default_parameter check);
when it is, a counter is activated so that collection terminates after
`maximum_number` pairs are reported. With two SI pairs in the mesh and a
limit of 1, only the first pair would be reported (limit fires before the
second is appended).

Source: CGAL PMP.self_intersections_impl Branch 1 @ line 371 —
*output-count-limit-applicability*: whether maximum_number NP is user-supplied
vs default; enables early-termination counter vs uncapped collection.

Defect carrier: two independent crossing pairs. Pair A (triangles 0,1): XY-plane
triangle crossed by XZ-plane triangle sharing the origin. Pair B (triangles 2,3):
a second XY-plane triangle crossed by a YZ-plane triangle sharing a different
point. The two pairs are spatially separated so the AABB returns both cleanly.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me051",
             title="Two SI pairs: maximum_number count-limit applicable branch",
             defect_class="self_intersection_count_limit")

# Crossing pair A: centered at origin.
# tri0: XY plane,  tri1: XZ plane — they cross along the X-axis.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared apex
a1 = m.vertex(1.0, 1.0, 0.0)   # 1
a2 = m.vertex(1.0, -1.0, 0.0)  # 2
a3 = m.vertex(1.0, 0.0, 1.0)   # 3
a4 = m.vertex(1.0, 0.0, -1.0)  # 4
t0 = m.triangle(a0, a1, a2)    # tri 0 — XY plane
t1 = m.triangle(a0, a3, a4)    # tri 1 — XZ plane; crosses tri 0

# Crossing pair B: centered at (10, 0, 0), well separated from pair A.
b0 = m.vertex(10.0, 0.0, 0.0)  # 5 — shared apex
b1 = m.vertex(11.0, 1.0, 0.0)  # 6
b2 = m.vertex(11.0, -1.0, 0.0) # 7
b3 = m.vertex(11.0, 0.0, 1.0)   # 8
b4 = m.vertex(11.0, 0.0, -1.0)  # 9
t2 = m.triangle(b0, b1, b2)    # tri 2 — XY-parallel plane
t3 = m.triangle(b0, b3, b4)    # tri 3 — tilted; crosses tri 2

# Assert: both SI pairs are present in the fixture geometry.
m.assert_triangles_self_intersect(t0, t1)   # pair A
m.assert_triangles_self_intersect(t2, t3)   # pair B
