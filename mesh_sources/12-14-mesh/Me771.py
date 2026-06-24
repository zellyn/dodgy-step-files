"""Me771 — is_needle_triangle_face shortest_edge_e0: needle triangle with e0 (halfedge h from v0→v1) as shortest edge; res==0; returns h (Branch 2).

CGAL PMP `PMP.is_needle_triangle_face` Branch 2 (*aspect_ratio_extreme*) @ line 430:
  'if(res == 0) return h;'
  — the triangle's aspect ratio exceeds the needle threshold and the shortest
  edge is e0 (the initial halfedge h, directed v0→v1). Branch 2 returns h directly.

  The three edges in slot order are:
    e0 = h         → directed v0→v1  (length = |v1-v0|)
    e1 = next(h)   → directed v1→v2  (length = |v2-v1|)
    e2 = prev(h)   → directed v2→v0  (length = |v0-v2|)

Defect pattern: needle triangle where the two vertices v0 and v1 at the base are
  very close together while the apex v2 is far away. The base edge v0→v1 (e0) is
  dramatically shorter than the two long lateral edges v1→v2 and v2→v0. Aspect
  ratio ≫ threshold; is_needle_triangle_face returns h (Branch 2: res==0).

Geometry:
  v0=(0.0, 0.0, 0.0), v1=(0.01, 0.0, 0.0), v2=(50.0, 1.0, 0.0)
  e0 = |v1-v0| = 0.01  ← shortest
  e1 = |v2-v1| ≈ 50.0
  e2 = |v0-v2| ≈ 50.0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me771",
    title="is_needle_triangle_face shortest_edge_e0: needle triangle v0-v1 base 0.01; e0 shortest; res==0 returns h (Branch 2)",
    defect_class="degenerate_triangle",
)

# Needle: base edge (v0→v1) is very short; apex v2 is far away.
v0 = m.vertex( 0.0,  0.0, 0.0)  # 0 — base left
v1 = m.vertex( 0.01, 0.0, 0.0)  # 1 — base right (0.01 from v0)
v2 = m.vertex(50.0,  1.0, 0.0)  # 2 — apex far away

t0 = m.triangle(v0, v1, v2)  # 0

# All three edges are boundary edges (single open triangle).
m.assert_edge_shared(v0, v1, 1)  # e0 (h): length 0.01 — shortest
m.assert_edge_shared(v1, v2, 1)  # e1 (next h): length ≈ 50.0
m.assert_edge_shared(v0, v2, 1)  # e2 (prev h): length ≈ 50.0

# Extreme aspect ratio: longest edge ≈ 50.0, shortest altitude ≈ area*2/longest.
# area = 0.5 * base * h_perp = 0.5 * 0.01 * 1.0 = 0.005 (apex height above base ≈ 1.0)
# altitude_min ≈ 2*0.005/50 = 0.0002; aspect = 50/0.0002 = 250000 >> threshold.
m.assert_triangle_aspect_ratio_gt(t0, 1000.0)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
