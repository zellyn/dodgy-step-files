"""Me1010 — run_stitch_borders vertex-merge-necessity: h1_tgt representative differs; merge into v_to_keep (Branch 1).

CGAL PMP `PMP.run_stitch_borders` Branch 1 (*vertex-merge-necessity*) @ line 597:
  'if(get(uvpm, h1_tgt) != get(uvpm, v_to_keep))'
  — when the union-find representative of the border halfedge target vertex h1_tgt
  differs from the chosen master v_to_keep, Branch 1 fires: all halfedges currently
  pointing at h1_tgt's old representative are redirected to v_to_keep.

The fixture models two open triangulated patches (patch A: t0,t1; patch B: t2,t3)
whose right/left boundary edges should be stitched. Boundary vertex h1_tgt on
patch A is at (1,0,0) and its exact counterpart on patch B (h2_src) is also at
(1,0,0) — stored as separate vertex indices 1 and 4. The union-find initially
assigns each vertex its own representative. When the merger processes halfedge h1
(A's boundary edge bottom-to-top), h1_tgt=v1 has representative v1 while
v_to_keep=v4; they differ → Branch 1 fires and re-points h1_tgt → v_to_keep.

Geometry:
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0)
    t0=(v0,v1,v2), t1=(v0,v2,v3) — open right edge v1-v2
  Patch B: v4=(1,0,0), v5=(1,1,0), v6=(2,0,0), v7=(2,1,0)
    t2=(v4,v6,v7), t3=(v4,v7,v5) — open left edge v4-v5
  Coincident pairs: v1==v4 at (1,0,0), v2==v5 at (1,1,0)
  Boundary seam: edge(v1,v2) on A, edge(v4,v5) on B
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1010",
    title="run_stitch_borders vertex-merge-necessity: h1_tgt representative differs from v_to_keep; redirect to master (Branch 1)",
    defect_class="open_boundary_stitch_gap",
)

# Patch A: two triangles, open right boundary edge v1-v2.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left-bottom
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — right-bottom (h1_tgt of boundary halfedge)
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — right-top
v3 = m.vertex(0.0, 1.0, 0.0)  # 3 — left-top

t0 = m.triangle(v0, v1, v2)   # 0: lower triangle of patch A
t1 = m.triangle(v0, v2, v3)   # 1: upper triangle of patch A

# Patch B: two triangles, open left boundary edge v4-v5.
v4 = m.vertex(1.0, 0.0, 0.0)  # 4 — coincident with v1 (v_to_keep candidate)
v5 = m.vertex(1.0, 1.0, 0.0)  # 5 — coincident with v2
v6 = m.vertex(2.0, 0.0, 0.0)  # 6 — right-bottom of patch B
v7 = m.vertex(2.0, 1.0, 0.0)  # 7 — right-top of patch B

t2 = m.triangle(v4, v6, v7)   # 2: lower triangle of patch B
t3 = m.triangle(v4, v7, v5)   # 3: upper triangle of patch B

# Boundary seam edges — each incident on exactly 1 triangle (open boundary).
m.assert_edge_shared(v1, v2, 1)   # patch A open seam: h1 boundary halfedge
m.assert_edge_shared(v4, v5, 1)   # patch B open seam: h2 boundary halfedge

# Near-coincident pairs confirming the unstitched stitch targets.
# h1_tgt=v1 and v_to_keep=v4 are at (1,0,0) — representatives differ → Branch 1.
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# No shared triangle between coincident pairs (they belong to different patches).
m.assert_vertex_pair_no_shared_triangle(v1, v4)
m.assert_vertex_pair_no_shared_triangle(v2, v5)

# Euler: two disconnected open patches, no shared topology.
# Patch A: V=4, E=5, F=2, chi=1. Patch B: V=4, E=5, F=2, chi=1. Combined: chi=2.
m.assert_euler_characteristic(8, 10, 4, 2)
