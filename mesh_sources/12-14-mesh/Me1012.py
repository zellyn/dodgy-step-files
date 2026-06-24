"""Me1012 — run_stitch_borders second-target-merge-necessity: h2_tgt representative differs from master; union_find merge fires (Branch 3).

CGAL PMP `PMP.run_stitch_borders` Branch 3 (*second-target-merge-necessity*) @ line 615:
  'if(get(uvpm, h2_tgt) != get(uvpm, v_to_keep))'
  — after stitching the h1_tgt side, the algorithm handles the second endpoint:
  h2_tgt (the target of halfedge h2, which coincides with h1's source). When
  h2_tgt's representative in the union-find differs from the chosen master for
  that second vertex, Branch 3 fires and all halfedges pointing at h2_tgt's old
  representative are updated to point to the second master.

The fixture uses two open fan-patches meeting at a two-vertex seam. Patch A has
a triangular fan with apex at v4=(0.5,1,0); patch B has an apex at v8=(0.5,-1,0).
The boundary seam is the edge (v0,v1) = ((0,0,0),(1,0,0)). When run_stitch_borders
processes the stitching pair for edge (v0,v1), halfedge h1 runs v0→v1 in patch A
and h2 runs v1→v0 in patch B. After h1_tgt=v1 is merged (Branch 1), the algorithm
examines h2_tgt=v0 in patch B. v0's patch-B counterpart (v5 at (0,0,0)) has its
own representative, distinct from the master for v0's seam position → Branch 3 fires.

Geometry:
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(-0.5,0,0), v3=(1.5,0,0), v4=(0.5,1,0)
    t0=(v0,v1,v4), t1=(v2,v0,v4), t2=(v1,v3,v4)
    Open seam: bottom edge (v0,v1)
  Patch B: v5=(0,0,0), v6=(1,0,0), v7=(-0.5,0,0), v8=(0.5,-1,0)
    t3=(v6,v5,v8), t4=(v5,v7,v8)
    Open seam: top edge (v5,v6)  [coincident with A's (v0,v1)]
  Coincident pairs: v0==v5 at (0,0,0), v1==v6 at (1,0,0)
  h1: A-halfedge v0→v1; h2: B-halfedge v6→v5; h2_tgt=v5 has its own representative
  distinct from v0's master → Branch 3 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1012",
    title="run_stitch_borders second-target-merge-necessity: h2_tgt representative differs from second-endpoint master; union_find merge fires (Branch 3)",
    defect_class="open_boundary_stitch_gap",
)

# Patch A: three-triangle fan, open seam edge (v0,v1).
v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — seam left  (h1_src)
v1 = m.vertex(1.0,  0.0, 0.0)  # 1 — seam right (h1_tgt)
v2 = m.vertex(-0.5, 0.0, 0.0)  # 2 — left wing
v3 = m.vertex(1.5,  0.0, 0.0)  # 3 — right wing
v4 = m.vertex(0.5,  1.0, 0.0)  # 4 — apex above

t0 = m.triangle(v0, v1, v4)    # 0: centre-top triangle
t1 = m.triangle(v2, v0, v4)    # 1: left-top triangle
t2 = m.triangle(v1, v3, v4)    # 2: right-top triangle

# Patch B: two-triangle open strip, open seam edge (v5,v6).
v5 = m.vertex(0.0,  0.0, 0.0)  # 5 — coincident with v0 (h2_tgt; representative differs)
v6 = m.vertex(1.0,  0.0, 0.0)  # 6 — coincident with v1 (h2_src)
v7 = m.vertex(-0.5, 0.0, 0.0)  # 7 — left wing of patch B
v8 = m.vertex(0.5, -1.0, 0.0)  # 8 — apex below

t3 = m.triangle(v6, v5, v8)    # 3: centre-bottom triangle of patch B
t4 = m.triangle(v5, v7, v8)    # 4: left-bottom triangle of patch B

# Open seam edges — each on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)   # patch A seam edge (h1's edge)
m.assert_edge_shared(v5, v6, 1)   # patch B seam edge (h2's edge; coincident with A's)

# Near-coincident pairs confirming the unstitched seam.
# h2_tgt=v5 at (0,0,0) has its own union-find rep != v0's master → Branch 3 fires.
m.assert_vertex_pair_distance_lt(v0, v5, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v6, 1e-9)

# No shared triangle between cross-patch coincident pairs.
m.assert_vertex_pair_no_shared_triangle(v0, v5)
m.assert_vertex_pair_no_shared_triangle(v1, v6)

# Euler: Patch A: V=5, E=7, F=3, chi=1.
#        Patch B: V=4, E=5, F=2, chi=1. Combined: V=9, E=12, F=5, chi=2.
m.assert_euler_characteristic(9, 12, 5, 2)
