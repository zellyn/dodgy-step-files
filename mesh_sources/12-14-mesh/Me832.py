"""Me832 — is_non_manifold_vertex cycle-break-condition: interior vertex whose halfedge ring traverses completely back to start (Branch 3).

CGAL PMP `PMP.is_non_manifold_vertex` Branch 3 (*cycle-break-condition*) @ line 79:
  'halfedge_descriptor h = halfedge(v, tmesh);
   do { ... h = prev(opposite(h, tmesh), tmesh); } while(h != start);'
  — when walking the halfedge ring around vertex v, the traversal terminates when
  h returns to the starting halfedge. For an interior vertex on a closed mesh (no
  boundary edge incident at v), the ring is a complete cycle: every halfedge in the
  star is visited and the loop exits via the break condition (h == start). The vertex
  has no null faces → border_counter remains 0 → function returns false (manifold).

Defect pattern: a closed patch of four triangles forming a diamond/quad with a
  central interior vertex v0. The four triangles fan around v0, each pair sharing
  an edge. v0 has no boundary edge → its halfedge ring completes a full cycle.
  Branch 3 (the break/exit condition) fires when the traversal returns to start.

Geometry (diamond, 5 vertices):
  v0=(0,0,0)   — central interior vertex under test
  v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0)  — outer ring
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
  Interior edges at v0: (v0,v1), (v0,v2), (v0,v3), (v0,v4) all n=2.
  Outer boundary: (v1,v2), (v2,v3), (v3,v4), (v4,v1) all n=1.
  v0 has no boundary halfedge → cycle terminates via break, border_counter=0.

Euler: V=5, E=8, F=4, chi=5-8+4=1 (open disk topology).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me832",
    title="is_non_manifold_vertex cycle-break-condition: interior vertex v0 in closed 4-triangle fan; halfedge ring completes full cycle via break (Branch 3)",
    defect_class="non_manifold_vertex",
)

v0 = m.vertex( 0.0,  0.0, 0.0)   # 0 — interior vertex (ring traversal terminates via break)
v1 = m.vertex( 1.0,  0.0, 0.0)   # 1 — outer right
v2 = m.vertex( 0.0,  1.0, 0.0)   # 2 — outer top
v3 = m.vertex(-1.0,  0.0, 0.0)   # 3 — outer left
v4 = m.vertex( 0.0, -1.0, 0.0)   # 4 — outer bottom

# Four triangles forming a complete fan around v0.
t0 = m.triangle(v0, v1, v2)   # right-upper
t1 = m.triangle(v0, v2, v3)   # left-upper
t2 = m.triangle(v0, v3, v4)   # left-lower
t3 = m.triangle(v0, v4, v1)   # right-lower

# All four spokes at v0 are interior edges (each shared by 2 triangles).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)

# Outer boundary edges (n=1).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)

# v0's ring is a complete cycle with no null-face incident halfedges.
# Euler: V=5, E=8, F=4, chi=1.
m.assert_euler_characteristic(5, 8, 4, 1)
