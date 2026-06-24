"""Me502 — remove_almost_degenerate_faces border_edge_needle: shortest edge on boundary; Euler::remove_face path (Branch 3).

CGAL PMP `PMP.remove_almost_degenerate_faces.face_range` Branch 3 (*Border edge needle*) @ line 1055:
  'if(is_border(get(halfedge_map, min_edge), tmesh))'
  — after a needle is detected and the collapse link-check is done, if the shortest
  edge lies on the mesh boundary (is_border), the algorithm calls Euler::remove_face
  to delete the entire triangle rather than attempting a collapse through a border edge.

Defect pattern: an open mesh (surface with boundary) containing a needle triangle
  whose shortest edge is a boundary edge — the edge is incident on only one triangle.
  The needle sits at the boundary, so min_edge is a border halfedge.

Geometry (z = 0):
  v0=(0.0,   0.0, 0.0)  — boundary needle left
  v1=(0.001, 0.0, 0.0)  — boundary needle right; edge v0-v1 is on the open boundary
  v2=(0.5,   0.866, 0.0) — needle apex; edges v0-v2 and v1-v2 shared with healthy tris

  Needle triangle t0=(v0,v1,v2): edge v0-v1 = 0.001 (boundary); v0-v2 ≈ v1-v2 ≈ 1.0.

  Healthy interior triangles fill in context around v2:
  v3=(1.0, 0.866, 0.0), v4=(-0.5, 0.866, 0.0)
  t1=(v1,v3,v2) — shares edge v1-v2 with needle (interior edge n=2)
  t2=(v2,v4,v0) — shares edge v0-v2 with needle (interior edge n=2)

  Boundary of the mesh: v0-v1 (needle short edge, n=1), v1-v3, v3-v2 (wait, v3-v2
  is in t1 as an interior edge? No — t1=(v1,v3,v2): edges v1-v3, v3-v2, v2-v1.
  Edge v2-v1 is shared with t0 → interior (n=2). Boundary: v1-v3, v3-v2 each n=1.)

  So the open boundary includes v0-v1 (the needle short edge) and other boundary segments.
  is_border(v0-v1) → true → Branch 3 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me502",
    title="remove_almost_degenerate_faces border_edge_needle: short edge v0-v1=0.001 is on open boundary; Euler::remove_face path (Branch 3)",
    defect_class="needle_triangle",
)

# Needle triangle on the mesh boundary.
v0 = m.vertex(0.0,   0.0,   0.0)   # 0 — boundary left
v1 = m.vertex(0.001, 0.0,   0.0)   # 1 — boundary right; edge v0-v1 = 0.001
v2 = m.vertex(0.5,   0.866, 0.0)   # 2 — needle apex

# Healthy flank vertices.
v3 = m.vertex(1.0,   0.866, 0.0)   # 3 — right flank
v4 = m.vertex(-0.5,  0.866, 0.0)   # 4 — left flank

# Needle (index 0): short edge v0-v1 on boundary (n=1 after all triangles added).
t_needle = m.triangle(v0, v1, v2)  # 0

# Healthy triangles sharing the long edges of the needle (making them interior).
m.triangle(v1, v3, v2)             # 1 — shares edge v1-v2 with needle
m.triangle(v2, v4, v0)             # 2 — shares edge v0-v2 with needle

# Short edge v0-v1 is a boundary edge: only t0 uses it → n=1.
m.assert_edge_shared(v0, v1, 1)

# The long edges of the needle are interior: shared by the needle and its flanks.
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)

# Short edge distance.
m.assert_vertex_pair_distance_lt(v0, v1, 0.002)

# Needle area: 0.5 * 0.001 * 0.866 ≈ 4.33e-4.
m.assert_triangle_area_lt(t_needle, 0.01)

# Extreme aspect ratio.
m.assert_triangle_aspect_ratio_gt(t_needle, 100.0)
