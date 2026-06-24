"""Me612 — is_cap_triangle_face handle_triplet slot 0: cap vertex at halfedge source (p).

CGAL PMP `PMP.is_cap_triangle_face` Branch 3 (*handle_triplet slot 0*) @ line 481:
  'handle_triplet(p, q, r, 0)'
  — after the non-negative scalar product confirms a cap exists, the function
  tries each vertex triplet permutation in order. Slot 0 calls handle_triplet
  with (p, q, r) where p = source(h, mesh). This fires when the cap vertex
  is the source of the halfedge passed to is_cap_triangle_face: the angle at
  p is near 180°, meaning p lies very close to the segment between q and r.

Defect pattern: a near-180° cap triangle where the cap vertex is placed at
  the first vertex position (the halfedge source, slot 0). The triangle is
  stored as (v_cap, v_base_left, v_base_right). When traversed from the
  halfedge starting at v_cap, p = v_cap (near 180°) is identified first and
  handle_triplet(p, q, r, 0) fires immediately.

Geometry:
  v_cap  = (5, 0.05, 0) — cap vertex; angle ≈ 179.7° (lies near midpoint of base)
  v_left = (0, 0, 0)    — base left
  v_right= (10, 0, 0)   — base right
  Triangle: (v_cap, v_left, v_right) → cap at slot 0 (p = v_cap)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me612",
    title="is_cap_triangle_face handle_triplet slot 0: cap vertex v0=(5,0.05,0) at halfedge source; angle≈179.7° at p; Branch 3 fires",
    defect_class="cap_triangle",
)

v_cap   = m.vertex(5.0,  0.05, 0.0)  # 0 — cap vertex (p); angle ≈ 179.7°
v_left  = m.vertex(0.0,  0.0,  0.0)  # 1 — base left  (q)
v_right = m.vertex(10.0, 0.0,  0.0)  # 2 — base right (r)

# Triangle with cap vertex at slot 0 (halfedge source p).
t0 = m.triangle(v_cap, v_left, v_right)  # 0 — cap at p → handle_triplet(p,q,r,0)

# The cap vertex (v0) nearly lies on the base edge (v1→v2).
# vertex_on_edge checks collinearity; v0 has y=0.05 so it is NOT collinear.
# Assert extremely high aspect ratio instead (longest_edge/shortest_altitude).
# Longest edge ≈ 10 (base v1–v2); height ≈ 0.05 → aspect ratio ≈ 200.
m.assert_triangle_aspect_ratio_gt(t0, 100.0)

# Area ≈ 0.5 * 10 * 0.05 = 0.25 (non-zero cap, very thin).
m.assert_triangle_area_lt(t0, 1.0)
