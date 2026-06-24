"""Me1011 — run_stitch_borders second-vertex-pair-distinct: h2_src differs from h1_tgt; merge h2_src conditionally (Branch 2).

CGAL PMP `PMP.run_stitch_borders` Branch 2 (*second-vertex-pair-distinct*) @ line 603:
  'if(get(uvpm, h2_src) != get(uvpm, h1_tgt))'
  — after handling h1_tgt merge, the algorithm checks whether h2 halfedge's source
  vertex (h2_src) has a different representative from h1_tgt's master. If distinct,
  Branch 2 fires and h2_src is also merged into the same master vertex.

The fixture uses two L-shaped open patches with a two-edge shared boundary seam
(three boundary vertices per side). Halfedge h1 runs along the bottom segment of
the seam; its source is h1_src at (0,0,0) and its target h1_tgt at (1,0,0). The
corresponding h2 runs in the opposite direction: h2_src at (1,0,0) [patch B's
counterpart to h1_tgt] and h2_tgt at (0,0,0) [patch B's counterpart to h1_src].
Since h2_src's initial representative is patch B's local vertex (index 5, at
(1,0,0)) while h1_tgt's master is patch A's vertex (index 1, at (1,0,0)), the
check 'h2_src != h1_tgt representative' is true → Branch 2 fires.

Geometry:
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(1,1,0)
    t0=(v0,v1,v3), t1=(v1,v2,v3) — open bottom seam v0-v1-v2
  Patch B: v4=(0,0,0), v5=(1,0,0), v6=(2,0,0), v7=(1,-1,0)
    t2=(v4,v7,v5), t3=(v5,v7,v6) — open top seam v4-v5-v6 (coincident with A's bottom)
  Coincident pairs: v0==v4 at (0,0,0), v1==v5 at (1,0,0), v2==v6 at (2,0,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1011",
    title="run_stitch_borders second-vertex-pair-distinct: h2_src representative differs from h1_tgt master; conditional merge fires (Branch 2)",
    defect_class="open_boundary_stitch_gap",
)

# Patch A: two triangles sharing apex v3=(1,1,0); open seam along y=0.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — seam left (h1_src in one halfedge)
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — seam mid  (h1_tgt of h1; v_to_keep)
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — seam right
v3 = m.vertex(1.0, 1.0, 0.0)  # 3 — apex above

t0 = m.triangle(v0, v1, v3)   # 0: left triangle of patch A
t1 = m.triangle(v1, v2, v3)   # 1: right triangle of patch A

# Patch B: two triangles sharing apex v7=(1,-1,0); open seam along y=0.
v4 = m.vertex(0.0, 0.0, 0.0)  # 4 — coincident with v0 (h2_tgt after direction flip)
v5 = m.vertex(1.0, 0.0, 0.0)  # 5 — coincident with v1 (h2_src; different rep from h1_tgt)
v6 = m.vertex(2.0, 0.0, 0.0)  # 6 — coincident with v2
v7 = m.vertex(1.0, -1.0, 0.0) # 7 — apex below

t2 = m.triangle(v4, v7, v5)   # 2: left triangle of patch B
t3 = m.triangle(v5, v7, v6)   # 3: right triangle of patch B

# Open seam edges — each incident on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)   # patch A seam segment left
m.assert_edge_shared(v1, v2, 1)   # patch A seam segment right
m.assert_edge_shared(v4, v5, 1)   # patch B seam segment left (coincident with A's left)
m.assert_edge_shared(v5, v6, 1)   # patch B seam segment right (coincident with A's right)

# Near-coincident pairs: three vertex pairs across the seam.
# h2_src=v5 at (1,0,0) has own representative != h1_tgt=v1's master → Branch 2 fires.
m.assert_vertex_pair_distance_lt(v0, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v5, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v6, 1e-9)

# No shared triangle between coincident cross-patch pairs.
m.assert_vertex_pair_no_shared_triangle(v0, v4)
m.assert_vertex_pair_no_shared_triangle(v1, v5)
m.assert_vertex_pair_no_shared_triangle(v2, v6)

# Euler: Patch A: V=4, E=5, F=2, chi=1. Patch B: V=4, E=5, F=2, chi=1. Combined chi=2.
m.assert_euler_characteristic(8, 10, 4, 2)
