"""Me217 — cutAndStitch_unbounded_singular_chain: cyclic singular chain pinched from interior.

MeshFix `Basic_TMesh.cutAndStitch` Branch 8 (*UNBOUNDED_SINGULAR_CHAIN*) @ line 1021:
  'if (e1->isLinked()) pinch(e1, false)'
  After bounded-chain pinches (Branch 7), any remaining linked singular edges
  form closed (cyclic) boundary loops with no endpoints. These unbounded chains
  are pinched with with_common_vertex=false — the merge starts from any interior
  edge of the cycle rather than from a specific endpoint.

Defect pattern: a closed boundary loop (hole in the hull) surrounded entirely
by triangles. The loop has no endpoints — every vertex in the loop connects to
exactly two boundary edges, forming a pure cycle. A healer must pinch from an
arbitrary interior edge to stitch this closed seam.

Geometry: a triangulated square with a square hole in the center.
  Outer ring: v0=(0,0,0), v1=(3,0,0), v2=(3,3,0), v3=(0,3,0)
  Inner hole: v4=(1,1,0), v5=(2,1,0), v6=(2,2,0), v7=(1,2,0)
  8 triangles forming a frame around the hole.

  t0=(v0,v1,v5), t1=(v0,v5,v4) — bottom strip
  t2=(v1,v2,v6), t3=(v1,v6,v5) — right strip
  t4=(v2,v3,v7), t5=(v2,v7,v6) — top strip
  t6=(v3,v0,v4), t7=(v3,v4,v7) — left strip

  The hole boundary (v4,v5,v6,v7) is a closed cycle with no endpoints —
  an unbounded singular chain that Branch 8 pinches with common_vertex=false.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me217",
             title="cutAndStitch_unbounded_singular_chain: closed hole boundary pinched from interior (with_common_vertex=false)",
             defect_class="hole_in_hull")

# Outer ring
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(3.0, 3.0, 0.0)   # 2
v3 = m.vertex(0.0, 3.0, 0.0)   # 3

# Inner hole boundary
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5
v6 = m.vertex(2.0, 2.0, 0.0)   # 6
v7 = m.vertex(1.0, 2.0, 0.0)   # 7

# Bottom strip
t0 = m.triangle(v0, v1, v5)   # 0
t1 = m.triangle(v0, v5, v4)   # 1

# Right strip
t2 = m.triangle(v1, v2, v6)   # 2
t3 = m.triangle(v1, v6, v5)   # 3

# Top strip
t4 = m.triangle(v2, v3, v7)   # 4
t5 = m.triangle(v2, v7, v6)   # 5

# Left strip
t6 = m.triangle(v3, v0, v4)   # 6
t7 = m.triangle(v3, v4, v7)   # 7

# The hole boundary: each inner edge is on exactly 1 triangle (boundary).
m.assert_hole_boundary([v4, v5, v6, v7])

# Outer boundary: bottom, right, top, left.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
