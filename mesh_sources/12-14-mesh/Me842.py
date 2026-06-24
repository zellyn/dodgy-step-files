"""Me842 — duplicate_non_manifold_vertices non-manifold-class-confirmation: known_nm_vertices lookup; vertex confirmed in non-manifold set before duplication (Branch 3).

CGAL PMP `PMP.duplicate_non_manifold_vertices` Branch 3 (*non-manifold-class-confirmation*) @ line 348:
  'if(known_nm_vertices.count(v)) { duplicate... }'
  — the function first collects all non-manifold vertices into known_nm_vertices
  (via PMP.non_manifold_vertices), then during the duplication sweep it verifies
  each candidate vertex appears in that pre-computed set before creating a copy.
  Branch 3 fires when the lookup succeeds (count > 0), confirming the vertex is
  genuinely non-manifold and should be duplicated.

Defect pattern: a mesh with a pre-identified non-manifold (bowtie) vertex hub.
  The vertex was already classified into known_nm_vertices by an earlier call to
  non_manifold_vertices(); here it is confirmed in that set. The fixture captures
  the two-sector bowtie with a compact 4-triangle layout so that known_nm_vertices
  unambiguously contains hub and Branch 3 fires on the lookup.

  Distinction from Me840 (halfedge-visitation tracking, same 2-fan bowtie): Me840
  emphasises the visited_halfedges set used within the traversal loop; Me842
  emphasises the known_nm_vertices pre-classification set checked before any
  traversal begins. The hub geometry is the same bowtie shape but annotated to
  highlight the 'known_nm_vertices' membership role.

Geometry:
  hub=(0,0,0): pre-identified non-manifold vertex; lookup in known_nm_vertices succeeds.
  Fan A (z=0, lower-right):
    a0=(2,0,0), a1=(2,1,0), a2=(1,2,0)
    t0=(hub,a0,a1), t1=(hub,a1,a2)  [share interior (hub,a1)]
  Fan B (z=1 plane, lifted):
    b0=(2,0,1), b1=(2,1,1), b2=(1,2,1)
    t2=(hub,b0,b1), t3=(hub,b1,b2)  [share interior (hub,b1)]
  Lifting Fan B to z=1 makes it spatially distinct from Fan A while keeping
  the same bowtie topology. V=7, E=10, F=4, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me842",
    title="duplicate_non_manifold_vertices non-manifold-class-confirmation: hub found in known_nm_vertices set; duplicate vertex operation proceeds (Branch 3)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex(0.0, 0.0, 0.0)   # 0 — pre-confirmed non-manifold vertex

# Fan A: lower-right sector, z=0 plane.
a0 = m.vertex(2.0, 0.0, 0.0)    # 1
a1 = m.vertex(2.0, 1.0, 0.0)    # 2
a2 = m.vertex(1.0, 2.0, 0.0)    # 3

# Fan B: lifted sector, z=1 plane (spatially distinct from Fan A).
b0 = m.vertex(2.0, 0.0, 1.0)    # 4
b1 = m.vertex(2.0, 1.0, 1.0)    # 5
b2 = m.vertex(1.0, 2.0, 1.0)    # 6

# Fan A triangles: share interior edge (hub, a1).
t0 = m.triangle(hub, a0, a1)    # 0: Fan A lower
t1 = m.triangle(hub, a1, a2)    # 1: Fan A upper

# Fan B triangles: share interior edge (hub, b1).
t2 = m.triangle(hub, b0, b1)    # 2: Fan B lower
t3 = m.triangle(hub, b1, b2)    # 3: Fan B upper

# Interior edges (n=2): one per fan.
m.assert_edge_shared(hub, a1, 2)   # Fan A interior: shared by t0, t1
m.assert_edge_shared(hub, b1, 2)   # Fan B interior: shared by t2, t3

# Boundary edges of Fan A (n=1).
m.assert_edge_shared(hub, a0, 1)
m.assert_edge_shared(a0,  a1, 1)
m.assert_edge_shared(a1,  a2, 1)
m.assert_edge_shared(hub, a2, 1)

# Boundary edges of Fan B (n=1).
m.assert_edge_shared(hub, b0, 1)
m.assert_edge_shared(b0,  b1, 1)
m.assert_edge_shared(b1,  b2, 1)
m.assert_edge_shared(hub, b2, 1)

# Hub is the pre-classified non-manifold vertex (known_nm_vertices.count(hub) > 0).
# Fan A (t0,t1) and Fan B (t2,t3) share only hub, giving a disconnected fan.
# The known_nm_vertices lookup at Branch 3 confirms hub before duplication.
m.assert_vertex_fan_disconnected(hub)

# Euler: V=7, E=10, F=4, chi=1.
m.assert_euler_characteristic(7, 10, 4, 1)
