"""Me703 — Basic_TMesh.bridgeBoundaries branch 4: gwe_endpoint_selection.

MeshFix `Basic_TMesh.bridgeBoundaries` Branch 4 (*gwe_endpoint_selection*) @ line 440:
  'v2 = (gwe->t1) ? (gwe->v2) : (gwe->v1);'
  — analogous to Branch 3 but for the second input edge gwe. When gwe->t1
  is non-NULL, the free endpoint of gwe is gwe->v2. This selects which
  vertex of gwe will anchor the second bridge triangle.

Defect pattern: two disjoint boundary edges (no shared vertex) where gwe
  has its t1 slot occupied by a triangle — so gwe->v2 is the free vertex
  selected for bridging. Geometrically identical layout to Me702 but
  documenting the gwe side of the endpoint-selection pair.

Geometry: two separate triangulated patches with open boundary edges.
  Top patch: t0=(a0,a1,a2), t1=(a0,a2,a3) sharing edge (a0,a2).
  Bottom patch: t2=(b0,b1,b2), t3=(b0,b2,b3) sharing edge (b0,b2).
  Patches are spatially disjoint — no vertex shared between them.
  gwe = boundary edge from bottom patch where t1 is non-NULL → v2 selected.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me703",
    title="bridgeBoundaries gwe_endpoint_selection: gwe->t1 non-NULL selects gwe->v2 as free endpoint; disjoint boundary edges on separate patches (Branch 4)",
    defect_class="boundary_hole",
)

# Top patch: two triangles.
a0 = m.vertex(0.0, 2.0, 0.0)   # 0
a1 = m.vertex(1.0, 2.0, 0.0)   # 1
a2 = m.vertex(0.5, 3.0, 0.0)   # 2
a3 = m.vertex(0.0, 3.0, 0.0)   # 3

t0 = m.triangle(a0, a1, a2)    # 0: top-patch lower triangle
t1 = m.triangle(a0, a2, a3)    # 1: top-patch upper triangle

# Bottom patch: two triangles at a different location.
b0 = m.vertex(2.0, 0.0, 0.0)   # 4
b1 = m.vertex(3.0, 0.0, 0.0)   # 5
b2 = m.vertex(2.5, 1.0, 0.0)   # 6
b3 = m.vertex(2.0, 1.0, 0.0)   # 7

t2 = m.triangle(b0, b1, b2)    # 2: bottom-patch lower triangle
t3 = m.triangle(b0, b2, b3)    # 3: bottom-patch upper triangle

# Top patch interior edge — n=2.
m.assert_edge_shared(a0, a2, 2)

# Bottom patch interior edge — n=2.
m.assert_edge_shared(b0, b2, 2)

# Top patch boundary edges — n=1 each.
m.assert_edge_shared(a0, a1, 1)
m.assert_edge_shared(a1, a2, 1)  # gve candidate
m.assert_edge_shared(a2, a3, 1)
m.assert_edge_shared(a0, a3, 1)

# Bottom patch boundary edges — n=1 each.
m.assert_edge_shared(b0, b1, 1)
m.assert_edge_shared(b1, b2, 1)  # gwe candidate: t1 non-NULL → v2 selected
m.assert_edge_shared(b2, b3, 1)
m.assert_edge_shared(b0, b3, 1)

# The two patches are disconnected components.
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=8, E=10, F=4, chi=2 (two separate open disks).
m.assert_euler_characteristic(8, 10, 4, 2)
