"""Me269 — range_with_face_set_border_edge_cycle: connected component has boundary cycle (nested hole).

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 10 @ line 1778
(*border_edge_cycle*): when processing the connected component of the marked face region
using union-find to build the boundary, the algorithm finds that index != nb_cc — there
is a 'cycle of border edges'. This happens when the marked region contains a nested hole
(a hole within the marked region, forming a second boundary loop). The algorithm skips
removal in this case.

Geometric signature: a mesh with an ANNULAR region (ring-shaped region with a hole
inside). The marked region around the degenerate edge forms a topological annulus:
it has TWO boundary loops — the outer boundary and an inner hole boundary. This is
detected as a cycle of border edges (the inner hole forms a closed loop within the
marked region).

Configuration: a flat annular ring mesh (outer ring radius ≈ 2, inner hole radius ≈ 0.5).
The degenerate edge connects two nearly-coincident vertices in the inner hole boundary.
The marked region is the ring itself, which has chi=0 (annulus = cylinder unrolled).

Two boundary loops:
  Outer: v0,v1,v2,v3 (large square outer boundary)
  Inner: v4,v5,v6,v7 (small square inner hole boundary) — contains degenerate edge (v4,v5)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me269",
             title="range_with_face_set border_edge_cycle: annular mesh with inner hole; degenerate inner-boundary edge → cycle of border edges → skip",
             defect_class="degenerate_edge")

# Outer boundary ring (large square).
v0 = m.vertex(-2.0, -2.0, 0.0)
v1 = m.vertex( 2.0, -2.0, 0.0)
v2 = m.vertex( 2.0,  2.0, 0.0)
v3 = m.vertex(-2.0,  2.0, 0.0)

# Inner hole boundary (small square with degenerate edge v4≈v5).
v4 = m.vertex(-0.5, -0.5, 0.0)
v5 = m.vertex(-0.5 + 1e-10, -0.5, 0.0)   # nearly same as v4 → degenerate border edge
v6 = m.vertex( 0.5, -0.5, 0.0)
v7 = m.vertex( 0.0,  0.5, 0.0)

# 8 triangles forming the annular ring (outer quad - inner quad, no cap).
# Connect outer vertices to inner vertices to form the ring.
# Bottom strip: v0,v1 (outer bottom) connected to v4,v5 (inner bottom).
t0 = m.triangle(v0, v1, v5)   # 0: bottom-left band
t1 = m.triangle(v0, v5, v4)   # 1: bottom-right band — shares (v4,v5) border with inner hole

# Right strip: v1,v2 (outer right) connected to v5,v6 (inner right).
t2 = m.triangle(v1, v2, v6)   # 2
t3 = m.triangle(v1, v6, v5)   # 3

# Top strip: v2,v3 (outer top) connected to v6,v7 (inner top).
t4 = m.triangle(v2, v3, v7)   # 4
t5 = m.triangle(v2, v7, v6)   # 5

# Left strip: v3,v0 (outer left) connected to v7,v4 (inner left).
t6 = m.triangle(v3, v0, v4)   # 6
t7 = m.triangle(v3, v4, v7)   # 7

# The degenerate border edge (v4,v5) is on the inner hole boundary.
# It is shared by t0 (which has edge (v0,v5) and (v1,v5)...) wait:
# t1=(v0,v5,v4) → edges (0,5),(4,5),(0,4); so (v4,v5) in t1.
# t0=(v0,v1,v5) → edges (0,1),(1,5),(0,5); no (v4,v5).
# So (v4,v5) is in t1 only → n=1 (border edge on inner hole).
m.assert_edge_shared(v4, v5, 1)

# v4 and v5 are nearly coincident.
m.assert_vertex_pair_distance_lt(v4, v5, 1e-9)

# The annulus has two boundary loops: outer and inner.
# Euler: V=8, count edges:
# t0:(0,1),(1,5),(0,5); t1:(0,5),(4,5),(0,4); t2:(1,2),(2,6),(1,6); t3:(1,6),(1,5),(5,6);
# Hmm wait t3=(v1,v6,v5)=(1,6,5) → edges (1,6),(6,5),(1,5)
# t4:(2,3),(3,7),(2,7); t5:(2,7),(6,7),(2,6)... t5=(v2,v7,v6)=(2,7,6) → edges (2,7),(7,6),(2,6)
# t6:(3,0),(0,4),(3,4); t7:(3,4),(4,7),(3,7)
# Unique edges: (0,1),(1,5),(0,5),(4,5),(0,4),(1,2),(2,6),(1,6),(6,5),(2,3),(3,7),(2,7),(7,6),(3,0),(3,4),(4,7) = 16
# V=8, E=16, F=8, chi = 8-16+8 = 0 (annulus/cylinder = 2 boundary loops)
m.assert_euler_characteristic(v=8, e=16, f=8, chi=0)

# Inner hole boundary loop (v4→v5→v6→v7→v4): each edge is a border edge (n=1).
m.assert_hole_boundary([v4, v5, v6, v7])
