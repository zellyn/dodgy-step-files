"""Me245 — negligible_size_dry_run: dry_run mode collects faces without removing them.

Catalog claim: CGAL PMP.remove_connected_components_of_negligible_size Branch 6
@ line 237 (*dry-run-vs-mutation*) branches on the `dry_run` named parameter.
When dry_run=true, the function collects faces that would be removed but does NOT
actually remove them from the mesh — it returns only the count. The mesh remains
intact.

Geometric signature: two disconnected components with a clear size disparity.
The tiny component (triangle 2) would be flagged for removal under area threshold,
but in dry_run mode the mesh is not mutated.

Defect carrier: a unit-quad patch (triangles 0-1, area=1.0) and a micro-triangle
(triangle 2, area≈5e-5). Both components remain after dry_run.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 6 @
line 237 — *dry-run-vs-mutation*: `if (dry_run)` → collect faces to
`output_iterator` but skip the `remove_faces` call.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me245",
             title="negligible_size dry_run: collect-only mode; micro-component identified but mesh not mutated",
             defect_class="disconnected_components")

# Component A: unit-square (two triangles, area = 1.0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: area = 0.5
t1 = m.triangle(v0, v2, v3)   # face 1: area = 0.5

# Component B: micro-triangle (area ≈ 5e-5) at a remote location.
v4 = m.vertex(30.0, 30.0, 0.0)
v5 = m.vertex(30.01, 30.0, 0.0)
v6 = m.vertex(30.0, 30.01, 0.0)
t2 = m.triangle(v4, v5, v6)   # face 2: below area threshold, flagged but not removed in dry_run

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t2, t0)

# Assert: the micro-triangle has negligible area (it would be flagged by dry_run).
m.assert_triangle_area_lt(t2, 1e-3)
