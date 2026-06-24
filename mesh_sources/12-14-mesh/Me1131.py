"""Me1131 — SI region requiring 3-ring expansion to become disk-fillable.

Catalog claim: two crossing triangles (tris 0,1) form the SI seed. A first
belt of triangles (tris 2-5) shares edges with the seed but together with the
seed still lacks disk topology. Only after a second expansion ring (tris 6-9)
is included does the selection become a disk (chi=1) that can be hole-filled.
This exercises the step > 0 iterative expand_face_selection loop in CGAL's
remove_self_intersections, which must expand by multiple topological layers
before attempting the repair.

Source: CGAL PMP.remove_self_intersections Branch 12 @ line 2041 —
*expansion-step-depth-control*: whether to expand face selection by multiple
topological layers (step > 0) vs work on initial SI region only.

Defect carrier: center crossing pair (tris 0,1) plus a two-ring surrounding
fan. The center pair alone has non-disk topology; the inner belt (tris 2-5)
still doesn't form a disk; only after adding the outer belt (tris 6-9) does
the full selection become a topological disk, enabling hole-fill at step=2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1131",
             title="SI pair needing 2-ring expansion: expand_face_selection step>0 branch",
             defect_class="self_intersection_expansion_needed")

# Center crossing pair: XY triangle and XZ triangle sharing apex at origin.
v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — shared apex (crossing point)
v1 = m.vertex(1.0,  1.0,  0.0)   # 1
v2 = m.vertex(1.0, -1.0,  0.0)   # 2
v3 = m.vertex(1.0,  0.0,  1.0)   # 3
v4 = m.vertex(1.0,  0.0, -1.0)   # 4
t0 = m.triangle(v0, v1, v2)     # tri 0 — XY plane
t1 = m.triangle(v0, v3, v4)     # tri 1 — XZ plane; crosses tri 0

# Inner belt: 4 triangles sharing edges with center pair.
v5 = m.vertex(2.0,  1.5,  0.0)   # 5
v6 = m.vertex(2.0, -1.5,  0.0)   # 6
v7 = m.vertex(2.0,  0.0,  1.5)   # 7
v8 = m.vertex(2.0,  0.0, -1.5)   # 8
m.triangle(v1, v5, v2)   # tri 2 — shares edge (v1,v2) with tri 0
m.triangle(v3, v7, v4)   # tri 3 — shares edge (v3,v4) with tri 1
m.triangle(v1, v3, v5)   # tri 4 — bridges upper-right
m.triangle(v2, v4, v6)   # tri 5 — bridges lower-right

# Outer belt: 4 more triangles making the total selection a disk.
v9  = m.vertex(3.0,  1.5,  0.0)  # 9
v10 = m.vertex(3.0, -1.5,  0.0)  # 10
v11 = m.vertex(3.0,  0.0,  1.5)  # 11
v12 = m.vertex(3.0,  0.0, -1.5)  # 12
m.triangle(v5, v9,  v7)   # tri 6 — outer bridge upper
m.triangle(v6, v8,  v10)  # tri 7 — outer bridge lower
m.triangle(v5, v7,  v9)   # tri 8 — outer right-up
m.triangle(v6, v10, v8)   # tri 9 — outer right-down

# Assert: center SI (tris 0 and 1 cross).
m.assert_triangles_self_intersect(0, 1)

# Assert: inner belt edge shared by exactly 2 triangles (manifold interior).
m.assert_edge_shared(v1, v2, 2)

# Assert: outer belt edge shared by exactly 2 triangles.
m.assert_edge_shared(v5, v7, 2)
