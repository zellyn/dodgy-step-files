"""Me921 — keep_largest_component_size_criterion: face_size >= threshold selects dominant component.

Catalog claim: CGAL PMP.keep_largest_connected_components Branch 2 @
line 410 (*component_size_criterion*) evaluates each connected component
against a face_size threshold derived from a `Face_size` property map.
Components whose cumulative face-size meets or exceeds the threshold are
retained; smaller components are marked for removal.

Geometric signature: two disconnected components of markedly different
sizes. Component A has 4 triangles (large — passes the threshold when
keeping 1 component). Component B has 1 triangle (small — face_size < that
of A; Branch 2 marks it for removal because it is not among the largest N).

Defect carrier: triangles 0-3 form a unit-square patch (component A, face
count = 4); triangle 4 is an isolated micro-patch at (10,10,0) (component
B, face count = 1). The face_size_pmap assigns count-1-per-face; component
A accumulates size 4 vs component B size 1 — Branch 2 keeps the larger
component and discards the smaller.

Source: CGAL PMP.keep_largest_connected_components Branch 2 @ line 410 —
*component_size_criterion*: per-component `Face_size` values sorted; bottom
(total_components - desired_num) components discarded.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me921",
             title="keep_largest component_size_criterion: face_size >= threshold retains large component",
             defect_class="disconnected_components")

# Component A: unit-square patch — 4 triangles (large component).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(0.5, 0.5, 1.0)  # apex for two extra triangles

t0 = m.triangle(v0, v1, v2)   # area=0.5
t1 = m.triangle(v0, v2, v3)   # area=0.5
t2 = m.triangle(v0, v1, v4)   # area ≈ 0.559
t3 = m.triangle(v1, v2, v4)   # area ≈ 0.559

# Component B: single tiny triangle at (10,10,0) — small component.
v5 = m.vertex(10.0,  10.0,  0.0)
v6 = m.vertex(10.01, 10.0,  0.0)
v7 = m.vertex(10.0,  10.01, 0.0)
t4 = m.triangle(v5, v6, v7)   # area ≈ 5e-5

# Assert: component B (t4) is disconnected from component A (t0).
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: the small triangle has negligible area (confirms size disparity).
m.assert_triangle_area_lt(t4, 1e-3)
