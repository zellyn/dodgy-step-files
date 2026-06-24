"""Me1100 — CreateTriangleFromVertices_over_constrained_e1: e1 already has 2 triangles (Branch 1).

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 1 (*OVER_CONSTRAINED_EDGE*) @ line 263:
  `if (IS_BIT(e1, 5)) { ... }`
  When edge e1 (the first edge computed from the three input vertices) already has
  two incident triangles, it is over-constrained — adding a third triangle would
  create a non-manifold configuration. Branch 1 detects IS_BIT(e1,5) and duplicates
  the edge to avoid the topological conflict.

In the MeshFix half-edge structure each edge has exactly two triangle slots (t1, t2).
BIT 5 on an edge signals that both slots are occupied. CreateTriangleFromVertices
checks e1 first; if set it creates a fresh copy of the edge so the new triangle
gets an unshared edge object.

Defect carrier: edge (v0,v1) is shared by three triangles — the two base triangles
t0=(v0,v1,v2) and t1=(v0,v1,v3) fill both t1/t2 slots of e1. A third triangle
t2=(v0,v1,v4) attempts to use the same edge as e1, triggering IS_BIT(e1,5).

Geometry (star fan around edge (v0,v1)):
  v0=(0,0,0), v1=(1,0,0) — shared edge endpoints
  v2=(0.5, 1.0, 0)   — apex of base triangle t0
  v3=(0.5,-1.0, 0)   — apex of base triangle t1
  v4=(0.5, 0.0, 1.0) — apex of new triangle t2 (out-of-plane)
  t0=(v0,v1,v2), t1=(v0,v1,v3) — fill both slots of edge (v0,v1)
  t2=(v0,v1,v4) — third triangle; e1=(v0,v1) is over-constrained → Branch 1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1100",
    title="CreateTriangleFromVertices_over_constrained_e1: e1=(v0,v1) already has 2 triangles; IS_BIT(e1,5) triggers edge duplication (Branch 1)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — shared edge tail
v1 = m.vertex(1.0,  0.0, 0.0)   # 1 — shared edge head
v2 = m.vertex(0.5,  1.0, 0.0)   # 2 — apex of t0 (above plane)
v3 = m.vertex(0.5, -1.0, 0.0)   # 3 — apex of t1 (below plane)
v4 = m.vertex(0.5,  0.0, 1.0)   # 4 — apex of t2 (out-of-plane)

# Two base triangles fill both slots of edge (v0,v1).
t0 = m.triangle(v0, v1, v2)   # 0 — occupies e1->t1
t1 = m.triangle(v0, v1, v3)   # 1 — occupies e1->t2

# Third triangle: e1=(v0,v1) is over-constrained — IS_BIT(e1,5) fires → Branch 1.
t2 = m.triangle(v0, v1, v4)   # 2 — third sharer of (v0,v1)

# Edge (v0,v1) is incident on 3 triangles — the over-constrained defect.
m.assert_edge_shared(v0, v1, 3)

# All other edges are boundary (each on exactly 1 triangle).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
