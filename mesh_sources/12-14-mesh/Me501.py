"""Me501 — remove_almost_degenerate_faces needle_non_collapsible: short edge violates link condition; flip path (Branch 2).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 2 (*Needle non-collapsible*) @ line 1031:
  'if(!CGAL::Euler::does_satisfy_link_condition(...))'
  — after a needle is detected, the shortest edge is tested for link-condition
  satisfaction before attempting collapse. If link(v0) ∩ link(v1) ⊋ link(edge(v0,v1)),
  the edge cannot be collapsed without creating a non-manifold mesh; the algorithm
  switches to an edge flip instead.

Defect pattern: a needle triangle with short edge v0-v1 (length 0.001). Two triangles
  share the edge (making it interior) so link(edge) = {v2, v3}. Two additional flanking
  triangles give v4 as an extra common neighbor of both v0 and v1, making
  link(v0) ∩ link(v1) = {v2, v3, v4} ⊋ {v2, v3} → link condition fails → flip path.

Geometry (z = 0):
  v0=(0.0, 0.0, 0.0), v1=(0.001, 0.0, 0.0)  — short edge (length 0.001)
  v2=(0.5, 0.866, 0.0)  — needle apex
  v3=(0.5, -0.866, 0.0) — below-neighbor; lk(edge v0-v1) = {v2, v3}
  v4=(1.0, 0.0, 0.0)    — extra common neighbor; in lk(v0)∩lk(v1) but not lk(edge)

  t0=(v0,v1,v2) — needle (short edge v0-v1)
  t1=(v1,v0,v3) — shares short edge below; makes it interior
  t2=(v0,v4,v2) — gives v0-v4 and v2-v4 edges; v4 ∈ lk(v0)
  t3=(v1,v2,v4) — gives v1-v4 and v2-v4 edges; v4 ∈ lk(v1)
  → link condition violated → Branch 2 fires
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me501",
    title="remove_almost_degenerate_faces needle_non_collapsible: extra shared neighbor v4 violates link condition for short edge v0-v1=0.001; flip path (Branch 2)",
    defect_class="needle_triangle",
)

v0 = m.vertex(0.0,   0.0,    0.0)   # 0 — needle short-edge left
v1 = m.vertex(0.001, 0.0,    0.0)   # 1 — needle short-edge right; dist=0.001
v2 = m.vertex(0.5,   0.866,  0.0)   # 2 — needle apex
v3 = m.vertex(0.5,  -0.866,  0.0)   # 3 — below; lk(edge)={v2,v3}
v4 = m.vertex(1.0,   0.0,    0.0)   # 4 — extra common neighbor; violates link

# Needle triangle (index 0).
t_needle = m.triangle(v0, v1, v2)  # 0

# Interior neighbor below — short edge v0-v1 now shared by 2 triangles.
m.triangle(v1, v0, v3)             # 1

# Flanking triangles introducing v4 as extra shared neighbor of both v0 and v1.
m.triangle(v0, v4, v2)             # 2 — v4 ∈ lk(v0)
m.triangle(v1, v2, v4)             # 3 — v4 ∈ lk(v1); link condition fails

# Short edge v0-v1 is interior (shared by t0, t1).
m.assert_edge_shared(v0, v1, 2)

# Short edge distance.
m.assert_vertex_pair_distance_lt(v0, v1, 0.002)

# Needle area: 0.5 * 0.001 * 0.866 ≈ 4.33e-4.
m.assert_triangle_area_lt(t_needle, 0.01)

# Extreme aspect ratio.
m.assert_triangle_aspect_ratio_gt(t_needle, 100.0)
