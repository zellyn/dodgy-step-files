"""Me237 — topTriangle_steepest_edge_selection: edge with lower slope replaces current best.

MeshFix `Basic_TMesh.topTriangle` Branch 8 (*steepest_edge_selection*) @ line 1723:
  '(az = (hv->z - e->oppositeVertex(hv)->z) / e->length()) < Ms' — edge slope
  less than current minimum → update fe and Ms.

Branch 8 fires when a candidate edge (one that passed Branch 7) has a *smaller*
slope value (steeper descent relative to length) than the current best. The slope
formula is (hv.z - opposite.z) / edge_length; a steeper drop gives a smaller
value. With two edges incident on hv at different slopes, Branch 8 fires once for
the steeper edge.

Geometry: hv=v2 at z=4; two descending edges:
  v0=(0,0,0): slope = (4-0)/sqrt(1+16) ≈ 0.971   (shallower)
  v1=(1,0,1): slope = (4-1)/sqrt(0+9) = 1.0        (same as above approx)

Let me choose distinct slopes clearly:
  v0=(0,0,0) z=0: edge (v0,v2) length=sqrt(1+16)≈4.12, slope=(4-0)/4.12≈0.97
  v1=(0,0,2) z=2: edge (v1,v2) length=sqrt(1+4)≈2.24,  slope=(4-2)/2.24≈0.89 (steeper)

So Branch 8 first sets fe to v0-edge (slope 0.97), then fires again for v1-edge
(slope 0.89 < 0.97) → fe updated to v1-edge (the steeper one).

Geometry:
  v0=(0,0,0), v1=(0,0,2), v2=(1,0,4)   — apex at z=4
  t0=(v0,v1,v2) — single triangle; elist has all three edges.

hv=v2 (z=4). Candidate edges (incident on hv):
  - (v0,v2): slope=(4-0)/sqrt(1+16)=(4)/sqrt(17)≈0.970
  - (v1,v2): slope=(4-2)/sqrt(1+4)=(2)/sqrt(5)≈0.894   ← steeper (smaller value)
  - (v0,v1): NOT incident on hv → rejected by Branch 7.
Branch 8 fires twice; after both, fe=(v1,v2) as the steepest.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me237",
             title="topTriangle_steepest_edge_selection: steeper edge (v1,v2) wins Branch 8 slope comparison",
             defect_class="topTriangle_steepest_edge_selection")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — z=0
v1 = m.vertex(0.0, 0.0, 2.0)   # 1 — z=2
v2 = m.vertex(1.0, 0.0, 4.0)   # 2 — hv (z=4, highest)

t0 = m.triangle(v0, v1, v2)   # 0 — single triangle

# All edges are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)   # steepest: slope=(4-2)/sqrt(1+4)≈0.894
m.assert_edge_shared(v0, v2, 1)   # shallower: slope=(4-0)/sqrt(1+16)≈0.970

# v2 is the highest vertex (z=4 > z=2 > z=0).
# The hole boundary is the triangle perimeter.
m.assert_hole_boundary([v0, v1, v2])

# Confirm two edges incident on hv (v2) have different slopes.
# Edge (v1,v2) length ≈ sqrt(1+4) ≈ 2.236: slope (4-2)/2.236 ≈ 0.894
# Edge (v0,v2) length ≈ sqrt(1+16) ≈ 4.123: slope (4-0)/4.123 ≈ 0.970
m.assert_vertex_pair_distance_lt(v1, v2, 3.0)   # ~2.24
m.assert_vertex_pair_distance_lt(v0, v2, 5.0)   # ~4.12
