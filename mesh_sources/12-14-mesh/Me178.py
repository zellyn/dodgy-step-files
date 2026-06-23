"""Me178 — orient_orientation_reversal: unoriented neighbor reversed for consistency.

Catalog claim: a chain of triangles where the DFS, having oriented t0 CCW,
reaches t1 with reversed winding and applies `inverse_orientation(index)`
(Branch 9, *orientation_reversal*) to flip t1 to match. Branch 9 fires when
the neighbor is NOT yet oriented (oriented[index]==false) and its winding is
opposite to what consistency requires — the algorithm reverses it in-place and
pushes it onto the DFS stack.

Geometric signature: a 3-triangle chain — t0 (seed, CCW), t1 (CW, adjacent
to t0, the reversal target), t2 (CCW, adjacent to t1). The orient algorithm
seeds on t0, walks to t1 (CW — inconsistent), reverses t1, then from t1
reaches t2 (already consistent). Branch 9 fires once: on the step from t0
to t1.

Defect carrier: t1=(v1, v0, v3) is CW (normal -Z). It shares edge (v0,v1)
with t0=(v0,v1,v2) which is CCW (+Z). The inconsistency triggers Branch 9.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me178",
             title="orient orientation_reversal: unoriented CW neighbor reversed by inverse_orientation to match CCW seed",
             defect_class="inconsistent_winding")

# Linear 3-triangle chain.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)   # CCW, +Z — seed
# t1: (v1-v0)×(v2-v0) = (1,0,0)×(0.5,1,0)=(0,0,1) → +Z (that's t0)
# t1 should be CW: use (v1,v0,v3) order.
# (v0-v1)×(v3-v1) = (-1,0,0)×(0.5,1,0) = (0,0,-1) → -Z ✓
t1 = m.triangle(v1, v0, v3)   # CW, -Z — the reversal target (Branch 9)
t2 = m.triangle(v1, v4, v3)   # CCW: (v4-v1)×(v3-v1)=(1,0,0)×(0.5,1,0)=(0,0,1) → +Z

# t0 and t1 share edge (v0,v1); antiparallel normals trigger Branch 9.
m.assert_edge_shared(v0, v1, 2)
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# t1 and t2 share edge (v1,v3).
m.assert_edge_shared(v1, v3, 2)
