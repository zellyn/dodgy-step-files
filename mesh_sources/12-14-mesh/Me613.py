"""Me613 — is_cap_triangle_face handle_triplet slot 1: cap vertex at second position (q).

CGAL PMP `PMP.is_cap_triangle_face` Branch 4 (*handle_triplet slot 1*) @ line 483:
  'handle_triplet(q, r, p, 1)'
  — the function first checks handle_triplet(p, q, r, 0) which does NOT fire
  (the vertex at slot 0, the halfedge source p, is not the cap vertex). The
  function then tries the second permutation: handle_triplet(q, r, p, 1).
  This fires when the cap vertex is at position q — i.e. the target of the
  input halfedge — whose angle is near 180°.

Defect pattern: a near-180° cap triangle where the cap vertex is placed at
  the second vertex position (q, the halfedge target). The triangle is stored
  as (v_base_left, v_cap, v_base_right). When traversed: p = v_base_left (not
  the cap), so slot 0 does not fire; q = v_cap triggers handle_triplet(q,r,p,1).

Geometry:
  v_left = (0, 0, 0)    — base left  (p, not the cap)
  v_cap  = (5, 0.05, 0) — cap vertex (q); angle ≈ 179.7°
  v_right= (10, 0, 0)   — base right (r)
  Triangle: (v_left, v_cap, v_right) → cap at slot 1 (q = v_cap)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me613",
    title="is_cap_triangle_face handle_triplet slot 1: cap vertex v1=(5,0.05,0) at halfedge target q; angle≈179.7°; Branch 4 fires",
    defect_class="cap_triangle",
)

v_left  = m.vertex(0.0,  0.0,  0.0)  # 0 — base left  (p); NOT the cap
v_cap   = m.vertex(5.0,  0.05, 0.0)  # 1 — cap vertex (q); angle ≈ 179.7°
v_right = m.vertex(10.0, 0.0,  0.0)  # 2 — base right (r)

# Triangle with cap vertex at slot 1 (halfedge target q).
# Slot 0 check handle_triplet(p,q,r,0) fails (p=v_left is not the cap);
# slot 1 check handle_triplet(q,r,p,1) fires (q=v_cap has the 180° angle).
t0 = m.triangle(v_left, v_cap, v_right)  # 0 — cap at q → Branch 4

# High aspect ratio confirms the cap geometry (longest edge ≈ 10, height ≈ 0.05).
m.assert_triangle_aspect_ratio_gt(t0, 100.0)

# Area ≈ 0.5 * 10 * 0.05 = 0.25.
m.assert_triangle_area_lt(t0, 1.0)
