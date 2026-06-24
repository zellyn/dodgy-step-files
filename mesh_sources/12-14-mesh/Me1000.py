"""Me1000 — remove_connected_components.by_face_range Iteration_construct: loop over face_range (Branch 1).

CGAL PMP `PMP.remove_connected_components.by_face_range` Branch 1 (*Iteration_construct*) @
line 740:
  'for(face_descriptor fd : face_range) { ... }'
  — the function receives a sub-range of face descriptors and iterates over them all,
  applying the connected-component removal logic to each face in the given range.
  Branch 1 fires whenever the face_range is non-empty and the loop body is entered
  at least once.

Defect pattern: two disconnected triangular components. Component A is a 3-triangle fan
  (faces 0-2) around a central vertex. Component B is a single isolated triangle (face 3)
  far away. The face_range designates all four faces; the loop iterates all of them, entering
  Branch 1 repeatedly. The isolated component (B) is the target for removal: it is
  unreachable from component A.

Geometry:
  Component A (3 triangles sharing vertex v0):
    v0=(0,0,0) hub; v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0) rim
    t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4)
  Component B (isolated triangle):
    v5=(10,0,0), v6=(11,0,0), v7=(10,1,0)
    t3=(v5,v6,v7)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1000",
    title="remove_connected_components.by_face_range Iteration_construct: loop enters for each face in range; 3-triangle component A + isolated triangle B (Branch 1)",
    defect_class="disconnected_components",
)

# Component A: 3-triangle fan around v0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — rim east
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — rim north
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — rim west
v4 = m.vertex(0.0, -1.0, 0.0)  # 4 — rim south

t0 = m.triangle(v0, v1, v2)    # face 0: NE sector
t1 = m.triangle(v0, v2, v3)    # face 1: NW sector
t2 = m.triangle(v0, v3, v4)    # face 2: SW sector

# Component B: isolated triangle far from A.
v5 = m.vertex(10.0, 0.0, 0.0)  # 5
v6 = m.vertex(11.0, 0.0, 0.0)  # 6
v7 = m.vertex(10.0, 1.0, 0.0)  # 7

t3 = m.triangle(v5, v6, v7)    # face 3: isolated component B

# Assertions: B is disconnected from A (iteration must visit face 3 in the range).
m.assert_triangle_not_reachable_from(t3, t0)

# Interior edges of component A (shared by 2 triangles each).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Boundary edges of A (n=1) and all edges of B (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 1)

# Euler: V=8, E=9+3=12 wait: A has 5v+7e+3f; B has 3v+3e+1f; total V=8, E=10, F=4, chi=2.
# Component A: V=5, E=7 (hub spokes: v0-v1,v0-v2,v0-v3,v0-v4 + rim: v1v2,v2v3,v3v4), F=3
# Component A chi: 5-7+3=1 (open disk). Component B: 3-3+1=1. Total chi=2.
m.assert_euler_characteristic(8, 10, 4, 2)
