"""Me513 — Edge.swap branch 4: TRIANGLE_EDGE_REPLACEMENT.

MeshFix `Edge.swap` Branch 4 (*TRIANGLE_EDGE_REPLACEMENT*) @ line 156:
  't1->replaceEdge(e1, e3); t2->replaceEdge(e3, e1);'
  — after updating the diagonal's endpoints, each triangle's edge cycle is
  repaired: t1 loses its old next-edge e1 and gains e3 (which belonged to t2),
  and vice versa. This cross-replacement keeps both triangles' edge-cycle links
  consistent with the new topology. Branch 4 fires for every successful swap.

Defect pattern: a 2-triangle quad where the edge cycle must be cross-linked
  after the diagonal flip. The geometry is a right-angle quad so the
  pre-swap and post-swap topology are easy to reason about: the diagonal
  (v0,v2) flips to (v1,v3) and both triangles adopt the other's outer edge.

Geometry (z=0):
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
  t0=(v0,v1,v2) — lower-right triangle; e1=edge(v2,v0) is nextEdge(diag)
  t1=(v0,v2,v3) — upper-left triangle; e3=edge(v2,v3) is nextEdge(diag)
  After swap: t1 replaces e1 with e3; t2 replaces e3 with e1.

The two triangles share diagonal (v0,v2) with n=2; the outer square boundary
  edges each have n=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me513",
    title="Edge.swap TRIANGLE_EDGE_REPLACEMENT: right-angle quad; t1->replaceEdge(e1,e3) and t2->replaceEdge(e3,e1) cross-links outer edges into new triangles (Branch 4)",
    defect_class="edge_swap_triangle_edge_replacement",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — bottom right
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — top right
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — top left

# Two-triangle quad sharing diagonal (v0,v2).
# t0 owns edges (v0,v1), (v1,v2), (v0,v2).
# t1 owns edges (v0,v2), (v2,v3), (v0,v3).
# After swap: t0 will contain (v1,v2),(v2,v3),(v1,v3); t1 will contain (v0,v1),(v0,v3),(v1,v3).
t0 = m.triangle(v0, v1, v2)   # 0: lower-right triangle
t1 = m.triangle(v0, v2, v3)   # 1: upper-left triangle

# Interior diagonal — cross-linked to both triangles.
m.assert_edge_shared(v0, v2, 2)

# Outer square edges — boundary.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Post-swap diagonal (v1,v3) does not yet exist.
m.assert_edge_shared(v1, v3, 0)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
