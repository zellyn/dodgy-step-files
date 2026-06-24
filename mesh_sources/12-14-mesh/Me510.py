"""Me510 — Edge.swap branch 1: EDGE_SWAP_SAFE_VALIDITY.

MeshFix `Edge.swap` Branch 1 (*EDGE_SWAP_SAFE_VALIDITY*) @ line 147:
  'if (!fast && (t1 == NULL || t2 == NULL || getCommonEdge(t1->oppositeVertex(this),
   t2->oppositeVertex(this)) != NULL)) return false;'
  — in safe mode the swap is rejected when: (a) the candidate edge is a boundary
  edge (t1 or t2 is NULL), OR (b) an edge already connects the two opposite
  vertices (the would-be post-swap diagonal already exists). Branch 1 fires
  whenever safe-mode finds such a blocking condition and returns false.

Defect pattern (boundary-edge block): a single triangle where all three edges
  are boundary edges (n=1, i.e., each edge has only one incident triangle, so
  t2 is NULL for all of them). Calling Edge.swap in safe mode on any of these
  edges returns false immediately because t2 == NULL.

Geometry (z=0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0)
  t0=(v0,v1,v2) — the sole triangle; all three edges are boundary edges.

All edges are boundary (n=1), fulfilling the t1==NULL || t2==NULL condition.
Safe-mode swap returns false for every edge in this mesh.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me510",
    title="Edge.swap EDGE_SWAP_SAFE_VALIDITY: boundary edge (n=1, t2==NULL) blocks safe-mode swap; all three edges are boundary (Branch 1)",
    defect_class="edge_swap_blocked_boundary_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — bottom right
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — apex

# Single triangle — all edges are boundary edges (n=1).
t0 = m.triangle(v0, v1, v2)

# Every edge has only one incident triangle — the swap-safe guard fires for all.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Euler: V=3, E=3, F=1, chi=1 (open disk).
m.assert_euler_characteristic(3, 3, 1, 1)
