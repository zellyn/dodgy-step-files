"""Me702 — Basic_TMesh.bridgeBoundaries branch 3: gve_endpoint_selection.

MeshFix `Basic_TMesh.bridgeBoundaries` Branch 3 (*gve_endpoint_selection*) @ line 439:
  'v1 = (gve->t1) ? (gve->v1) : (gve->v2);'
  — for a boundary edge gve, exactly one of t1/t2 is NULL (boundary
  condition). Branch 3 fires the true arm: gve->t1 is non-NULL, so the
  free (unattached) endpoint of gve is gve->v1. This selects which
  vertex of gve will anchor the first bridge triangle.

Defect pattern: two disjoint boundary edges (no shared vertex) where
  gve has its t1 slot occupied by a triangle — i.e., the triangle is
  stored in t1 rather than t2. The MeshFix half-edge structure assigns
  the incident triangle to t1 or t2; when t1 is set, v1 is the free
  vertex (the vertex not shared by the triangle on t1 side).

Geometry: four triangles forming an L-shape with two disjoint open edges.
  Left patch: t0=(v0,v1,v2), t1=(v0,v2,v3) sharing edge (v0,v2).
  Right patch: t2=(v4,v5,v6), t3=(v4,v6,v7) sharing edge (v4,v6).
  Boundary edges on left patch open side: (v1,v2) n=1, (v0,v1) n=1, (v2,v3) n=1, (v0,v3) n=1.
  Boundary edges on right patch open side: (v5,v6) n=1, (v4,v5) n=1, (v6,v7) n=1, (v4,v7) n=1.
  The two patches are spatially disjoint — no shared vertices.
  gve = boundary edge from left patch where t1 is non-NULL → v1 selected.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me702",
    title="bridgeBoundaries gve_endpoint_selection: gve->t1 non-NULL selects gve->v1 as free endpoint; disjoint boundary edges on separate patches (Branch 3)",
    defect_class="boundary_hole",
)

# Left patch: two triangles, open on their right boundary.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)   # 0: left-patch lower triangle
t1 = m.triangle(v0, v2, v3)   # 1: left-patch upper triangle

# Right patch: two triangles spatially separate, open on their left boundary.
v4 = m.vertex(3.0, 0.0, 0.0)  # 4
v5 = m.vertex(4.0, 0.0, 0.0)  # 5
v6 = m.vertex(3.5, 1.0, 0.0)  # 6
v7 = m.vertex(3.0, 1.0, 0.0)  # 7

t2 = m.triangle(v4, v5, v6)   # 2: right-patch lower triangle
t3 = m.triangle(v4, v6, v7)   # 3: right-patch upper triangle

# Left patch interior edge — n=2.
m.assert_edge_shared(v0, v2, 2)

# Right patch interior edge — n=2.
m.assert_edge_shared(v4, v6, 2)

# Left patch boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)  # gve candidate: boundary edge on left patch
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Right patch boundary edges — n=1 each.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)  # gwe candidate: boundary edge on right patch
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v4, v7, 1)

# The two patches are disconnected components.
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=8, E=10, F=4, chi=2 (two separate open disks, each chi=1).
m.assert_euler_characteristic(8, 10, 4, 2)
