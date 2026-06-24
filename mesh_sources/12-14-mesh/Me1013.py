"""Me1013 — run_stitch_borders opposite-edge-source-merge: h1_src distinct from h2_tgt; conditional merge fires (Branch 4).

CGAL PMP `PMP.run_stitch_borders` Branch 4 (*opposite-edge-source-merge*) @ line 621:
  'if(get(uvpm, h1_src) != get(uvpm, v_to_keep_2))'
  — after handling the h2_tgt side of the seam, the algorithm checks h1_src (the
  source of halfedge h1) against v_to_keep_2, the master for the second endpoint.
  When h1_src's union-find representative differs from v_to_keep_2, Branch 4 fires
  and h1_src is merged into the second master, completing the full two-endpoint
  stitch for this halfedge pair.

The fixture uses two open rectangular patches with a horizontal two-vertex seam.
Patch A (above) has a quad split into two triangles; patch B (below) mirrors it.
The stitch boundary is the edge (v0,v1) in patch A and (v4,v5) in patch B. When
run_stitch_borders processes the halfedge pair (h1: v0→v1 in A, h2: v5→v4 in B):
  - Branch 1 fires for h1_tgt=v1 vs v_to_keep=v5 (different reps)
  - Branch 2 fires for h2_src=v5 vs h1_tgt's new master
  - Branch 3 fires for h2_tgt=v4 vs v_to_keep_2
  - Branch 4 fires for h1_src=v0 vs v_to_keep_2=v4 (still distinct) → merge v0→v4

The key structural feature: h1_src=v0 at (0,0,0) has its own representative distinct
from the master assigned to h2_tgt=v4 at (0,0,0) until Branch 4 completes the merge.

Geometry:
  Patch A: v0=(0,0,0), v1=(2,0,0), v2=(0,2,0), v3=(2,2,0)
    t0=(v0,v1,v3), t1=(v0,v3,v2) — open bottom edge (v0,v1) = h1's edge
  Patch B: v4=(0,0,0), v5=(2,0,0), v6=(0,-2,0), v7=(2,-2,0)
    t2=(v5,v4,v6), t3=(v5,v6,v7) — open top edge (v4,v5) coincident with A's (v0,v1)
  Coincident pairs: v0==v4 at (0,0,0), v1==v5 at (2,0,0)
  h1: A-halfedge v0→v1 (going right along y=0)
  h2: B-halfedge v5→v4 (going left along y=0, opposite direction)
  h1_src=v0 distinct from h2_tgt master=v4 → Branch 4 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1013",
    title="run_stitch_borders opposite-edge-source-merge: h1_src representative distinct from h2_tgt master; merge completes two-endpoint stitch (Branch 4)",
    defect_class="open_boundary_stitch_gap",
)

# Patch A: two triangles, open bottom edge (v0,v1).
v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — bottom-left of A (h1_src; distinct from h2_tgt=v4)
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — bottom-right of A (h1_tgt)
v2 = m.vertex(0.0,  2.0, 0.0)  # 2 — top-left of A
v3 = m.vertex(2.0,  2.0, 0.0)  # 3 — top-right of A

t0 = m.triangle(v0, v1, v3)    # 0: lower-right triangle of patch A
t1 = m.triangle(v0, v3, v2)    # 1: upper-left triangle of patch A

# Patch B: two triangles, open top edge (v4,v5).
v4 = m.vertex(0.0,  0.0, 0.0)  # 4 — top-left of B, coincident with v0 (h2_tgt)
v5 = m.vertex(2.0,  0.0, 0.0)  # 5 — top-right of B, coincident with v1 (h2_src)
v6 = m.vertex(0.0, -2.0, 0.0)  # 6 — bottom-left of B
v7 = m.vertex(2.0, -2.0, 0.0)  # 7 — bottom-right of B

t2 = m.triangle(v5, v4, v6)    # 2: left triangle of patch B
t3 = m.triangle(v5, v6, v7)    # 3: right triangle of patch B

# Open seam edges — each on exactly 1 triangle (unstitched boundary).
m.assert_edge_shared(v0, v1, 1)   # patch A open bottom seam (h1's edge)
m.assert_edge_shared(v4, v5, 1)   # patch B open top seam (h2's edge)

# Near-coincident pairs: the stitch targets at both seam endpoints.
# h1_src=v0 at (0,0,0) has its own rep, distinct from h2_tgt=v4's master → Branch 4.
m.assert_vertex_pair_distance_lt(v0, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v5, 1e-9)

# No shared triangle between cross-patch coincident pairs (separate patches).
m.assert_vertex_pair_no_shared_triangle(v0, v4)
m.assert_vertex_pair_no_shared_triangle(v1, v5)

# Euler: Patch A: V=4, E=5, F=2, chi=1. Patch B: V=4, E=5, F=2, chi=1. Combined chi=2.
m.assert_euler_characteristic(8, 10, 4, 2)
