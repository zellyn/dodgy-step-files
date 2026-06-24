"""Me503 — remove_almost_degenerate_faces needle_flip_impossible: flip would create duplicate edge; deferred (Branch 4).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 4 (*Needle flip impossible*) @ line 1087:
  'if(halfedge(w, x, tmesh).second)'
  — when the needle's shortest edge passes the link-condition check but the flip
  target edge (connecting the "opposite" vertices of the two triangles sharing the
  short edge) already exists in the mesh, the flip would produce a duplicate edge.
  The algorithm defers the face for later processing.

Defect pattern: a two-triangle patch (t0+t1) sharing the needle's short edge v0-v1.
  Flipping v0-v1 would create edge v2-v3 (the "diagonal across" the quad formed by
  t0 and t1). A third triangle t2 uses v2-v3 as a boundary edge, so halfedge(v2,v3)
  already exists → the flip is impossible → Branch 4 fires.

Geometry (z = 0):
  v0=(0.0,   0.0,   0.0)  — needle short-edge left
  v1=(0.001, 0.0,   0.0)  — needle short-edge right (distance 0.001 from v0)
  v2=(0.5,   0.866, 0.0)  — needle apex; above the short edge
  v3=(0.5,  -0.866, 0.0)  — below; neighbor in t1 opposite v2
  v4=(1.0,   0.0,   0.0)  — extra vertex completing the blocking triangle

  t0=(v0,v1,v2)  — needle triangle; short edge v0-v1=0.001
  t1=(v1,v0,v3)  — below-neighbor; shares edge v0-v1 (interior, n=2)
  t2=(v2,v3,v4)  — blocking triangle; edge v2-v3 already exists (n=1 boundary)
                   → flipping v0-v1 into v2-v3 would duplicate v2-v3 → Branch 4
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me503",
    title="remove_almost_degenerate_faces needle_flip_impossible: edge v2-v3 pre-exists; flip of short edge v0-v1=0.001 blocked (Branch 4)",
    defect_class="needle_triangle",
)

v0 = m.vertex(0.0,   0.0,    0.0)   # 0
v1 = m.vertex(0.001, 0.0,    0.0)   # 1 — 0.001 from v0; needle short edge
v2 = m.vertex(0.5,   0.866,  0.0)   # 2 — needle apex
v3 = m.vertex(0.5,  -0.866,  0.0)   # 3 — below-neighbor
v4 = m.vertex(1.0,   0.0,    0.0)   # 4 — extra vertex

# Needle triangle (index 0).
t_needle = m.triangle(v0, v1, v2)  # 0

# Below-neighbor sharing the short edge (makes v0-v1 interior).
m.triangle(v1, v0, v3)             # 1

# Blocking triangle: introduces edge v2-v3 before the flip can create it.
m.triangle(v2, v3, v4)             # 2

# Short edge v0-v1 is interior (n=2).
m.assert_edge_shared(v0, v1, 2)

# Flip-target edge v2-v3 already exists as boundary edge in t2 (n=1).
# halfedge(v2,v3) is present → flip impossible → Branch 4.
m.assert_edge_shared(v2, v3, 1)

# Short edge distance: 0.001.
m.assert_vertex_pair_distance_lt(v0, v1, 0.002)

# Needle area: 0.5 * 0.001 * 0.866 ≈ 4.33e-4.
m.assert_triangle_area_lt(t_needle, 0.01)

# Extreme aspect ratio.
m.assert_triangle_aspect_ratio_gt(t_needle, 100.0)
