"""Me1080 — remove_degenerate_faces no_degenerate_faces: clean mesh triggers empty-set early return (Branch 1).

CGAL PMP `PMP.remove_degenerate_faces` Branch 1 (*no_degenerate_faces*) @ line 2049:
  'if (degenerate_face_set.empty()) return true;'
  — the initial scan of all faces finds no zero-area triangles; the degenerate_face_set
  is empty and the function returns true immediately without entering the repair loop.

Defect pattern: no defect — this is a clean, fully non-degenerate triangle strip.
  Three triangles form a flat fan in the XY plane. Every triangle has positive area;
  no two vertices in any triangle are collinear. When remove_degenerate_faces is called
  on this mesh, the initial degenerate-face scan produces an empty set → Branch 1 fires.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(3,1,0), v4=(4,0,0)
  t0=(v0,v1,v2): area = 1.0 (non-degenerate)
  t1=(v1,v3,v2): area = 0.5 (non-degenerate)
  t2=(v1,v4,v3): area = 1.0 (non-degenerate)
  All interior shared edges are manifold (n=2); boundary edges are n=1.
  degenerate_face_set.empty() → Branch 1 return true.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1080",
    title="remove_degenerate_faces no_degenerate_faces: three non-degenerate triangles; degenerate_face_set.empty() early return (Branch 1)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left base
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — center base
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — left apex
v3 = m.vertex(3.0, 1.0, 0.0)  # 3 — right apex
v4 = m.vertex(4.0, 0.0, 0.0)  # 4 — right base

# Three non-degenerate triangles sharing two interior edges.
t0 = m.triangle(v0, v1, v2)   # 0: left triangle, area = 1.0
t1 = m.triangle(v1, v3, v2)   # 1: center triangle, area = 1.0
t2 = m.triangle(v1, v4, v3)   # 2: right triangle, area = 1.0

# Interior shared edges (manifold, n=2).
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v3, 2)   # shared by t1 and t2

# All three triangles have positive area — none are degenerate.
# (area = 1.0, 1.0, 1.0; degenerate_face_set stays empty → Branch 1 fires)
# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
