"""Me772 — is_needle_triangle_face shortest_edge_e1: needle triangle with e1 (next(h), directed v1→v2) as shortest edge; res==1; returns next(h,tm) (Branch 3).

CGAL PMP `PMP.is_needle_triangle_face` Branch 3 (*aspect_ratio_extreme*) @ line 432:
  'else if(res == 1) return next(h,tm);'
  — the triangle's aspect ratio exceeds the needle threshold and the shortest
  edge is e1 (next of the initial halfedge h, directed v1→v2). Branch 3 returns
  next(h,tm).

  The three edges in slot order are:
    e0 = h         → directed v0→v1  (length = |v1-v0|)
    e1 = next(h)   → directed v1→v2  (length = |v2-v1|)
    e2 = prev(h)   → directed v2→v0  (length = |v0-v2|)

Defect pattern: needle triangle where v1 and v2 are very close together while
  v0 is far from both. The edge v1→v2 (e1, next(h)) is dramatically shorter than
  the two long edges. Aspect ratio ≫ threshold; is_needle_triangle_face returns
  next(h,tm) (Branch 3: res==1).

Geometry:
  v0=(0.0, 1.0, 0.0), v1=(50.0, 0.0, 0.0), v2=(50.01, 0.0, 0.0)
  e0 = |v1-v0| ≈ 50.01 (long)
  e1 = |v2-v1| = 0.01  ← shortest
  e2 = |v0-v2| ≈ 50.01 (long)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me772",
    title="is_needle_triangle_face shortest_edge_e1: needle triangle v1-v2 base 0.01; e1 shortest; res==1 returns next(h,tm) (Branch 3)",
    defect_class="degenerate_triangle",
)

# Needle: edge e1 = v1→v2 is very short; v0 is far from both v1 and v2.
v0 = m.vertex( 0.0,  1.0, 0.0)  # 0 — apex far away from base
v1 = m.vertex(50.0,  0.0, 0.0)  # 1 — base left
v2 = m.vertex(50.01, 0.0, 0.0)  # 2 — base right (0.01 from v1)

t0 = m.triangle(v0, v1, v2)  # 0

# All three edges are boundary edges (single open triangle).
m.assert_edge_shared(v0, v1, 1)  # e0 (h): length ≈ 50.01 — long
m.assert_edge_shared(v1, v2, 1)  # e1 (next h): length = 0.01 — shortest
m.assert_edge_shared(v0, v2, 1)  # e2 (prev h): length ≈ 50.01 — long

# Extreme aspect ratio: longest edge ≈ 50.01.
# area = 0.5 * base * height = 0.5 * 0.01 * 1.0 = 0.005
# altitude_min ≈ 2*0.005/50.01 ≈ 0.0002; aspect ≈ 50.01/0.0002 ≈ 250050 >> threshold.
m.assert_triangle_aspect_ratio_gt(t0, 1000.0)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
