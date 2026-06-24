"""Me922 — keep_largest_dry_run_mode: dry_run=true skips mesh modification.

Catalog claim: CGAL PMP.keep_largest_connected_components Branch 3 @
line 419 (*dry_run_mode*) fires when the caller passes `dry_run=true`.
In dry-run mode the function identifies which components would be removed
(their faces are collected into the output iterator) but does NOT call the
actual mesh-mutation step. The mesh topology is left intact after the call.

Geometric signature: two disconnected components — a large 3-triangle patch
(component A) and a small 1-triangle component (component B). With
desired_num=1 and dry_run=true, Branch 3 recognises the would-be removal
candidate (component B) and skips `remove_connected_components`, returning
the face count that *would* have been removed without modifying the mesh.

Defect carrier: triangles 0-2 form a connected right-angle patch (component
A, face count=3); triangle 3 is an isolated micro-patch at (20,20,0)
(component B, face count=1). dry_run=true triggers Branch 3.

Source: CGAL PMP.keep_largest_connected_components Branch 3 @ line 419 —
*dry_run_mode*: `if (dry_run) { /* do NOT call remove_connected_components */
return faces_to_remove.size(); }`.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me922",
             title="keep_largest dry_run_mode: dry_run=true; component identified but mesh not mutated",
             defect_class="disconnected_components")

# Component A: three-triangle right-angle patch (large component).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(2.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # area=0.5
t1 = m.triangle(v0, v2, v3)   # area=0.5; shares edge (v0,v2) with t0
t2 = m.triangle(v2, v4, v3)   # area=0.5; shares edge (v2,v3) with t1

# Component B: single triangle at (20,20,0) — small component.
v5 = m.vertex(20.0,  20.0,  0.0)
v6 = m.vertex(20.01, 20.0,  0.0)
v7 = m.vertex(20.0,  20.01, 0.0)
t3 = m.triangle(v5, v6, v7)   # area ≈ 5e-5

# Assert: component B (t3) is disconnected from component A (t0).
m.assert_triangle_not_reachable_from(t3, t0)

# Assert: component A triangles are connected (shared edges).
m.assert_edge_shared(v0, v2, 2)  # t0 and t1 share (v0,v2)
m.assert_edge_shared(v2, v3, 2)  # t1 and t2 share (v2,v3)

# Assert: the small triangle has negligible area (confirms it is the smaller component).
m.assert_triangle_area_lt(t3, 1e-3)
