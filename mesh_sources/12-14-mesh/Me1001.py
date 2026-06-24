"""Me1001 — remove_connected_components.by_face_range Logic_guard: !get(is_cst, v) vertex not constrained; remove (Branch 2).

CGAL PMP `PMP.remove_connected_components.by_face_range` Branch 2 (*Logic_guard*) @
line 741:
  'if(!get(is_cst, v)) { remove_face(fd, pmesh); ... }'
  — for each face in the face_range, the algorithm tests each incident vertex against a
  constraint property map (is_cst). When the vertex carries no constraint flag
  (!get(is_cst, v) is true), the face is unconditionally removed. Branch 2 fires for
  every unconstrained vertex encountered during iteration.

Defect pattern: two disconnected components. Component A (main mesh) is a 4-triangle
  diamond; Component B is a 2-triangle patch with no constraint-flagged vertices. When
  the face_range covers component B's faces and none of B's vertices are constrained,
  !get(is_cst, v) is true for every vertex in B, and Branch 2 fires to remove those
  faces. Component A's vertices are not in the face_range (or are constrained), so A
  survives.

Geometry:
  Component A (4-triangle diamond, hub v0=(0,0,0)):
    v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0), v4=(0,-1,0)
    t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
  Component B (2-triangle patch with unconstrained vertices):
    v5=(20,0,0), v6=(21,0,0), v7=(20,1,0), v8=(21,1,0)
    t4=(v5,v6,v7), t5=(v6,v8,v7)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1001",
    title="remove_connected_components.by_face_range Logic_guard: unconstrained vertices (!get(is_cst,v)) in face_range; 4-tri component A + 2-tri unconstrained component B removed (Branch 2)",
    defect_class="disconnected_components",
)

# Component A: 4-triangle diamond (closed loop around hub v0).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — east
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — north
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — west
v4 = m.vertex(0.0, -1.0, 0.0)  # 4 — south

t0 = m.triangle(v0, v1, v2)    # face 0
t1 = m.triangle(v0, v2, v3)    # face 1
t2 = m.triangle(v0, v3, v4)    # face 2
t3 = m.triangle(v0, v4, v1)    # face 3: closes the fan

# Component B: 2-triangle patch; all vertices unconstrained →
# !get(is_cst, v) true for every vertex in the face_range.
v5 = m.vertex(20.0, 0.0, 0.0)  # 5
v6 = m.vertex(21.0, 0.0, 0.0)  # 6
v7 = m.vertex(20.0, 1.0, 0.0)  # 7
v8 = m.vertex(21.0, 1.0, 0.0)  # 8

t4 = m.triangle(v5, v6, v7)    # face 4: unconstrained
t5 = m.triangle(v6, v8, v7)    # face 5: unconstrained

# Assertions: B is disconnected from A.
m.assert_triangle_not_reachable_from(t4, t0)
m.assert_triangle_not_reachable_from(t5, t0)

# Component A: hub edges (all n=2 — full closed fan).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t3
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# Component A: rim edges (n=1 each, open boundary).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v1, 1)

# Component B: shared diagonal (n=2); perimeter (n=1).
m.assert_edge_shared(v6, v7, 2)   # shared by t4 and t5
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v8, 1)
m.assert_edge_shared(v7, v8, 1)

# Euler: A: V=5, E=8, F=4, chi=5-8+4=1 (open disk).
# B: V=4, E=5, F=2, chi=4-5+2=1 (open disk).
# Total: V=9, E=13, F=6, chi=2.
m.assert_euler_characteristic(9, 13, 6, 2)
