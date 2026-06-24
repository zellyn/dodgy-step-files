"""Me850 — does_bound_a_volume connectivity_broken: open mesh has boundary edge; is_closed fails; returns false (Branch 1).

CGAL PMP `PMP.does_bound_a_volume` Branch 1 (*connectivity_broken*) @ line 918:
  'if(!PMP::is_closed(tmesh)) return false;'
  — the predicate immediately returns false when the mesh has at least one
  boundary halfedge (an edge shared by only one triangle). Any open mesh
  with a boundary cycle triggers this branch before orientation or
  self-intersection are even evaluated.

Defect pattern: tetrahedron base face removed, leaving a triangular hole.
  Three triangular side faces form a manifold open mesh. The three base
  edges each appear in exactly one triangle (n=1), forming a single
  boundary cycle. is_closed returns false → Branch 1 fires → does_bound_a_volume
  returns false immediately.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,0.5,1)
  Side faces: (v0,v1,v3), (v1,v2,v3), (v0,v3,v2)  [three lateral faces]
  Base edges (v0,v1), (v1,v2), (v0,v2) each appear once → boundary cycle.
  Interior (shared) edges: (v0,v3), (v1,v3), (v2,v3) each appear twice.
  Euler: V=4, E=6, F=3, chi=1 (open disk / cone topology).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me850",
    title="does_bound_a_volume connectivity_broken: tetrahedron with base removed; boundary cycle present; is_closed returns false (Branch 1)",
    defect_class="hole_in_hull",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — base corner
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — base corner
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — base corner
v3 = m.vertex(0.5, 0.5, 1.0)  # 3 — apex

# Three lateral faces only; base face (v0,v1,v2) is absent → open mesh.
t0 = m.triangle(v0, v1, v3)   # 0: front-left lateral
t1 = m.triangle(v1, v2, v3)   # 1: front-right lateral
t2 = m.triangle(v0, v3, v2)   # 2: back lateral

# Lateral (shared) edges — each shared by two triangles.
m.assert_edge_shared(v0, v3, 2)  # t0 and t2
m.assert_edge_shared(v1, v3, 2)  # t0 and t1
m.assert_edge_shared(v2, v3, 2)  # t1 and t2

# Boundary edges (base) — each shared by exactly one triangle.
m.assert_edge_shared(v0, v1, 1)  # t0 base; no base face → boundary
m.assert_edge_shared(v1, v2, 1)  # t1 base; boundary
m.assert_edge_shared(v0, v2, 1)  # t2 base; boundary

# Three base edges form a single triangular boundary cycle.
m.assert_hole_boundary([v0, v1, v2])

# Euler: V=4, E=6, F=3, chi=1 (cone / open disk).
m.assert_euler_characteristic(4, 6, 3, 1)
