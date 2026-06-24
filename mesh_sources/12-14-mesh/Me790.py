"""Me790 — PMP.non_manifold_vertices nonmanifold_vertex_detection: bowtie pinch vertex with two disconnected umbrella sectors; multiple border halfedges trigger umbrella enumeration (Branch 1).

CGAL PMP `PMP.non_manifold_vertices` Branch 1 (*nonmanifold_vertex_detection*) @ line 260:
  'if(halfedge(v, tm) != boost::graph_traits<TriangleMesh>::null_halfedge())'
  — the algorithm iterates halfedges around the target vertex using
  halfedge_around_target(v, tm). A non-manifold (bowtie) vertex has more than one
  border halfedge in its star. When the enumerator encounters multiple border
  halfedges it emits a representative halfedge for each disconnected umbrella sector.
  Branch 1 is the detection gate: the vertex has incident halfedges (not an isolated
  vertex), so the star-traversal begins.

Input pattern: bowtie pinch vertex hub with two disconnected triangle fans.
  Fan A (triangles t0, t1) shares only hub with Fan B (triangles t2, t3).
  The link of hub has two connected components (upper fan CC and lower fan CC).
  Hub has four border halfedges — two per umbrella — forcing Branch 1 to iterate
  the star twice and emit two representative halfedges.

Defect: vertex hub=(0,0,0) is a non-manifold pinch vertex.
  Fan A — upper: t0=(hub, a0, a1), t1=(hub, a1, a2)
    a0=(1,1,0), a1=(0,1,0), a2=(-1,1,0)
  Fan B — lower: t2=(hub, b0, b1), t3=(hub, b1, b2)
    b0=(1,-1,0), b1=(0,-1,0), b2=(-1,-1,0)

Topology:
  Interior fan edges: (hub,a1) shared by t0+t1; (hub,b1) shared by t2+t3. n=2 each.
  Border hub edges: (hub,a0), (hub,a2), (hub,b0), (hub,b2). n=1 each.
  Fan A outer: (a0,a1) n=1, (a1,a2) n=1.
  Fan A base: (hub,a0) n=1, (hub,a2) n=1.
  Fan B outer: (b0,b1) n=1, (b1,b2) n=1.
  Fan B base: (hub,b0) n=1, (hub,b2) n=1.

Euler: V=7, E=10, F=4, chi = 7-10+4 = 1.
  Each fan (2 triangles) is an open disk with chi=1; gluing at hub gives chi=1+1-1=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me790",
    title="PMP.non_manifold_vertices nonmanifold_vertex_detection: bowtie hub vertex with 2 disconnected umbrella sectors; 4 border halfedges at hub trigger sector enumeration (Branch 1)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex( 0.0,  0.0, 0.0)  # 0 — bowtie pinch vertex

# Fan A — upper (y > 0)
a0  = m.vertex( 1.0,  1.0, 0.0)  # 1 — rightmost rim of upper fan
a1  = m.vertex( 0.0,  1.0, 0.0)  # 2 — middle rim (shared by t0 and t1)
a2  = m.vertex(-1.0,  1.0, 0.0)  # 3 — leftmost rim of upper fan

# Fan B — lower (y < 0)
b0  = m.vertex( 1.0, -1.0, 0.0)  # 4 — rightmost rim of lower fan
b1  = m.vertex( 0.0, -1.0, 0.0)  # 5 — middle rim (shared by t2 and t3)
b2  = m.vertex(-1.0, -1.0, 0.0)  # 6 — leftmost rim of lower fan

# Fan A: two triangles around hub sharing interior edge (hub, a1).
t0 = m.triangle(hub, a0, a1)  # 0: right half of upper fan
t1 = m.triangle(hub, a1, a2)  # 1: left half of upper fan

# Fan B: two triangles around hub sharing interior edge (hub, b1).
t2 = m.triangle(hub, b0, b1)  # 2: right half of lower fan
t3 = m.triangle(hub, b1, b2)  # 3: left half of lower fan

# Interior fan edges — each shared by exactly 2 triangles.
m.assert_edge_shared(hub, a1, 2)  # (0,2): shared by t0 and t1
m.assert_edge_shared(hub, b1, 2)  # (0,5): shared by t2 and t3

# Border hub edges — each belongs to exactly one triangle.
m.assert_edge_shared(hub, a0, 1)  # (0,1): boundary — t0 only
m.assert_edge_shared(hub, a2, 1)  # (0,3): boundary — t1 only
m.assert_edge_shared(hub, b0, 1)  # (0,4): boundary — t2 only
m.assert_edge_shared(hub, b2, 1)  # (0,6): boundary — t3 only

# Fan A outer rim edges — boundary.
m.assert_edge_shared(a0, a1, 1)   # (1,2): t0 outer
m.assert_edge_shared(a1, a2, 1)   # (2,3): t1 outer

# Fan B outer rim edges — boundary.
m.assert_edge_shared(b0, b1, 1)   # (4,5): t2 outer
m.assert_edge_shared(b1, b2, 1)   # (5,6): t3 outer

# hub's fan is disconnected: Fan A and Fan B share no edge.
m.assert_vertex_fan_disconnected(hub)

# Fan A and Fan B share only hub — no triangle from each sector shares a triangle.
m.assert_vertex_pair_no_shared_triangle(a0, b0)  # rim vertices in different sectors

# Euler: V=7, E=10, F=4, chi=7-10+4=1.
m.assert_euler_characteristic(7, 10, 4, 1)
