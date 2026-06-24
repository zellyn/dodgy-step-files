"""Me704 — Basic_TMesh.bridgeBoundaries branch 5: two_triangle_bridge.

MeshFix `Basic_TMesh.bridgeBoundaries` Branch 5 (*two_triangle_bridge*) @ line 444:
  'je = CreateEdge(v1, v2); je2 = CreateEdge(v2, gve->v2); je1 = CreateEdge(gwe->v1, v1);
   CreateTriangle(gve, je2, je); CreateTriangle(gwe, je1, je); return je;'
  — when two boundary edges are disjoint (no common vertex), the bridge
  requires 2 new triangles connected by 3 new edges (je, je1, je2).
  v1 and v2 are the free endpoints selected by Branches 3 and 4.

Defect pattern: a mesh with two topologically disjoint boundary edges that
  share no vertex. The gap between the two boundary loops is bridged by
  inserting 2 triangles. Each bridge triangle is anchored to one boundary
  edge plus the new connecting edges.

Geometry: six triangles in two separate triangulated patches.
  Left patch: t0=(p0,p1,p2), t1=(p1,p3,p2) — diamond shape open on right side.
  Right patch: t2=(q0,q1,q2), t3=(q1,q3,q2) — diamond shape open on left side.
  Additional triangles in each patch to make the boundary structure clear.
  The two open boundary edges (p1,p2) and (q0,q1) are disjoint — no shared vertex.
  bridgeBoundaries creates 3 new edges and 2 new triangles to close the gap.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me704",
    title="bridgeBoundaries two_triangle_bridge: disjoint boundary edges (p1,p2) and (q0,q2) bridged by CreateEdge x3 + CreateTriangle x2 (Branch 5)",
    defect_class="boundary_hole",
)

# Left patch — a quadrilateral divided into two triangles.
p0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left corner
p1 = m.vertex(1.0, 0.5, 0.0)  # 1 — right-bottom
p2 = m.vertex(1.0, 1.5, 0.0)  # 2 — right-top
p3 = m.vertex(0.0, 2.0, 0.0)  # 3 — top corner

t0 = m.triangle(p0, p1, p2)   # 0: lower triangle of left patch
t1 = m.triangle(p0, p2, p3)   # 1: upper triangle of left patch

# Right patch — a quadrilateral divided into two triangles.
q0 = m.vertex(3.0, 0.5, 0.0)  # 4 — left-bottom of right patch
q1 = m.vertex(4.0, 0.0, 0.0)  # 5 — right corner
q2 = m.vertex(3.0, 1.5, 0.0)  # 6 — left-top of right patch
q3 = m.vertex(4.0, 2.0, 0.0)  # 7 — top corner

t2 = m.triangle(q0, q1, q2)   # 2: lower triangle of right patch
t3 = m.triangle(q1, q3, q2)   # 3: upper triangle of right patch

# Left patch interior edge — n=2.
m.assert_edge_shared(p0, p2, 2)

# Right patch interior edge — n=2.
m.assert_edge_shared(q1, q2, 2)

# Left patch boundary edges — n=1 each.
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p1, p2, 1)  # gve: disjoint open boundary edge
m.assert_edge_shared(p2, p3, 1)
m.assert_edge_shared(p0, p3, 1)

# Right patch boundary edges — n=1 each.
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q0, q2, 1)  # gwe: disjoint open boundary edge
m.assert_edge_shared(q1, q3, 1)
m.assert_edge_shared(q2, q3, 1)

# The two patches are completely disconnected — no shared vertices.
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=8, E=10, F=4, chi=2 (two disjoint open disks, each chi=1).
m.assert_euler_characteristic(8, 10, 4, 2)
