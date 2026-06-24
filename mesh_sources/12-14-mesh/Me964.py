"""Me964 — CreateUnorientedTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edges.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 5 (*triangle_adjacency_assignment*) @ line 404:
  `*at1 = *at2 = *at3 = tt;`
  After the triangle object is created (Branch 4), all three slot pointers at1, at2,
  at3 are written to point to tt. This bi-directional link makes each bounding edge
  aware of the new triangle. The adjacency assignment is identical to CreateTriangle's
  Branch 5 (Me354) but reached without orientation gating.

Defect carrier: two triangles sharing an edge, demonstrating that both at-slot
assignments fired correctly for the shared edge. The first triangle's CreateUnoriented-
Triangle call wrote tt into e_diag->t1; the second call wrote tt into e_diag->t2.
The resulting n=2 on the shared edge confirms that *at1=*at2=*at3=tt executed for
both calls, linking each triangle into its bounding edges.

Geometry (right-angle pair — same layout as Me354 for easy comparison):
  v0=(0,0,0), v1=(3,0,0), v2=(3,3,0), v3=(0,3,0)
  t0=(v0,v1,v2) — first creation; diagonal e_diag->t1=t0
  t1=(v0,v2,v3) — second creation; diagonal e_diag->t2=t1
  Diagonal edge (v0,v2): n=2 after both *at assignments.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me964",
    title="CreateUnorientedTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edge slots to tt (Branch 5)",
    defect_class="create_unoriented_triangle_adjacency_assignment",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(3.0, 3.0, 0.0)   # 2
v3 = m.vertex(0.0, 3.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0 — first call; *at1=t0 wrote diagonal->t1=t0
t1 = m.triangle(v0, v2, v3)   # 1 — second call; *at1=t1 wrote diagonal->t2=t1

# Shared diagonal edge (v0,v2): both adjacency slots filled (n=2).
m.assert_edge_shared(v0, v2, 2)   # Branch 5: *at= assignments confirmed

# Boundary edges: each owned by exactly one triangle's adjacency assignment.
m.assert_edge_shared(v0, v1, 1)   # t0 only
m.assert_edge_shared(v1, v2, 1)   # t0 only
m.assert_edge_shared(v2, v3, 1)   # t1 only
m.assert_edge_shared(v0, v3, 1)   # t1 only

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(v=4, e=5, f=2, chi=1)
