"""Me1022 — compatible_orientations nesting-constraint detector: direct-nesting-level-match.

Catalog claim: CGAL PMP.compatible_orientations (nesting-constraint detector) Branch 3
@ line 1204 (*direct-nesting-level-match*). After the nesting levels are computed for
each connected component, the detector checks whether a child component's nesting level
equals the parent's level plus one (`nesting_levels[child] == nesting_levels[parent] + 1`).
When this condition is satisfied, the outer component is at level 0 (outermost) and the
directly nested inner component is at level 1 — a direct parent-child relationship.
Branch 3 fires and the detector marks faces for potential winding-order flip to achieve
orientation compatibility across the nesting boundary.

Defect carrier: two closed tetrahedral components at distinct nesting levels. The outer
tetrahedron (edge length 6) is the root (level 0). The inner tetrahedron (edge length 0.6,
centered at the outer's centroid) is directly nested inside (level 1). No intermediate
nesting shell exists — the nesting level difference is exactly +1, satisfying the
parent-child match condition.

Key terms: 'nesting_levels', '+1', 'parent-child'.

Outer tetrahedron (component A, triangles 0-3) — nesting level 0:
  v0=(0,0,0), v1=(6,0,0), v2=(3,5.196,0), v3=(3,1.732,4.899)
  (edge length 6)

Inner tetrahedron (component B, triangles 4-7) — nesting level 1:
  Centered at outer centroid (3, 1.732, 1.225), edge length 0.6.
  i0=(2.7,1.732,1.225), i1=(3.3,1.732,1.225), i2=(3.0,2.252,1.225), i3=(3.0,1.924,1.714)

The inner component's vertices are all contained within the outer tetrahedron, establishing
the nesting_levels[inner] == nesting_levels[outer] + 1 relationship.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1022",
    title="compatible_orientations nesting-constraint detector: nesting_levels[child]==parent+1 direct parent-child relationship",
    defect_class="nested_orientation_parent_child",
)

# Component A: outer tetrahedron, edge length 6 — nesting level 0 (outermost).
v0 = m.vertex(0.0,   0.0,    0.0)      # 0 — outer base-left
v1 = m.vertex(6.0,   0.0,    0.0)      # 1 — outer base-right
v2 = m.vertex(3.0,   5.196,  0.0)      # 2 — outer base-far (6*sqrt(3)/2 ≈ 5.196)
v3 = m.vertex(3.0,   1.732,  4.899)    # 3 — outer apex (6*sqrt(3)/6 ≈ 1.732, 6*sqrt(6)/3 ≈ 4.899)

# Outer faces wound outward (normals away from centroid (3, 2.309, 1.225)).
t0 = m.triangle(v0, v2, v1)   # 0 — outer bottom
t1 = m.triangle(v0, v1, v3)   # 1 — outer front
t2 = m.triangle(v1, v2, v3)   # 2 — outer right
t3 = m.triangle(v0, v3, v2)   # 3 — outer left

# Component B: inner tetrahedron, edge length 0.6 — nesting level 1 (direct child of A).
# Centered at (3.0, 1.732, 1.225) — the outer tetrahedron's centroid.
i0 = m.vertex(2.7,   1.732,  1.225)    # 4 — inner base-left
i1 = m.vertex(3.3,   1.732,  1.225)    # 5 — inner base-right
i2 = m.vertex(3.0,   2.252,  1.225)    # 6 — inner base-far (0.6*sqrt(3)/2 ≈ 0.520)
i3 = m.vertex(3.0,   1.924,  1.714)    # 7 — inner apex (0.6*sqrt(3)/6 ≈ 0.173, 0.6*sqrt(6)/3 ≈ 0.490)

# Inner faces wound outward (normals away from inner centroid).
t4 = m.triangle(i0, i2, i1)   # 4 — inner bottom
t5 = m.triangle(i0, i1, i3)   # 5 — inner front
t6 = m.triangle(i1, i2, i3)   # 6 — inner right
t7 = m.triangle(i0, i3, i2)   # 7 — inner left

# Outer component: all 6 edges closed manifold (each shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Inner component: all 6 edges closed manifold (each shared by exactly 2 triangles).
m.assert_edge_shared(i0, i1, 2)
m.assert_edge_shared(i0, i2, 2)
m.assert_edge_shared(i0, i3, 2)
m.assert_edge_shared(i1, i2, 2)
m.assert_edge_shared(i1, i3, 2)
m.assert_edge_shared(i2, i3, 2)

# Inner component is topologically disconnected from outer (separate connected component).
# The CGAL nesting-level computation assigns level 0 to the outer (root) and level 1
# to the inner (directly contained). Branch 3 fires: nesting_levels[inner] == 0+1.
m.assert_triangle_not_reachable_from(target=t4, source=t0)

# Euler: V=8, E=12, F=8, chi=4 (two disjoint closed genus-0 components).
# Outer alone: V=4, E=6, F=4, chi=2 (level 0). Inner alone: V=4, E=6, F=4, chi=2 (level 1).
m.assert_euler_characteristic(v=8, e=12, f=8, chi=4)
