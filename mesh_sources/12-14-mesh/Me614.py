"""Me614 — is_cap_triangle_face handle_triplet slot 2: cap vertex at third position (r).

CGAL PMP `PMP.is_cap_triangle_face` Branch 5 (*handle_triplet slot 2*) @ line 485:
  'handle_triplet(r, p, q, 2)'
  — the function tries handle_triplet(p, q, r, 0) and handle_triplet(q, r, p, 1)
  in turn; neither fires because neither p nor q is the cap vertex. The third
  and final permutation handle_triplet(r, p, q, 2) then fires: the cap vertex
  is at position r — the vertex reached via next(next(h)) in the halfedge
  traversal — whose angle is near 180°.

Defect pattern: a near-180° cap triangle where the cap vertex is placed at
  the third vertex position (r). The triangle is stored as
  (v_base_left, v_base_right, v_cap). When traversed: p = v_base_left (not
  cap, slot 0 fails); q = v_base_right (not cap, slot 1 fails); r = v_cap
  triggers handle_triplet(r, p, q, 2).

Geometry:
  v_left = (0, 0, 0)    — base left  (p, not the cap)
  v_right= (10, 0, 0)   — base right (q, not the cap)
  v_cap  = (5, 0.05, 0) — cap vertex (r); angle ≈ 179.7°
  Triangle: (v_left, v_right, v_cap) → cap at slot 2 (r = v_cap)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me614",
    title="is_cap_triangle_face handle_triplet slot 2: cap vertex v2=(5,0.05,0) at third vertex r; angle≈179.7°; Branch 5 fires",
    defect_class="cap_triangle",
)

v_left  = m.vertex(0.0,  0.0,  0.0)  # 0 — base left  (p); NOT the cap
v_right = m.vertex(10.0, 0.0,  0.0)  # 1 — base right (q); NOT the cap
v_cap   = m.vertex(5.0,  0.05, 0.0)  # 2 — cap vertex (r); angle ≈ 179.7°

# Triangle with cap vertex at slot 2 (third vertex r).
# Slot 0 check handle_triplet(p,q,r,0) fails (p=v_left is not the cap);
# slot 1 check handle_triplet(q,r,p,1) fails (q=v_right is not the cap);
# slot 2 check handle_triplet(r,p,q,2) fires (r=v_cap has the 180° angle).
t0 = m.triangle(v_left, v_right, v_cap)  # 0 — cap at r → Branch 5

# High aspect ratio confirms the cap geometry (longest edge ≈ 10, height ≈ 0.05).
m.assert_triangle_aspect_ratio_gt(t0, 100.0)

# Area ≈ 0.5 * 10 * 0.05 = 0.25.
m.assert_triangle_area_lt(t0, 1.0)
