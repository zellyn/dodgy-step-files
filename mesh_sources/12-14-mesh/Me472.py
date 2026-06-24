"""Me472 — remove_a_border_edge boundary_reached_during_exploration: region contacts outer boundary (Branch 3).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 3 (*boundary_reached_during_exploration*) @ line 1255:
  'is_border(opposite(h, tmesh), tmesh)' during BFS region grow → boundary reached;
  function returns null_vertex (abort removal).

When the algorithm tries to grow the face region to be removed around a border edge
it does a BFS over adjacent faces. If during BFS it reaches another border halfedge
(the region contacts the outer boundary of the mesh on a second side), it cannot
form a closed disk and aborts.

This happens when the region of marked faces is topologically an open strip that
touches the mesh boundary on both sides, so the BFS traversal exits through the
second boundary before enclosing the region.

Geometry: a chain of three triangles forming an open strip where the region
exploration must cross from the first boundary to the second.
  v0=(0,0,0), v1=(2,0,0), v2=(4,0,0)  — bottom row
  v3=(1,1,0), v4=(3,1,0)              — top row
  t0=(v0,v1,v3) — left triangle
  t1=(v1,v4,v3) — middle triangle; shares (v1,v3) with t0 and (v1,v4)? No.

Simpler: single triangle with THREE border edges — the region exploration from any
border edge immediately finds another border halfedge → branch fires.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  t0=(v0,v1,v2) — all three edges are border (n=1).

Starting from border edge (v0,v1) the BFS would try to expand through the interior
of the triangle, but the opposite halfedges of (v0,v2) and (v1,v2) are also border
→ boundary reached immediately during region exploration.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me472",
    title="remove_a_border_edge boundary_reached_during_exploration: all three edges are border; region touches outer boundary immediately (Branch 3)",
    defect_class="border_edge_boundary_reached_during_exploration",
)

# Single triangle: all three edges are border (n=1).
# When remove_a_border_edge tries to expand the face region from any border edge,
# it immediately finds the other two edges are also border → boundary reached.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

t0 = m.triangle(v0, v1, v2)   # 0 — isolated single triangle, fully on boundary

# All edges are border (n=1): the region has no interior to expand into.
m.assert_edge_shared(v0, v1, 1)   # border edge — trigger edge
m.assert_edge_shared(v1, v2, 1)   # border — reached during exploration
m.assert_edge_shared(v0, v2, 1)   # border — reached during exploration

# The single boundary loop encloses the entire patch.
m.assert_hole_boundary([v0, v1, v2])

# Euler: V=3, E=3, F=1, chi=1 (open disk / single triangle).
m.assert_euler_characteristic(3, 3, 1, 1)
