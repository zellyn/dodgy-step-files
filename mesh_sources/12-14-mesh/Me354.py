"""Me354 — CreateTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edges to triangle.

MeshFix `Basic_TMesh.CreateTriangle` Branch 5 (*triangle_adjacency_assignment*) @ line 376:
  `*at1 = *at2 = *at3 = tt;`
  After creating the triangle object tt, all three edge-slot pointers (at1, at2, at3)
  are written to point back to tt. This bi-directional link is the adjacency
  assignment step: each bounding edge now knows about tt.

Defect carrier: two triangles that share an edge, demonstrating that the shared
edge's adjacency slots were both written during their respective CreateTriangle
calls. One triangle owns one slot of the shared edge; the other owns the second
slot. The resulting edge incidence n=2 confirms both adjacency assignments fired.

Geometry (right-angle pair):
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0)
  t0=(v0,v1,v2) — first triangle; *at1 wrote e_diag->t1=t0
  t1=(v0,v2,v3) — second triangle; *at1 wrote e_diag->t2=t1
  Diagonal edge (v0,v2): shared by both → n=2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me354",
    title="CreateTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edge slots to tt (Branch 5)",
    defect_class="create_triangle_adjacency_assignment",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0 — first CreateTriangle call; wrote e_diag->t1=t0
t1 = m.triangle(v0, v2, v3)   # 1 — second CreateTriangle call; wrote e_diag->t2=t1

# The shared diagonal edge (v0,v2): both adjacency slots filled → n=2.
m.assert_edge_shared(v0, v2, 2)   # Branch 5: *at1=tt wrote both slots

# Boundary edges: each owned by exactly one triangle's adjacency assignment.
m.assert_edge_shared(v0, v1, 1)   # t0 only
m.assert_edge_shared(v1, v2, 1)   # t0 only
m.assert_edge_shared(v2, v3, 1)   # t1 only
m.assert_edge_shared(v0, v3, 1)   # t1 only

# Euler characteristic: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(v=4, e=5, f=2, chi=1)
