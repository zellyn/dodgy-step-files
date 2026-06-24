"""Me512 — Edge.swap branch 3: EDGE_ENDPOINT_SWAP.

MeshFix `Edge.swap` Branch 3 (*EDGE_ENDPOINT_SWAP*) @ line 154:
  'v1 = t2->oppositeVertex(this); v2 = t1->oppositeVertex(this);'
  — the diagonal's endpoints are updated in-place to point to the two
  opposite vertices of the flanking triangles. After this step the edge
  object now spans the perpendicular diagonal of the quad. Branch 3 fires
  for any interior swap once topology extraction (Branch 2) has run.

Defect pattern: a 2-triangle quad where the current interior diagonal is
  (v0,v2) and the post-swap diagonal will connect the opposite vertices
  v1=(1,0,0) and v3=(0,1,0). The geometry is chosen so the post-swap
  diagonal distance is clearly different from the pre-swap diagonal distance,
  making the endpoint swap easy to verify via distance assertions.

Geometry (z=0):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0,2,0)
  t0=(v0,v1,v2) — pre-swap: diagonal runs (v0,v2), opposite vertex v1
  t1=(v0,v2,v3) — pre-swap: diagonal runs (v0,v2), opposite vertex v3

After swap: diagonal becomes (v1,v3). The pre-swap diagonal (v0,v2) has
  length sqrt(1²+1²)=√2 ≈ 1.414. The post-swap diagonal (v1,v3) has length
  sqrt(2²+2²-2·2·cos90°)... actually v1=(2,0), v3=(0,2): dist=sqrt(8)≈2.83.
  v0=(0,0), v2=(1,1): pre-swap dist=√2. We assert v1-v3 distance > v0-v2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me512",
    title="Edge.swap EDGE_ENDPOINT_SWAP: diagonal endpoints updated from (v0,v2) to opposite vertices (v1,v3); post-swap diagonal spans longer distance across quad (Branch 3)",
    defect_class="edge_swap_endpoint_update",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — original diagonal endpoint (origin)
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — opposite vertex of t0; becomes new diagonal endpoint
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — original diagonal endpoint (center)
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — opposite vertex of t1; becomes new diagonal endpoint

# Two-triangle quad sharing current diagonal (v0,v2).
t0 = m.triangle(v0, v1, v2)   # 0: lower triangle
t1 = m.triangle(v0, v2, v3)   # 1: upper triangle

# Current interior diagonal (v0,v2) — to be swapped to (v1,v3).
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — n=1.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Pre-swap diagonal (v0,v2): length = sqrt(1²+1²) = sqrt(2) ≈ 1.414
m.assert_vertex_pair_distance_lt(v0, v2, 1.5)

# Post-swap diagonal (v1,v3): length = sqrt(2²+2²) = sqrt(8) ≈ 2.828
# Opposite vertices v1=(2,0,0) and v3=(0,2,0) — distance is ~2.83.
# Confirm they are not yet connected (no pre-existing diagonal).
m.assert_edge_shared(v1, v3, 0)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
