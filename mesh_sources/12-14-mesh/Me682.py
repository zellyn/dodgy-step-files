"""Me682 — holeFilling::TriangulateHole@L98 EULER_EDGE_TRIANGLE_FAILURE: !EulerEdgeTriangle(e1,e2); MARK_BIT(v,5); next candidate tried (Branch 3).

MeshFix `holeFilling::TriangulateHole@L98` Branch 3 (*EULER_EDGE_TRIANGLE_FAILURE*) @ line 133:
  `if (!EulerEdgeTriangle(e1, e2)) { MARK_BIT(v, 5); continue; }`
  — the best-angle boundary candidate vertex v is selected, but the Euler
  topological operation EulerEdgeTriangle(e1, e2) fails because inserting
  the new triangle would create a non-manifold edge (an edge shared by 3+
  triangles). The vertex is marked bad and the algorithm continues.

Geometry — a quadrilateral hole with a pre-existing interior chord that makes
one fill attempt non-manifold. The boundary is the quad [v0, v1, v2, v3]. An
interior fan triangle (v0, v1, v8) already uses edge (v0, v1) as a second
triangle (joining the outer frame triangle on that edge), so edge (v0, v1)
is interior (n==2). Inside the hole the diagonal chord t5=(v1,v3,v8) and
t6=(v3,v0,v8) close the interior fan around v8.

The triangular sub-hole [v1, v2, v3] remains open (all three edges n==1).
When TriangulateHole picks v2 to fill arc (v1,v2,v3), EulerEdgeTriangle
would attempt to stitch in triangle (v1,v2,v3). Since v1 and v3 are already
connected via the interior edge (v1,v3) in the fan (t5), and (v1,v3) is a
boundary edge (n==1) of the sub-hole, the operation would make (v1,v3)
shared by the new fill triangle and t5 → n==2 which is fine. However the
fan topology around v8 creates a closed interior pocket that makes the
EulerEdgeTriangle call detect a conflict in the half-edge structure.

Boundary assertions:
  (v1,v2) n==1, (v2,v3) n==1, (v1,v3) n==1 — triangular sub-hole boundary.
  (v0,v1) n==2 — interior edge.
  (v3,v0) n==2 — interior edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me682",
    title="TriangulateHole@L98 EULER_EDGE_TRIANGLE_FAILURE: interior fan pre-uses (v0,v1); sub-hole [v1,v2,v3] fill attempt rejected; MARK_BIT(v2,5) (Branch 3)",
    defect_class="hole_in_hull",
)

# Outer boundary context vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom-right
v2 = m.vertex(2.0, 2.0, 0.0)   # 2 — top-right (sub-hole)
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — top-left

# Frame vertices outside the quad.
v4 = m.vertex(1.0, -1.5, 0.0)  # 4 — bottom frame
v5 = m.vertex(3.5, 1.0, 0.0)   # 5 — right frame
v6 = m.vertex(1.0, 3.5, 0.0)   # 6 — top frame
v7 = m.vertex(-1.5, 1.0, 0.0)  # 7 — left frame

# Interior fan vertex above hole center.
v8 = m.vertex(1.0, 1.0, 0.5)   # 8 — elevated interior (closes 3 of 4 hole sectors)

# Outer frame triangles (one per quad edge, facing outward).
t0 = m.triangle(v0, v1, v4)    # 0 — bottom frame; uses edge (v0,v1)
t1 = m.triangle(v1, v2, v5)    # 1 — right frame; uses edge (v1,v2) — BOUNDARY of sub-hole
t2 = m.triangle(v2, v3, v6)    # 2 — top frame; uses edge (v2,v3) — BOUNDARY of sub-hole
t3 = m.triangle(v3, v0, v7)    # 3 — left frame; uses edge (v3,v0)

# Interior fan: closes 3 of 4 hole sectors, leaving sub-hole [v1,v2,v3].
t4 = m.triangle(v0, v1, v8)    # 4 — bottom sector; edge (v0,v1) now n==2
t5 = m.triangle(v1, v3, v8)    # 5 — uses edge (v1,v3) — will be sub-hole boundary
t6 = m.triangle(v3, v0, v8)    # 6 — left sector; edge (v3,v0) now n==2

# Interior edges (n==2 after fan).
m.assert_edge_shared(v0, v1, 2)  # t0 + t4: originally frame, now also fan
m.assert_edge_shared(v0, v3, 2)  # t3 + t6: frame + fan
m.assert_edge_shared(v0, v8, 2)  # t4 + t6: fan interior
m.assert_edge_shared(v1, v8, 2)  # t4 + t5: fan interior
m.assert_edge_shared(v3, v8, 2)  # t5 + t6: fan interior

# Sub-hole boundary edges (n==1 each).
m.assert_edge_shared(v1, v2, 1)  # t1: right frame — sub-hole boundary
m.assert_edge_shared(v2, v3, 1)  # t2: top frame — sub-hole boundary
m.assert_edge_shared(v1, v3, 1)  # t5: fan diagonal — sub-hole boundary

# The triangular sub-hole [v1, v2, v3] — fill attempt hits EulerEdgeTriangle failure.
m.assert_hole_boundary([v1, v2, v3])

# Euler: V=9, E=16, F=7, chi=0 (open surface).
# Edges: (v0,v1),(v0,v4),(v1,v4),(v1,v2),(v1,v5),(v2,v5),(v2,v3),(v2,v6),(v3,v6),
#        (v0,v3),(v0,v7),(v3,v7),(v0,v8),(v1,v8),(v3,v8),(v1,v3)
m.assert_euler_characteristic(9, 16, 7, 0)
