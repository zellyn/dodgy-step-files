"""Me033 — non_disk_degenerate_cc: degenerate face group with non-disk topology (Branch 10).

Catalog claim: a cluster of degenerate (collinear/zero-area) triangles
shares edges in a pattern that does NOT form a topological disk. The Euler
characteristic of the cluster fails the v-e+f==1 (disk) check. CGAL
PMP.remove_degenerate_faces marks the component as unremovable and
continues the outer loop.

Source: CGAL PMP.remove_degenerate_faces Branch 10 @ line 2407 —
*non-disk-topology-in-component*: degenerate face group v-e+f ≠ 1;
marked as not a topological disk; repair skipped for this component.

Defect carrier: a "figure-8" or annular cluster of degenerate triangles.
Four collinear triangles in a cycle: two pairs share a hub edge. The cluster
wraps around with a non-contractible loop — topological genus > 0 for the
cluster, so the Euler check fails. Six zero-area triangles arranged so the
cluster has two "holes" in the interior boundary.

Geometry: all 8 vertices at z=0 on the X axis; triangles degenerate.
The connectivity pattern forms a strip that wraps back on itself.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me033",
             title="non-disk degenerate CC: collinear cluster with non-disk topology (v-e+f≠1)",
             defect_class="degenerate_triangle")

# Six collinear vertices along X — all zero-area triangles.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(5.0, 0.0, 0.0)   # 5

# Six zero-area triangles. Edge (v2, v3) is shared by 3 faces — non-manifold
# and non-disk topology: a single internal edge incident on 3 faces means
# v-e+f ≠ 1 for the cluster (non-disk).
t0 = m.triangle(v0, v1, v2)   # face 0: zero area
t1 = m.triangle(v1, v2, v3)   # face 1: zero area, shares (v1,v2) with t0
t2 = m.triangle(v2, v3, v4)   # face 2: zero area, shares (v2,v3) with t1
t3 = m.triangle(v3, v4, v5)   # face 3: zero area, shares (v3,v4) with t2
t4 = m.triangle(v0, v2, v4)   # face 4: zero area, spans non-adjacent
t5 = m.triangle(v1, v3, v5)   # face 5: zero area, spans non-adjacent

# Assert all six degenerate faces have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)
m.assert_triangle_area_lt(t3, 1e-12)
m.assert_triangle_area_lt(t4, 1e-12)
m.assert_triangle_area_lt(t5, 1e-12)

# The edge (v2, v3) is shared by faces t1 and t2; (v1, v2) by t0 and t1;
# (v3, v4) by t2 and t3. The cluster connectivity is non-disk.
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v2, v3, 2)
m.assert_edge_shared(v3, v4, 2)
