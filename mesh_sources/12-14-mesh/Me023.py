"""Me023 — SI requiring multi-hop neighborhood expansion (expansion-step branch).

Catalog claim: a self-intersecting triangle pair (triangles 0,1) is surrounded
by a belt of additional triangles (triangles 2–5). The SI region cannot be
hole-filled from the initial 2-triangle seed alone — the topology is only
disk-fillable after expanding by 2 topological steps outward to include the belt.
This exercises the expand_face_selection / step parameter of the SI removal loop.

Source: CGAL PMP.remove_self_intersections Branch 12 @ line 2041 —
*expansion-step-depth-control*: whether to expand face selection by multiple
topological layers (step > 0) vs work on initial SI region only.

Defect carrier: triangles 0 and 1 cross at the center. Triangles 2–5 are a
surrounding quad fan sharing boundary edges with the center pair. The center pair
alone has a non-disk topology (two crossing faces); including the belt converts the
selection to a disk, enabling hole-fill.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me023",
             title="SI pair surrounded by expansion belt: expand_face_selection branch",
             defect_class="self_intersection_expansion_needed")

# Center crossing pair: XY triangle and XZ triangle sharing apex at origin.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared apex (crossing point)
v1 = m.vertex(1.0, 1.0, 0.0)   # 1
v2 = m.vertex(1.0, -1.0, 0.0)  # 2
v3 = m.vertex(1.0, 0.0, 1.0)   # 3
v4 = m.vertex(1.0, 0.0, -1.0)  # 4
t0 = m.triangle(v0, v1, v2)    # tri 0 — XY plane
t1 = m.triangle(v0, v3, v4)    # tri 1 — XZ plane; crosses tri 0

# Belt: four triangles surrounding the crossing region, each sharing an edge
# with either tri 0 or tri 1.
v5 = m.vertex(2.0,  1.0, 0.0)  # 5 — outer right-up
v6 = m.vertex(2.0, -1.0, 0.0)  # 6 — outer right-down
v7 = m.vertex(2.0,  0.0, 1.5)  # 7 — outer right-up-z
v8 = m.vertex(2.0,  0.0,-1.5)  # 8 — outer right-down-z

m.triangle(v1, v5, v2)    # tri 2 — shares edge (v1,v2) with tri 0
m.triangle(v3, v7, v4)    # tri 3 — shares edge (v3,v4) with tri 1
m.triangle(v1, v3, v5)    # tri 4 — bridges upper belt
m.triangle(v2, v4, v6)    # tri 5 — bridges lower belt

# Assert: center SI.
m.assert_triangles_self_intersect(0, 1)

# Assert: belt tri 2 shares edge (v1,v2) with center (only 2 incident triangles
# on that edge — manifold, not non-manifold).
m.assert_edge_shared(v1, v2, 2)
