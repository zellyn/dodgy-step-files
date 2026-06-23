"""Me267 — range_with_face_set_not_topological_disk: marked region fails disk test after expansion.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 8 @ line 1846
(*not_topological_disk_after_expansion*): even after marking additional faces to resolve
non-manifold boundary vertices, the marked region still does not form a topological disk
(is_selection_a_topological_disk returns false). The algorithm skips the removal and marks
all_removed=false.

A region of triangles forms a topological disk iff it is simply connected: the region
has exactly one boundary loop and no handles (genus 0 with boundary, Euler chi=1).
If the region forms a cylinder (genus 0, closed) or has internal holes, chi != 1 and
the disk test fails.

Geometric signature: the marked region around the degenerate edge forms a CYLINDER
(two boundary loops) rather than a disk. When the region has two holes (two separate
boundary loops), is_selection_a_topological_disk fails.

Configuration: a tube/cylinder formed by 6 triangles in two rings. The degenerate edge
connects the two boundary circles of the cylinder. The cylinder has chi=0 (not 1),
failing the topological disk check.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me267",
             title="range_with_face_set not_topological_disk_after_expansion: marked region forms cylinder (chi=0) → disk test fails → skip",
             defect_class="degenerate_edge")

# A triangulated cylinder: two rings of 3 vertices each, connected by 6 triangles.
# Top ring: v0,v1,v2 (with v0≈v1: degenerate edge on top ring).
# Bottom ring: v3,v4,v5.
v0 = m.vertex(0.0,   1.0, 1.0)
v1 = m.vertex(1e-10, 1.0, 1.0)   # nearly same as v0 — degenerate edge on top ring

v2 = m.vertex(1.0,  0.0, 1.0)    # top ring 3rd vertex

# Bottom ring (open).
v3 = m.vertex(0.0,  1.0, 0.0)    # below v0
v4 = m.vertex(1e-10,1.0, 0.0)    # below v1
v5 = m.vertex(1.0,  0.0, 0.0)    # below v2

# 6 triangles forming the cylinder (two triangle strips around the tube).
# Top ring: (v0,v1,v2) — but that uses degenerate edge (v0,v1).
# Instead use 2 top-ring triangles and 4 side triangles.
# Top cap edge: (v0,v1,v2): but degenerate triangle.
# Cylinder side: connect top ring to bottom ring.
t0 = m.triangle(v0, v1, v2)   # 0: top strip — includes degenerate edge (v0,v1)
t1 = m.triangle(v0, v3, v1)   # 1: left side (v0-v1 stripe) — includes (v0,v1)
t2 = m.triangle(v1, v3, v4)   # 2: left side lower
t3 = m.triangle(v1, v4, v2)   # 3: wait, this creates edge (1,2)
t4 = m.triangle(v2, v4, v5)   # 4: right side
t5 = m.triangle(v0, v5, v3)   # 5: back stripe

# The degenerate edge (v0,v1) is in t0 and t1 → n=2.
m.assert_edge_shared(v0, v1, 2)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# The cylinder has two distinct boundary loops:
# Top: (v0,v2) — the far top edge (v2 has only top connection)
# Bottom: (v3,v4,v5) — the bottom ring
# Verify cylinder topology: compute chi.
# V=6, count edges: t0:(0,1),(1,2),(0,2); t1:(0,3),(0,1),(1,3); t2:(1,3),(1,4),(3,4);
# t3:(1,2),(1,4),(2,4); t4:(2,4),(2,5),(4,5); t5:(0,5),(0,3),(3,5)?
# Unique edges: (0,1),(0,2),(1,2),(0,3),(1,3),(1,4),(3,4),(2,4),(2,5),(4,5),(0,5),(3,5) = 12
# V=6, E=12, F=6 -> chi = 6-12+6 = 0 (cylinder = sphere with 2 holes, chi=0)
m.assert_euler_characteristic(v=6, e=12, f=6, chi=0)
