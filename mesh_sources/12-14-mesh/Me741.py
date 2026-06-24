"""Me741 — TriangulateHole_L439_single_vertex_hole: hole has only one unvisited neighbor; nextEdge and prevEdge both boundary; return 0 (Branch 2).

MeshFix `holeFilling::TriangulateHole` Branch 2 (*SINGLE_VERTEX_HOLE*) @ line 453:
  'if (nextEdge(e)->isOnBoundary() && prevEdge(e)->isOnBoundary()) return 0'
  After confirming e is a boundary edge, the hole walk examines whether the next
  and previous edges around the hole are also boundary edges sharing the same
  vertex — meaning the hole degenerates to a single unvisited vertex (a cap where
  the hole rim collapses). Branch 2 returns 0 without filling.

Defect pattern: a triangular mesh where the hole is bounded by exactly 3
  boundary edges meeting at a single shared vertex (a pinched tip). Specifically:
  from seed edge e=(v0,v1), nextEdge(e) goes v1→v2 (boundary) and prevEdge(e)
  returns v2→v0 (boundary). The hole "triangle" is trivially closed — filling it
  would create a degenerate zero-area patch. Branch 2 detects this and aborts.

Geometry: a single triangle t0=(v0,v1,v2) forms the frame. The hole is the
  triangle itself, perceived from the inside — all 3 of its edges are boundary.
  A second isolated triangle t1=(v3,v4,v5) provides a non-degenerate component
  so the mesh is non-trivially structured.

  v0=(0,0,0), v1=(2,0,0), v2=(1,1.732,0)
  t0=(v0,v1,v2) — open equilateral triangle; all edges boundary (n=1).
  Each edge e has nextEdge(e) and prevEdge(e) both on the boundary of this same
  3-edge loop → Branch 2 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me741",
    title="TriangulateHole_L439_single_vertex_hole: 3-edge boundary loop; nextEdge and prevEdge both boundary; single-vertex hole cannot be triangulated; return 0 (Branch 2)",
    defect_class="hole_in_hull",
)

# Single open equilateral triangle — all edges boundary.
v0 = m.vertex(0.0, 0.0, 0.0)       # 0
v1 = m.vertex(2.0, 0.0, 0.0)       # 1
v2 = m.vertex(1.0, 1.732, 0.0)     # 2 — apex (~equilateral)

# A second non-degenerate triangle providing context.
v3 = m.vertex(4.0, 0.0, 0.0)       # 3
v4 = m.vertex(6.0, 0.0, 0.0)       # 4
v5 = m.vertex(5.0, 1.732, 0.0)     # 5

t0 = m.triangle(v0, v1, v2)   # 0 — main open triangle; all 3 edges boundary
t1 = m.triangle(v3, v4, v5)   # 1 — isolated reference triangle; also all-boundary

# t0 boundary edges (n=1 each) — this is the 3-edge hole loop.
m.assert_edge_shared(v0, v1, 1)   # seed edge e
m.assert_edge_shared(v1, v2, 1)   # nextEdge(e) — also boundary
m.assert_edge_shared(v0, v2, 1)   # prevEdge(e) — also boundary

# t1 boundary edges (n=1 each).
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# The 3-edge boundary loop of t0: v0→v1→v2→v0.
m.assert_hole_boundary([v0, v1, v2])
