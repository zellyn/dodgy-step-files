"""Me1021 — compatible_orientations nesting-constraint detector: nested-component-existence.

Catalog claim: CGAL PMP.compatible_orientations (nesting-constraint detector) Branch 2
@ line 1192 (*nested-component-existence*). After computing per-component nesting
information, the detector checks whether `nested_cc_per_cc_shared` is non-empty for
each component. When two closed components are spatially nested (one enclosed inside
the other), the shared nesting map is non-empty and Branch 2 is entered; for a flat
list of disjoint non-nested components the map would be empty and Branch 2 is skipped.

Defect carrier: two closed tetrahedral components — a large outer tetrahedron and a
small inner tetrahedron geometrically contained inside the outer one. The inner
component's bounding box is fully inside the outer component's bounding box, so the
CGAL point-in-polyhedron test establishes a nesting relationship and populates
`nested_cc_per_cc_shared`, triggering Branch 2.

Key terms: 'nested_cc_per_cc_shared', 'empty'.

Outer tetrahedron (component A, triangles 0-3):
  Vertices at unit scale: v0=(0,0,0), v1=(4,0,0), v2=(2,3.464,0), v3=(2,1.155,3.266)
  (edge length 4 — large component)

Inner tetrahedron (component B, triangles 4-7):
  Vertices centered at (2, 1.2, 0.9), edge length 0.5 — fully inside the outer.
  i0=(1.75,1.2,0.9), i1=(2.25,1.2,0.9), i2=(2.0,1.633,0.9), i3=(2.0,1.344,1.308)

Both components are closed manifold surfaces (each tetrahedron has chi=2).
Combined: V=8, E=12, F=8, chi=4 (two disjoint closed components).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1021",
    title="compatible_orientations nesting-constraint detector: nested_cc_per_cc_shared non-empty (two nested closed tetrahedra)",
    defect_class="nested_closed_components",
)

# Component A: large outer tetrahedron (edge length 4, centered near origin).
v0 = m.vertex(0.0,   0.0,    0.0)      # 0 — outer base-left
v1 = m.vertex(4.0,   0.0,    0.0)      # 1 — outer base-right
v2 = m.vertex(2.0,   3.464,  0.0)      # 2 — outer base-far (4*sqrt(3)/2 ≈ 3.464)
v3 = m.vertex(2.0,   1.155,  3.266)    # 3 — outer apex (4*sqrt(3)/6 ≈ 1.155, 4*sqrt(6)/3 ≈ 3.266)

# Outer faces wound outward (normals away from interior centroid (2, 1.54, 0.82)).
t0 = m.triangle(v0, v2, v1)   # 0 — outer bottom
t1 = m.triangle(v0, v1, v3)   # 1 — outer front
t2 = m.triangle(v1, v2, v3)   # 2 — outer right
t3 = m.triangle(v0, v3, v2)   # 3 — outer left

# Component B: small inner tetrahedron (edge length 0.5), fully inside component A.
# Center at (2.0, 1.2, 0.9) — well inside the outer tetrahedron.
i0 = m.vertex(1.75,  1.2,    0.9)      # 4 — inner base-left
i1 = m.vertex(2.25,  1.2,    0.9)      # 5 — inner base-right
i2 = m.vertex(2.0,   1.633,  0.9)      # 6 — inner base-far (0.5*sqrt(3)/2 ≈ 0.433)
i3 = m.vertex(2.0,   1.344,  1.309)    # 7 — inner apex (0.5*sqrt(6)/3 ≈ 0.408)

# Inner faces wound outward (normals away from inner centroid (2.0, 1.327, 1.002)).
t4 = m.triangle(i0, i2, i1)   # 4 — inner bottom
t5 = m.triangle(i0, i1, i3)   # 5 — inner front
t6 = m.triangle(i1, i2, i3)   # 6 — inner right
t7 = m.triangle(i0, i3, i2)   # 7 — inner left

# Outer component: all 6 edges shared by exactly 2 triangles (closed manifold).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Inner component: all 6 edges shared by exactly 2 triangles (closed manifold).
m.assert_edge_shared(i0, i1, 2)
m.assert_edge_shared(i0, i2, 2)
m.assert_edge_shared(i0, i3, 2)
m.assert_edge_shared(i1, i2, 2)
m.assert_edge_shared(i1, i3, 2)
m.assert_edge_shared(i2, i3, 2)

# Inner component is topologically disconnected from outer component.
# This forces the nesting detector to analyze two separate closed components
# and populate nested_cc_per_cc_shared (Branch 2 fires).
m.assert_triangle_not_reachable_from(target=t4, source=t0)

# Euler: V=8, E=12, F=8, chi=4 (two disjoint closed genus-0 components).
m.assert_euler_characteristic(v=8, e=12, f=8, chi=4)
