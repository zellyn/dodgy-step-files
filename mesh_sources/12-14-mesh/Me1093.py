"""Me1093 — non_disk_cc_ring: degenerate face ring fails Euler disk test, marked unremovable (Branch 10).

CGAL PMP.remove_degenerate_faces Branch 10 @ line 2407 — *non-disk-topology-in-component*:
  'if (v - e + f != 1) { /* not a topological disk */ all_removed = false; continue; }'
  — when the degenerate connected component's Euler characteristic χ = V - E + F ≠ 1,
  the component is not a topological disk. CGAL marks it as unremovable and continues.

Defect pattern: four collinear vertices v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(3,0,0)
  forming a cycle of degenerate triangles. The cycle creates a non-disk topology:
  t0=(v0,v1,v2), t1=(v1,v2,v3), t2=(v0,v2,v3), t3=(v0,v1,v3). All four are zero-area.
  The cluster has edges v0-v1, v0-v2, v0-v3, v1-v2, v1-v3, v2-v3 — each shared by 2
  of the 4 faces. The boundary of the cluster is empty (every edge is internal). This
  means the "boundary" is a closed loop with no hole, i.e. genus > 0 for the cluster.
  V=4, E=6, F=4 → χ = 4 - 6 + 4 = 2 (sphere-like), not 1 (disk-like).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1093",
             title="non-disk degenerate CC: collinear ring χ=2≠1, topology check fails (Branch 10)",
             defect_class="degenerate_triangle")

# Four collinear vertices — all combinations of 3 form zero-area triangles.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 0.0, 0.0)   # 3

# All four combinations of 3-out-of-4 collinear vertices — all zero area.
t0 = m.triangle(v0, v1, v2)   # face 0: zero area
t1 = m.triangle(v1, v2, v3)   # face 1: zero area; shares (v1,v2) with t0
t2 = m.triangle(v0, v2, v3)   # face 2: zero area; shares (v0,v2) with t0, (v2,v3) with t1
t3 = m.triangle(v0, v1, v3)   # face 3: zero area; shares (v0,v1) with t0, (v0,v3) with t2

# Assert all four degenerate faces have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)
m.assert_triangle_area_lt(t3, 1e-12)

# Every edge is shared by exactly 2 of the 4 faces (no boundary edges in cluster).
# The complete graph K4 has 6 edges, each shared by 2 faces.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler characteristic: V=4, E=6, F=4, chi=4-6+4=2 (sphere, not disk where chi=1).
m.assert_euler_characteristic(v=4, e=6, f=4, chi=2)
