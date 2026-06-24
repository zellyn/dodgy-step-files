"""Me792 — PMP.non_manifold_vertices visited_umbrella_detection: multi-sector pinch vertex; re-traversal attempt hits already-visited sector, visited_set check skips it (Branch 3).

CGAL PMP `PMP.non_manifold_vertices` Branch 3 (*visited_umbrella_detection*) @ line 295:
  'if(visited.find(hf) != visited.end()) continue;'  // (or equivalent guard)
  — after each umbrella sector around a non-manifold vertex is enumerated, its
  halfedges are added to the visited set. When the outer loop over halfedges around
  the target vertex reaches a halfedge that belongs to an already-enumerated sector,
  the visited_set check fires and the sector is skipped (Branch 3).

Input pattern: pinch vertex hub with THREE disconnected umbrella sectors.
  - Sector A: single triangle t0
  - Sector B: single triangle t1
  - Sector C: single triangle t2
  All three sectors share only hub (no shared edge between any pair of sectors).
  The algorithm enumerates Sector A first, adds its halfedges to visited.
  Then encounters Sector B — new, enumerates it.
  Then encounters Sector C — new, enumerates it.
  On subsequent iterations of the outer loop over halfedges_around_target(hub),
  the algorithm re-encounters halfedges from already-visited sectors; the visited_set
  check (Branch 3) fires and skips them.

Geometry (three sectors in 3D to visually separate them):
  Sector A (upper-right, z=0):  t0=(hub, a0, a1)  a0=(1,1,0)   a1=(2,0,0)
  Sector B (upper-left, z=0):   t1=(hub, b0, b1)  b0=(-1,1,0)  b1=(-2,0,0)
  Sector C (lower, z=1 plane):  t2=(hub, c0, c1)  c0=(0,-1,1)  c1=(0,-1,-1)

hub = (0,0,0). Three isolated triangle fans, each touching only at hub.

Topology:
  All edges at hub are border edges (n=1 each): (hub,a0), (hub,a1), (hub,b0),
  (hub,b1), (hub,c0), (hub,c1). Outer edges each n=1: (a0,a1), (b0,b1), (c0,c1).

Euler: V=7 (hub + 6 rim), E=9 (6 hub edges + 3 outer edges), F=3, chi=7-9+3=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me792",
    title="PMP.non_manifold_vertices visited_umbrella_detection: 3-sector bowtie hub; outer loop re-encounters visited halfedges; visited_set skip fires for sectors A and B on re-encounter (Branch 3)",
    defect_class="non_manifold_vertex",
)

hub = m.vertex( 0.0,  0.0,  0.0)  # 0 — pinch vertex with 3 disconnected sectors

# Sector A — upper-right triangle (z=0 plane)
a0 = m.vertex( 1.0,  1.0,  0.0)  # 1
a1 = m.vertex( 2.0,  0.0,  0.0)  # 2

# Sector B — upper-left triangle (z=0 plane)
b0 = m.vertex(-1.0,  1.0,  0.0)  # 3
b1 = m.vertex(-2.0,  0.0,  0.0)  # 4

# Sector C — lower triangle (spans z-axis, separated from A and B)
c0 = m.vertex( 0.0, -1.0,  1.0)  # 5
c1 = m.vertex( 0.0, -1.0, -1.0)  # 6

# Three isolated single-triangle sectors — all sharing only hub.
t0 = m.triangle(hub, a0, a1)  # 0: Sector A
t1 = m.triangle(hub, b0, b1)  # 1: Sector B
t2 = m.triangle(hub, c0, c1)  # 2: Sector C

# All hub edges are border edges — n=1 each.
m.assert_edge_shared(hub, a0, 1)  # (0,1): Sector A border
m.assert_edge_shared(hub, a1, 1)  # (0,2): Sector A border
m.assert_edge_shared(hub, b0, 1)  # (0,3): Sector B border
m.assert_edge_shared(hub, b1, 1)  # (0,4): Sector B border
m.assert_edge_shared(hub, c0, 1)  # (0,5): Sector C border
m.assert_edge_shared(hub, c1, 1)  # (0,6): Sector C border

# Outer rim edges — each belongs to one triangle.
m.assert_edge_shared(a0, a1, 1)  # (1,2): t0 outer
m.assert_edge_shared(b0, b1, 1)  # (3,4): t1 outer
m.assert_edge_shared(c0, c1, 1)  # (5,6): t2 outer

# hub's fan is disconnected: three sectors share no edges at hub.
m.assert_vertex_fan_disconnected(hub)

# No cross-sector triangle sharing — confirms 3 truly independent sectors.
m.assert_vertex_pair_no_shared_triangle(a0, b0)  # sectors A and B independent
m.assert_vertex_pair_no_shared_triangle(a0, c0)  # sectors A and C independent
m.assert_vertex_pair_no_shared_triangle(b0, c0)  # sectors B and C independent

# Euler: V=7, E=9, F=3, chi=7-9+3=1.
m.assert_euler_characteristic(7, 9, 3, 1)
