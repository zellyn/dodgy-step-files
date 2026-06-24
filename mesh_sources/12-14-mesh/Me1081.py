"""Me1081 — remove_degenerate_faces all_faces_degenerate: two collinear triangles exhaust the face set (Branch 2).

CGAL PMP `PMP.remove_degenerate_faces` Branch 2 (*all_faces_degenerate*) @ line 2052:
  'if (degenerate_face_set.size() == faces_size) { ... clear all elements ... return true; }'
  — every face in the mesh is in the degenerate set; the early-exit path clears
  all vertices, edges and faces and returns true without entering the main repair loop.

Defect pattern: two collinear triangles sharing a vertex, both with zero area.
  The degenerate_face_set has 2 entries and faces_size == 2 → Branch 2 fires.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear along x-axis
  v3=(0,1,0), v4=(1,1,0), v5=(2,1,0) — collinear along y=1 line
  t0=(v0,v1,v2): three points on y=0 line → area = 0
  t1=(v3,v4,v5): three points on y=1 line → area = 0
  Both triangles degenerate; degenerate_face_set.size()==2 == faces_size==2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1081",
    title="remove_degenerate_faces all_faces_degenerate: two collinear zero-area triangles; degenerate_face_set.size()==faces_size clear-all path (Branch 2)",
    defect_class="degenerate_triangle",
)

# Triangle 0: three collinear points along the x-axis at y=0.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
t0 = m.triangle(v0, v1, v2)   # 0: collinear, area = 0

# Triangle 1: three collinear points along y=1 line.
v3 = m.vertex(0.0, 1.0, 0.0)  # 3
v4 = m.vertex(1.0, 1.0, 0.0)  # 4
v5 = m.vertex(2.0, 1.0, 0.0)  # 5
t1 = m.triangle(v3, v4, v5)   # 1: collinear, area = 0

# Both triangles are zero-area — entire mesh is degenerate.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)

# All edges are boundary edges (each triangle is isolated, no shared edges).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
