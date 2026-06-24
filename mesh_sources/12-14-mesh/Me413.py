"""Me413 — refineSelectedHolePatches_edge_length_averaging: non-interior edges summed to compute sigma.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 4 (*EDGE_LENGTH_AVERAGING*) @ line 632:
  'sigma += e->length(); noe++' — for each edge in all_edges that is NOT in
  interior_edges, its length is added to sigma. After the loop, sigma is divided
  by noe to get the average boundary-edge length, which becomes the density
  threshold for vertex splitting.

Defect pattern: a 4-triangle hole-fill patch where the boundary (non-interior)
  edges have a well-defined average length. The 4 triangles share interior edges
  (excluded from sigma); the boundary edges contribute their lengths to sigma.

  This fixture has equal-length boundary edges of length 1.0, so sigma = 1.0 and
  noe = 4 boundary edges. The average (sigma/noe) = 1.0 is the refinement threshold.

Geometry: 4 right-isoceles triangles arranged as a 2x2 grid.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)
  v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)
  t0=(v0,v1,v4), t1=(v0,v4,v3), t2=(v1,v2,v4), t3=(v2,v5,v4)

  Interior edges: (v0,v4) between t0 and t1; (v1,v4) between t0 and t2; (v2,v4) between t2 and t3.
  Boundary edges (contribute to sigma): (v0,v1),(v1,v2),(v0,v3),(v3,v4),(v4,v3)…

  Wait — recalculate:
  t0=(v0,v1,v4): edges (v0,v1),(v1,v4),(v4,v0)
  t1=(v0,v4,v3): edges (v0,v4),(v4,v3),(v3,v0)
  t2=(v1,v2,v4): edges (v1,v2),(v2,v4),(v4,v1)
  t3=(v2,v5,v4): edges (v2,v5),(v5,v4),(v4,v2)

  Interior (n=2): (v0,v4) t0+t1; (v1,v4) t0+t2; (v2,v4) t2+t3
  Boundary (n=1): (v0,v1),(v0,v3),(v3,v4),(v1,v2),(v2,v5),(v4,v5) — 6 edges

  Edge lengths (all horizontal/vertical, length=1.0):
    (v0,v1)=1, (v0,v3)=1, (v3,v4)=1, (v1,v2)=1, (v2,v5)=1, (v4,v5)=1
  sigma = 6 * 1.0 = 6.0; noe = 6; average = 1.0

Interior edges (diagonals, excluded from sigma):
  (v0,v4) = sqrt(2) ≈ 1.414; (v1,v4) = 1.0; (v2,v4) = 1.0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me413",
             title="refineSelectedHolePatches_edge_length_averaging: boundary edges summed for sigma average (Branch 4)",
             defect_class="hole_in_hull")

# 2x2 grid of 6 vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# 4-triangle patch.
t0 = m.triangle(v0, v1, v4)   # 0
t1 = m.triangle(v0, v4, v3)   # 1 — (v0,v4) interior with t0
t2 = m.triangle(v1, v2, v4)   # 2 — (v1,v4) interior with t0
t3 = m.triangle(v2, v5, v4)   # 3 — (v2,v4) interior with t2

# Interior edges — excluded from sigma averaging (Branch 3 detected these).
m.assert_edge_shared(v0, v4, 2)   # t0 ↔ t1: diagonal, excluded from sigma
m.assert_edge_shared(v1, v4, 2)   # t0 ↔ t2: length 1.0, excluded from sigma
m.assert_edge_shared(v2, v4, 2)   # t2 ↔ t3: length 1.0, excluded from sigma

# Boundary edges — NON-interior; each contributes to sigma (Branch 4).
m.assert_edge_shared(v0, v1, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v0, v3, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v3, v4, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v1, v2, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v2, v5, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v4, v5, 1)   # length 1.0 → sigma += 1.0
# sigma = 6.0, noe = 6, average boundary edge length = 1.0.

# Euler: V=6, E=9 (3 interior + 6 boundary), F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
