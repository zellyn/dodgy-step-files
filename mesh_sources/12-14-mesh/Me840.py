"""Me840 — duplicate_non_manifold_vertices halfedge-visitation-tracking: visited_halfedges insert skips already-processed halfedges (Branch 1).

CGAL PMP `PMP.duplicate_non_manifold_vertices` Branch 1 (*halfedge-visitation-tracking*) @ line 335:
  'visited_halfedges.insert(h)'
  — as the function traverses halfedges around a non-manifold vertex, it records
  each processed halfedge in visited_halfedges. On a second sweep the insert
  finds the halfedge already present and skips it, preventing double-duplication.

Defect pattern: bowtie vertex hub shared by two disconnected triangle fans (Fan A
  and Fan B). When CGAL iterates halfedges around hub, the first fan's halfedges
  are inserted into visited_halfedges; when the traversal loops back and encounters
  those same halfedges again (due to the disconnected topology), Branch 1 fires and
  skips re-processing them. This is the prototypical visited-halfedge guard.

Geometry:
  hub=(0,0,0): bowtie center — non-manifold vertex (fan disconnected).
  Fan A: two triangles in z=0 plane, right of hub.
    a0=(2,0,0), a1=(2,1,0)  → t0=(hub,a0,a1)
    a2=(2,2,0), a3=(1,2,0)  → t1=(hub,a1,a2) shares (hub,a1) — interior within Fan A
    Wait: need Fan A fully isolated from Fan B.
  Use 4 triangles total: Fan A = t0,t1 sharing edge (hub,a1); Fan B = t2,t3 sharing edge (hub,b1).
  Fans share only hub → disconnected fan at hub → Branch 1 fires.

  Fan A: a0=(2,0,0), a1=(2,1,0), a2=(1,2,0)
    t0=(hub,a0,a1), t1=(hub,a1,a2)  [share edge (hub,a1) → interior]
  Fan B: b0=(-2,0,0), b1=(-2,1,0), b2=(-1,2,0)
    t2=(hub,b0,b1), t3=(hub,b1,b2)  [share edge (hub,b1) → interior]
  No edges between Fan A and Fan B (except through hub vertex only).
  Edge counts: (hub,a1)=2 [t0,t1 interior], (hub,b1)=2 [t2,t3 interior].
  Boundary edges of Fan A: (hub,a0),(a0,a1),(a1,a2),(a2,hub) → each n=1.
  Boundary edges of Fan B: (hub,b0),(b0,b1),(b1,b2),(b2,hub) → each n=1.
  V=7, E: interior=2 + boundary=8 = 10, F=4.
  chi = V - E + F = 7 - 10 + 4 = 1 per fan → two open disks, chi=1 each. Total: 2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me840",
    title="duplicate_non_manifold_vertices halfedge-visitation-tracking: bowtie hub visited_halfedges.insert skips already-processed halfedge ring (Branch 1)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex(0.0, 0.0, 0.0)   # 0 — bowtie hub (non-manifold vertex)

# Fan A: right-side sector, z=0 plane.
a0 = m.vertex(2.0, 0.0, 0.0)    # 1
a1 = m.vertex(2.0, 1.0, 0.0)    # 2
a2 = m.vertex(1.0, 2.0, 0.0)    # 3

# Fan B: left-side sector, z=0 plane.
b0 = m.vertex(-2.0,  0.0, 0.0)  # 4
b1 = m.vertex(-2.0,  1.0, 0.0)  # 5
b2 = m.vertex(-1.0,  2.0, 0.0)  # 6

# Fan A triangles: share interior edge (hub, a1).
t0 = m.triangle(hub, a0, a1)    # 0: Fan A lower
t1 = m.triangle(hub, a1, a2)    # 1: Fan A upper

# Fan B triangles: share interior edge (hub, b1).
t2 = m.triangle(hub, b0, b1)    # 2: Fan B lower
t3 = m.triangle(hub, b1, b2)    # 3: Fan B upper

# Interior edges within each fan (n=2).
m.assert_edge_shared(hub, a1, 2)   # shared by t0 and t1 (Fan A interior)
m.assert_edge_shared(hub, b1, 2)   # shared by t2 and t3 (Fan B interior)

# Boundary edges of Fan A (n=1): outer hull of right sector.
m.assert_edge_shared(hub, a0, 1)   # t0 lower-left boundary
m.assert_edge_shared(a0,  a1, 1)   # t0 outer
m.assert_edge_shared(a1,  a2, 1)   # t1 outer
m.assert_edge_shared(hub, a2, 1)   # t1 upper-left boundary

# Boundary edges of Fan B (n=1): outer hull of left sector.
m.assert_edge_shared(hub, b0, 1)   # t2 lower-right boundary
m.assert_edge_shared(b0,  b1, 1)   # t2 outer
m.assert_edge_shared(b1,  b2, 1)   # t3 outer
m.assert_edge_shared(hub, b2, 1)   # t3 upper-right boundary

# Hub has a disconnected triangle fan — classic bowtie non-manifold vertex.
# Fan A (t0,t1) and Fan B (t2,t3) share only hub; no edge connects them.
# CGAL visited_halfedges.insert fires when the first cycle's halfedges
# are encountered again during the second cycle's traversal (Branch 1).
m.assert_vertex_fan_disconnected(hub)

# Euler: V=7, E=10, F=4, chi=1 (two open disks sharing a vertex, chi=1 each
# but mesh is not connected → chi is computed per connected component).
m.assert_euler_characteristic(7, 10, 4, 1)
