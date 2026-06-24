"""Me641 — holeFilling::fillSmallBoundaries VERTEX_ON_BOUNDARY: boundary vertex detected by isOnBoundary() (Branch 2).

MeshFix `holeFilling::fillSmallBoundaries` Branch 2 (*VERTEX_ON_BOUNDARY*) @ line 536:
  'if (v->isOnBoundary()) { ... }' — for each vertex of a candidate boundary loop,
  the algorithm checks whether the vertex lies on the mesh boundary. Boundary vertices
  get their boundary-edge count incremented as the loop is traversed. This branch
  fires for any open mesh where at least one vertex has an open half-edge ring.

Defect pattern: a 5-triangle open mesh with a triangular hole at the top (v3,v4,v5).
  Vertices v0 and v2 are clearly on the outer boundary (their edge rings are open).
  The hole boundary vertex v3 also has boundary edges (v0,v3) n=1.
  When fillSmallBoundaries traverses the hole boundary loop, it calls v->isOnBoundary()
  on each vertex; v3 is on boundary → Branch 2 fires and the boundary-edge count grd
  is incremented for that vertex.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(4,0,0) — bottom row
  v3=(1,2,0), v4=(3,2,0)             — middle row
  v5=(2,4,0)                          — top (hole apex)
  Triangles:
    t0=(v0,v1,v3), t1=(v1,v2,v4), t2=(v1,v3,v4), t3=(v2,v4,v5), t4=(v0,v2,v1)
  Hole: missing triangle (v3,v4,v5); edges (v3,v4) n=1, (v4,v5) n=1.
  Outer boundary: (v0,v3) n=1, (v0,v2) n=1, (v2,v5) n=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me641",
    title="holeFilling::fillSmallBoundaries VERTEX_ON_BOUNDARY: v->isOnBoundary() true for v3 on hole boundary; grd incremented (Branch 2)",
    defect_class="boundary_hole",
)

# Mesh vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left corner; boundary
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom-center
v2 = m.vertex(4.0, 0.0, 0.0)   # 2 — bottom-right corner; boundary
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — middle-left; boundary (hole vertex + outer open)
v4 = m.vertex(3.0, 2.0, 0.0)   # 4 — middle-right; boundary (hole vertex)
v5 = m.vertex(2.0, 4.0, 0.0)   # 5 — top apex; boundary (hole vertex)

# Five triangles: open mesh with hole (v3,v4,v5) missing.
t0 = m.triangle(v0, v1, v3)    # 0: bottom-left
t1 = m.triangle(v1, v2, v4)    # 1: bottom-right
t2 = m.triangle(v1, v3, v4)    # 2: middle bridge; creates hole edge (v3,v4)
t3 = m.triangle(v2, v4, v5)    # 3: top-right; creates hole edge (v4,v5)
t4 = m.triangle(v0, v2, v1)    # 4: bottom connector; closes bottom strip

# Triangular hole: (v3, v4, v5). The filling triangle is absent.
# The hole gap between v3 and v5 has no spanning triangle.
m.assert_hole_boundary([v3, v4, v5])

# Hole-adjacent boundary edges (n=1).
m.assert_edge_shared(v3, v4, 1)   # only in t2=(1,3,4); confirms v3 on boundary of hole
m.assert_edge_shared(v4, v5, 1)   # only in t3=(2,4,5); confirms v4 on boundary of hole

# Outer boundary edges — v0, v2, v3 on mesh boundary.
m.assert_edge_shared(v0, v3, 1)   # only in t0=(0,1,3); confirms v3->isOnBoundary()
m.assert_edge_shared(v0, v2, 1)   # only in t4=(0,2,1)
m.assert_edge_shared(v2, v5, 1)   # only in t3=(2,4,5)

# Interior (n=2) edges confirming mesh connectivity.
m.assert_edge_shared(v0, v1, 2)   # t0=(0,1,3) and t4=(0,2,1)
m.assert_edge_shared(v1, v2, 2)   # t1=(1,2,4) and t4=(0,2,1)
m.assert_edge_shared(v1, v3, 2)   # t0=(0,1,3) and t2=(1,3,4)
m.assert_edge_shared(v1, v4, 2)   # t1=(1,2,4) and t2=(1,3,4)
m.assert_edge_shared(v2, v4, 2)   # t1=(1,2,4) and t3=(2,4,5)
