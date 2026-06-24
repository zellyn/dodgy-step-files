"""Me474 — remove_a_border_edge isolated_region: region completely surrounded by border (Branch 5).

CGAL PMP `PMP.remove_a_border_edge.with_sets` Branch 5 (*isolated_region*) @ line 1304:
  'is_border(hk1, tmesh)' → the half-edge going around the region is itself a border;
  function returns null_vertex (isolated region cannot be removed).

When the algorithm identifies the candidate face region and tries to find the
halfedge that goes around its outer boundary, it checks if hk1 (the halfedge
after the border edge in the one-ring traversal) is itself a border halfedge.
If it is, the region is completely isolated — every edge bounding the region
is a border edge, so there is no interior anchor to attach to after removal.
The algorithm returns null_vertex.

A single isolated triangle (all three edges on the boundary) is the minimal
isolated-region fixture: every edge is a border edge (n=1), so any halfedge
selected as hk1 will also be a border halfedge → Branch 5 fires.

Wait — this is almost identical to Me472. The distinction is:
- Me472 (Branch 3): region exploration BFS hits another border halfedge DURING
  traversal (discovered while expanding the region).
- Me474 (Branch 5): after region is already identified, hk1 — the halfedge
  pointing *around* the completed region — is itself a border → isolated.

For Me474 we want a LARGER isolated patch: a connected patch of 4 triangles
where ALL boundary halfedges of the patch are border halfedges of the full mesh.
This makes the entire patch a free-floating island with no attachment. Using a
quad-patch (4 triangles from 4 quads): a 2x1 strip of two quads → 4 triangles,
with all 6 border edges on the outer boundary.

Geometry: 2-quad strip of 4 triangles, all outer edges border.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)  — bottom row
  v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)  — top row
  t0=(v0,v1,v4), t1=(v0,v4,v3) — left quad
  t2=(v1,v2,v5), t3=(v1,v5,v4) — right quad
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me474",
    title="remove_a_border_edge isolated_region: 4-triangle free-floating island; all boundary edges are border; hk1 is always border (Branch 5)",
    defect_class="border_edge_isolated_region",
)

# 2x1 grid of quads → 4 triangles, fully isolated patch.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — bottom-center
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — bottom-right
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — top-left
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — top-center (interior vertex)
v5 = m.vertex(2.0, 1.0, 0.0)   # 5 — top-right

# Left quad: t0+t1.
t0 = m.triangle(v0, v1, v4)   # 0
t1 = m.triangle(v0, v4, v3)   # 1
# Right quad: t2+t3.
t2 = m.triangle(v1, v2, v5)   # 2
t3 = m.triangle(v1, v5, v4)   # 3

# Interior shared edges (n=2).
m.assert_edge_shared(v0, v4, 2)   # left-quad diagonal
m.assert_edge_shared(v1, v4, 2)   # center shared edge between left and right quads
m.assert_edge_shared(v1, v5, 2)   # right-quad diagonal

# All boundary edges are border (n=1): the patch is fully isolated.
m.assert_edge_shared(v0, v1, 1)   # bottom-left border
m.assert_edge_shared(v1, v2, 1)   # bottom-right border
m.assert_edge_shared(v2, v5, 1)   # right border
m.assert_edge_shared(v4, v5, 1)   # top-right border
m.assert_edge_shared(v3, v4, 1)   # top-left border
m.assert_edge_shared(v0, v3, 1)   # left border

# The outer boundary forms a single loop: v0→v1→v2→v5→v4→v3→v0.
m.assert_hole_boundary([v0, v1, v2, v5, v4, v3])

# Euler: V=6, E=9, F=4, chi=1 (open disk — one boundary component, simply connected).
# Wait: the patch IS simply connected (no inner hole), so chi=1, not an isolated fragment issue.
# The isolated_region branch fires not because of topology but because hk1 is a border edge.
m.assert_euler_characteristic(6, 9, 4, 1)
