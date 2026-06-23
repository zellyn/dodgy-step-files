"""Me336 — pinch_cascade_v1: after merge, v1 still has non-manifold edges — recursive pinch(e_1, true).

MeshFix `Basic_TMesh.pinch` Branch 7 (*CASCADE_PINCH_NEEDED_V1*) @ line 956:
  'if (e_1 != NULL) pinch(e_1, true);'
  After the primary merge of e1 and e2, the algorithm checks whether v1
  (endpoint of e1) still has additional non-manifold edges cached in its
  info list. If e_1 != NULL (another singular edge hangs off v1), the
  algorithm recursively calls pinch(e_1, true) to resolve the cascading
  non-manifoldness at v1.

Defect pattern: a multi-level non-manifold fan at vertex v0 (v1 in the
  algorithm) where a first merge resolves one layer but leaves v0 still
  non-manifold due to a second overlapping fan at the same vertex.

Geometry: three triangle fans all sharing vertex v0, forming two levels of
  disconnected fans. The first pinch call merges fans A and B; the cascade
  fires because v0's edge-ring still has fan C remaining.

  v0=(0,0,0): triple-fan non-manifold vertex
  Fan A: t0=(v0,v1,v2), t1=(v0,v2,v3) — sector 0°-120°
  Fan B: t2=(v0,v4,v5) — sector 120°-240° (disconnected from A)
  Fan C: t3=(v0,v6,v7) — sector 240°-360° (disconnected from A and B)

  v0's fan is split into 3 disconnected sectors → cascade pinch fires.
"""
from step_corpus.mesh_builder import MeshFile

import math

m = MeshFile(catalog_id="Me336",
             title="pinch_cascade_v1: v1 still non-manifold after first merge — recursive pinch(e_1,true) fires",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — triple-fan pinch vertex

# Fan A (sector 0°–90°)
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.7,  0.7, 0.0)  # 2
v3 = m.vertex(0.0,  1.0, 0.0)  # 3

# Fan B (sector 120°–180°)
v4 = m.vertex(-0.5,  0.866, 0.0)  # 4
v5 = m.vertex(-1.0,  0.0,   0.0)  # 5

# Fan C (sector 240°–300°)
v6 = m.vertex(-0.5, -0.866, 0.0)  # 6
v7 = m.vertex( 0.5, -0.866, 0.0)  # 7

t0 = m.triangle(v0, v1, v2)   # 0 — Fan A tri 0
t1 = m.triangle(v0, v2, v3)   # 1 — Fan A tri 1
t2 = m.triangle(v0, v4, v5)   # 2 — Fan B
t3 = m.triangle(v0, v6, v7)   # 3 — Fan C

# Fan A internal edge (v0,v2) is shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)

# v0's fan is disconnected across 3 sectors → cascade pinch needed.
m.assert_vertex_fan_disconnected(v0)

# Fan B and Fan C are disconnected from Fan A.
m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t3, t0)
m.assert_triangle_not_reachable_from(t3, t2)

# Outer boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v0, v5, 1)
m.assert_edge_shared(v0, v6, 1)
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v0, v7, 1)
