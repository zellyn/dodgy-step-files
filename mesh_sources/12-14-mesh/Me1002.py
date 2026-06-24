"""Me1002 — remove_connected_components.by_face_range Alternative_path: else fallback for constrained vertex (Branch 3).

CGAL PMP `PMP.remove_connected_components.by_face_range` Branch 3 (*Alternative_path*) @
line 743:
  '} else { ... }  // constraint-respecting fallback'
  — when a face in the face_range has at least one constrained vertex (get(is_cst, v)
  is true for some v), the removal logic takes the else path instead of immediately
  removing the face. This constraint-respecting fallback fires whenever the face's
  incident vertices include a constrained one, deferring or skipping removal to preserve
  topological invariants around constraint boundaries.

Defect pattern: two disconnected components. Component A is a 3-triangle fan (main mesh).
  Component B is a 3-triangle strip where the boundary vertex shared between the two
  end triangles is marked as constrained. When the face_range includes component B's
  faces, the algorithm checks is_cst on each incident vertex; the constrained vertex
  triggers the else fallback (Branch 3) rather than the unconditional remove of Branch 2.

Geometry:
  Component A (3-triangle fan around hub v0):
    v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0)
    t0=(v0,v1,v2), t1=(v0,v2,v3)
  Component B (3-triangle strip with constrained boundary vertex v7):
    v4=(10,0,0), v5=(11,0,0), v6=(11,1,0), v7=(10,1,0) [constrained], v8=(10,2,0)
    t2=(v4,v5,v7), t3=(v5,v6,v7), t4=(v4,v7,v8)
  v7 is the constrained vertex: the face_range contains t2-t4; when processing t2 or
  t4 (which include v7), get(is_cst, v7)==true fires the else path (Branch 3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1002",
    title="remove_connected_components.by_face_range Alternative_path: constrained vertex v7 in face_range triggers else fallback; 2-tri component A + 3-tri component B with constraint (Branch 3)",
    defect_class="disconnected_components",
)

# Component A: 2-triangle fan (small main component).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — east
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — north
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — west

t0 = m.triangle(v0, v1, v2)    # face 0: NE sector
t1 = m.triangle(v0, v2, v3)    # face 1: NW sector

# Component B: 3-triangle strip with one constrained vertex (v7).
# v7 is "constrained" in the sense that get(is_cst, v7) == true, so faces
# incident on v7 take the else fallback (Branch 3) rather than unconditional remove.
v4 = m.vertex(10.0, 0.0, 0.0)  # 4 — bottom-left of B
v5 = m.vertex(11.0, 0.0, 0.0)  # 5 — bottom-right of B
v6 = m.vertex(11.0, 1.0, 0.0)  # 6 — mid-right of B
v7 = m.vertex(10.0, 1.0, 0.0)  # 7 — constrained boundary vertex
v8 = m.vertex(10.0, 2.0, 0.0)  # 8 — top-left of B

t2 = m.triangle(v4, v5, v7)    # face 2: bottom strip triangle (includes v7 — constrained)
t3 = m.triangle(v5, v6, v7)    # face 3: right strip triangle (includes v7 — constrained)
t4 = m.triangle(v4, v7, v8)    # face 4: top strip triangle (includes v7 — constrained)

# Assertions: B is disconnected from A.
m.assert_triangle_not_reachable_from(t2, t0)
m.assert_triangle_not_reachable_from(t4, t0)

# Component A interior edge (shared by t0 and t1).
m.assert_edge_shared(v0, v2, 2)

# Component A boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Component B: edges shared by 2 triangles (all incident on v7).
m.assert_edge_shared(v4, v7, 2)   # shared by t2 and t4
m.assert_edge_shared(v5, v7, 2)   # shared by t2 and t3

# Component B: boundary edges (n=1).
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v4, v8, 1)

# Euler:
# Component A: V=4, E=5, F=2, chi=1 (open disk).
# Component B: V=5, E=7, F=3, chi=1 (open disk).
# Total: V=9, E=12, F=5, chi=2.
m.assert_euler_characteristic(9, 12, 5, 2)
