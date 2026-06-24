"""Me773 — is_needle_triangle_face shortest_edge_e2: needle triangle with e2 (prev(h), directed v2→v0) as shortest edge; res==2; returns prev(h,tm) (Branch 4).

CGAL PMP `PMP.is_needle_triangle_face` Branch 4 (*aspect_ratio_extreme*) @ line 434:
  'else return prev(h,tm);'  // res == 2
  — the triangle's aspect ratio exceeds the needle threshold and the shortest
  edge is e2 (prev of the initial halfedge h, directed v2→v0). Branch 4 (the
  implicit else) returns prev(h,tm).

  The three edges in slot order are:
    e0 = h         → directed v0→v1  (length = |v1-v0|)
    e1 = next(h)   → directed v1→v2  (length = |v2-v1|)
    e2 = prev(h)   → directed v2→v0  (length = |v0-v2|)

Defect pattern: needle triangle where v2 and v0 are very close together while
  v1 is far from both. The edge v2→v0 (e2, prev(h)) is dramatically shorter than
  the two long edges. Aspect ratio ≫ threshold; is_needle_triangle_face returns
  prev(h,tm) (Branch 4: res==2).

Geometry:
  v0=(0.0,  0.0, 0.0), v1=(50.0, 1.0, 0.0), v2=(0.01, 0.0, 0.0)
  e0 = |v1-v0| ≈ 50.01  (long)
  e1 = |v2-v1| ≈ 50.0   (long)
  e2 = |v0-v2| = 0.01   ← shortest
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me773",
    title="is_needle_triangle_face shortest_edge_e2: needle triangle v2-v0 base 0.01; e2 shortest; res==2 returns prev(h,tm) (Branch 4)",
    defect_class="degenerate_triangle",
)

# Needle: edge e2 = v2→v0 is very short; v1 is far from both v0 and v2.
v0 = m.vertex( 0.0,  0.0, 0.0)  # 0 — base left
v1 = m.vertex(50.0,  1.0, 0.0)  # 1 — apex far away
v2 = m.vertex( 0.01, 0.0, 0.0)  # 2 — base right (0.01 from v0)

t0 = m.triangle(v0, v1, v2)  # 0

# All three edges are boundary edges (single open triangle).
m.assert_edge_shared(v0, v1, 1)  # e0 (h): length ≈ 50.01 — long
m.assert_edge_shared(v1, v2, 1)  # e1 (next h): length ≈ 50.0 — long
m.assert_edge_shared(v0, v2, 1)  # e2 (prev h): length = 0.01 — shortest

# Extreme aspect ratio: longest edge ≈ 50.01.
# area = 0.5 * |cross(v1-v0, v2-v0)|
# v1-v0 = (50,1,0), v2-v0 = (0.01,0,0)
# cross = (0, 0, 50*0 - 1*0.01) = (0, 0, -0.01) → |cross|=0.01
# area = 0.5 * 0.01 = 0.005
# altitude_min ≈ 2*0.005/50.01 ≈ 0.0002; aspect ≈ 50.01/0.0002 ≈ 250050 >> threshold.
m.assert_triangle_aspect_ratio_gt(t0, 1000.0)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
