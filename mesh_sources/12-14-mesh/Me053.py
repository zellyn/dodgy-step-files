"""Me053 — throw_on_SI exception mode: first SI triggers early termination.

Catalog claim: a single self-intersecting triangle pair is present. CGAL
PMP.self_intersections_impl Branch 4 @ line 402 tests whether the `throw_on_SI`
named parameter is set; when it is, finding the first intersection raises a
`Throw_at_output_exception` rather than appending to an output iterator. The
fixture demonstrates the geometry that triggers the throw — one pair of crossing
triangles, with no additional pairs needed (the exception fires on the first hit).

Source: CGAL PMP.self_intersections_impl Branch 4 @ line 402 —
*throw-vs-accumulate-exception-mode*: throw_on_SI flag → raise exception on
first SI vs append pair to output iterator; used by callers that only need
boolean SI presence, not the full list.

Defect carrier: triangle 0 lies in the XY plane; triangle 1 is a vertical
(XZ-plane) triangle sharing the apex (origin). Their interiors cross along the
positive X half-axis. A single pair is the minimal geometry to fire Branch 4.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me053",
             title="throw_on_SI mode: single crossing pair fires exception on first hit",
             defect_class="self_intersection_throw_on_first")

# Minimal single SI pair: two triangles sharing the apex at the origin.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared apex
v1 = m.vertex(2.0, 1.0, 0.0)   # 1
v2 = m.vertex(2.0, -1.0, 0.0)  # 2
v3 = m.vertex(2.0, 0.0, 1.0)   # 3
v4 = m.vertex(2.0, 0.0, -1.0)  # 4

m.triangle(v0, v1, v2)   # tri 0 — XY plane
m.triangle(v0, v3, v4)   # tri 1 — XZ plane; crosses tri 0 along X-axis

# Assert: the crossing pair exists.
m.assert_triangles_self_intersect(0, 1)
