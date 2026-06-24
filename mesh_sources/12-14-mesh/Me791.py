"""Me791 — PMP.non_manifold_vertices umbrella_sector_boundary: border halfedge at boundary of umbrella sector around open-mesh pinch vertex triggers is_border check (Branch 2).

CGAL PMP `PMP.non_manifold_vertices` Branch 2 (*umbrella_sector_boundary*) @ line 280:
  'if(is_border(hf, tm)) { ... }'
  — while walking the half-edge star around a non-manifold vertex, the algorithm
  tests whether each half-edge is a border half-edge. When the umbrella sector has
  an open boundary (the mesh is not closed at that sector), is_border fires and the
  algorithm marks that sector boundary and advances to the next sector.

Input pattern: a pinch vertex with two open-ended umbrella sectors separated by
  border halfedges. Unlike Me790 (classic bowtie with symmetric fans), here the
  pinch vertex is at the tip of two open fans — each fan has a border halfedge
  emanating from hub — giving the vertex a 'star' whose traversal encounters
  is_border at sector boundaries.

Defect: vertex hub=(0,0,0) is a non-manifold pinch vertex with boundary halfedges.
  Sector A (open fan of 3 triangles):
    t0=(hub, a0, a1), t1=(hub, a1, a2), t2=(hub, a2, a3)
    a0=(2,1,0), a1=(1,1,0), a2=(0,1,0), a3=(-1,1,0)
    Interior edges (hub,a1) n=2, (hub,a2) n=2.
    Border edges at hub: (hub,a0) n=1, (hub,a3) n=1.
  Sector B (isolated single triangle):
    t3=(hub, b0, b1)
    b0=(1,-1,0), b1=(-1,-1,0)
    Both edges at hub are border: (hub,b0) n=1, (hub,b1) n=1.

  When PMP.non_manifold_vertices traverses sector B and reaches the border
  halfedge (hub,b0) or (hub,b1), is_border fires (Branch 2).

Topology:
  Interior edges: (hub,a1) n=2, (hub,a2) n=2.
  Border edges at hub: (hub,a0) n=1, (hub,a3) n=1, (hub,b0) n=1, (hub,b1) n=1.
  Sector A outer rim: (a0,a1) n=1, (a1,a2) n=1, (a2,a3) n=1.
  Sector B outer: (b0,b1) n=1.

Euler: V=7 (hub + a0..a3 + b0 + b1), E=12, F=4, chi=7-12+4=-1.
  Wait: V=1+4+2=7. Edges: hub→a0,a1,a2,a3 = 4; hub→b0,b1 = 2; a0-a1,a1-a2,a2-a3 = 3; b0-b1 = 1. Total E=10.
  chi = 7 - 10 + 4 = 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me791",
    title="PMP.non_manifold_vertices umbrella_sector_boundary: open-mesh pinch vertex; border halfedge at sector boundary triggers is_border; 3-triangle sector A + 1-triangle sector B (Branch 2)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex( 0.0,  0.0, 0.0)  # 0 — pinch vertex (non-manifold)

# Sector A — open 3-triangle fan (upper, y > 0)
a0 = m.vertex( 2.0,  1.0, 0.0)  # 1 — rightmost outer rim
a1 = m.vertex( 1.0,  1.0, 0.0)  # 2 — right-mid outer rim (interior at hub)
a2 = m.vertex( 0.0,  1.0, 0.0)  # 3 — left-mid outer rim (interior at hub)
a3 = m.vertex(-1.0,  1.0, 0.0)  # 4 — leftmost outer rim

# Sector B — isolated single triangle (lower, y < 0)
b0 = m.vertex( 1.0, -1.0, 0.0)  # 5 — right rim
b1 = m.vertex(-1.0, -1.0, 0.0)  # 6 — left rim

# Sector A: 3 triangles sharing successive interior edges at hub.
t0 = m.triangle(hub, a0, a1)  # 0: rightmost — shares (hub,a1) with t1
t1 = m.triangle(hub, a1, a2)  # 1: middle — shares (hub,a1) with t0 and (hub,a2) with t2
t2 = m.triangle(hub, a2, a3)  # 2: leftmost — shares (hub,a2) with t1

# Sector B: single isolated triangle at hub.
t3 = m.triangle(hub, b0, b1)  # 3: lower isolated triangle

# Interior fan edges within sector A — shared by 2 triangles each.
m.assert_edge_shared(hub, a1, 2)  # (0,2): shared by t0 and t1
m.assert_edge_shared(hub, a2, 2)  # (0,3): shared by t1 and t2

# Border hub edges (1 triangle each) — is_border fires at these.
m.assert_edge_shared(hub, a0, 1)  # (0,1): sector A left boundary
m.assert_edge_shared(hub, a3, 1)  # (0,4): sector A right boundary
m.assert_edge_shared(hub, b0, 1)  # (0,5): sector B left boundary  ← is_border fires
m.assert_edge_shared(hub, b1, 1)  # (0,6): sector B right boundary ← is_border fires

# Sector A outer rim edges.
m.assert_edge_shared(a0, a1, 1)  # (1,2): t0 outer rim
m.assert_edge_shared(a1, a2, 1)  # (2,3): t1 outer rim
m.assert_edge_shared(a2, a3, 1)  # (3,4): t2 outer rim

# Sector B outer edge.
m.assert_edge_shared(b0, b1, 1)  # (5,6): t3 outer edge

# hub's fan is disconnected: Sector A (t0,t1,t2) and Sector B (t3) share no edge.
m.assert_vertex_fan_disconnected(hub)

# Euler: V=7, E=10, F=4, chi=7-10+4=1.
m.assert_euler_characteristic(7, 10, 4, 1)
