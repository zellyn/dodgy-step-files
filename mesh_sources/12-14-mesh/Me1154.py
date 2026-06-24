"""Me1154 — keep_connected_components by_face_range: face-range iteration path.

CGAL PMP `PMP.keep_connected_components` Branch 1 (*by_face_range*) @ line 304:
  'for(face_descriptor f : face_range) { ... }' — the face-range overload
  iterates a caller-supplied range of face descriptors to identify which
  connected components should be kept. This branch fires when the caller
  provides a face-range rather than a component-id list.

Defect pattern: a two-component mesh where the caller supplies a face range
  covering only component A. The function iterates the range, determines the
  CC of each supplied face, and marks those CCs as "kept". Faces in component B
  (not in the supplied range) are then removed.

Geometry:
  Component A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — single triangle t0.
  Component B: v3=(10,0,0), v4=(11,0,0), v5=(10.5,1,0) — single triangle t1.
  Both components are fully disconnected; face-range = {t0} keeps only A.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1154",
    title="keep_connected_components by_face_range: face-range iteration; two-component mesh with face-range selection of component A",
    defect_class="disconnected_components",
)

# Component A: single triangle at origin.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

t0 = m.triangle(v0, v1, v2)    # 0: component A — kept by face-range

# Component B: single triangle far from A.
v3 = m.vertex(10.0, 0.0, 0.0)  # 3
v4 = m.vertex(11.0, 0.0, 0.0)  # 4
v5 = m.vertex(10.5, 1.0, 0.0)  # 5

t1 = m.triangle(v3, v4, v5)    # 1: component B — excluded from face-range

# t0 and t1 are completely disconnected — no shared edges or vertices.
m.assert_triangle_not_reachable_from(t1, t0)

# Component A boundary edges (all n=1 on isolated triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Component B boundary edges.
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# Euler: V=6, E=6, F=2, chi=2 (two disconnected open triangles).
m.assert_euler_characteristic(6, 6, 2, 2)
