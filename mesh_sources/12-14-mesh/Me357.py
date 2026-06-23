"""Me357 — CreateTriangle_topology_invalidation: d_boundaries=d_handles=d_shells=1 after creation.

MeshFix `Basic_TMesh.CreateTriangle` Branch 8 (*topology_invalidation*) @ line 381:
  `d_boundaries = d_handles = d_shells = 1;`
  The last step of CreateTriangle marks all three topology-cache flags as dirty.
  This forces the mesh to lazily recompute boundary count, handle count (genus),
  and shell count on the next query — necessary because adding a triangle can
  change all three.

Defect carrier: a mesh where a new triangle closes a boundary loop, changing the
topology. Before creation: an open hole (boundary edge count > 0). After creation:
a closed shell (boundary = 0 if the triangle plugs the last hole, or changed genus
if it creates a handle). The d_boundaries/d_handles/d_shells flags must be set
dirty so next-query recomputes reflect the new topology.

Geometry: tetrahedron (closed manifold), 4 triangles. Adding the 4th triangle
(tf) closes the last open boundary, invalidating all three caches — exactly what
Branch 8 forces the flags to track. χ = V - E + F = 4 - 6 + 4 = 2 (sphere).

  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,0.33,1)
  t0=(v0,v1,v2), t1=(v0,v3,v1), t2=(v1,v3,v2) — 3 existing open-shell triangles
  tf=(v0,v2,v3) — 4th triangle added by CreateTriangle; closes the shell
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me357",
    title="CreateTriangle_topology_invalidation: d_boundaries=d_handles=d_shells=1 on closed shell (Branch 8)",
    defect_class="create_triangle_topology_invalidation",
)

v0 = m.vertex(0.0, 0.0,  0.0)   # 0
v1 = m.vertex(1.0, 0.0,  0.0)   # 1
v2 = m.vertex(0.5, 1.0,  0.0)   # 2
v3 = m.vertex(0.5, 0.33, 1.0)   # 3 — apex above the base triangle

# Three pre-existing faces of the tetrahedron.
t0 = m.triangle(v0, v1, v2)   # 0 — base
t1 = m.triangle(v0, v3, v1)   # 1 — front face
t2 = m.triangle(v1, v3, v2)   # 2 — right face

# tf: the closing triangle added by CreateTriangle, triggering Branch 8.
tf = m.triangle(v0, v2, v3)   # 3 — left face (closes the shell)

# All 6 tetrahedron edges are now interior (n=2): the shell is closed.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler characteristic of a closed genus-0 surface: χ = V - E + F = 4 - 6 + 4 = 2.
# d_boundaries/d_handles/d_shells all invalidated by Branch 8 after tf is added.
m.assert_euler_characteristic(v=4, e=6, f=4, chi=2)
