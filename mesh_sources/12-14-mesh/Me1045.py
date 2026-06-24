"""Me1045 — stitch_borders halfedge-pair-orientation: hd_kpr canonical swap ensures first halfedge is canonical.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 6 (*halfedge-pair-orientation*) @ line 473:
  'if (hd_kpr(hp.second, hp.first)) std::swap(hp.first, hp.second);'
  After identifying a matching boundary halfedge pair, the dispatcher checks whether
  the pair needs to be swapped to maintain canonical ordering (first < second under
  the halfedge descriptor comparator hd_kpr). Branch 6 fires when the pair's
  current orientation is non-canonical and a swap is performed.

Defect pattern: two patches with a stitchable seam where the boundary halfedges
  are discovered in reverse canonical order. Patch A has boundary halfedge hA along
  (v1,v0), and Patch B has boundary halfedge hB along (v3,v2). When matched as a
  pair, hB < hA under hd_kpr (i.e. the second halfedge is canonically smaller than
  the first), triggering the swap so that the smaller descriptor becomes hp.first.

Geometry:
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
    t0=(v0,v1,v2) — single open triangle; all edges boundary
  Patch B: v3=(1,0,0)[=v1], v4=(0,0,0)[=v0], v5=(0.5,-1,0)
    t1=(v3,v4,v5) — second open triangle; all edges boundary
  The edge (v0,v1) on Patch A is coincident with (v3,v4)=(v1,v0) on Patch B —
  same endpoints but opposite traversal direction. The canonical order comparison
  fires and may swap the pair.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1045",
    title="stitch_borders halfedge-pair-orientation: hd_kpr canonical swap fires for non-canonical halfedge pair; two patches with reversed coincident boundary edge",
    defect_class="boundary_gap_thin",
)

# Patch A — top triangle
v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2

# Patch B — bottom triangle with coincident seam edge in reversed orientation
v3 = m.vertex(1.0, 0.0, 0.0)    # 3 — coincident with v1
v4 = m.vertex(0.0, 0.0, 0.0)    # 4 — coincident with v0
v5 = m.vertex(0.5, -1.0, 0.0)   # 5 — far vertex

t0 = m.triangle(v0, v1, v2)     # 0 — Patch A
t1 = m.triangle(v3, v4, v5)     # 1 — Patch B; seam edge (v3,v4) == reversed (v0,v1)

# All edges are boundary (n=1)
m.assert_edge_shared(v0, v1, 1)  # Patch A seam edge (geometric position)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

m.assert_edge_shared(v3, v4, 1)  # Patch B seam edge (same geometry, reversed halfedge)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# Coincident vertex pairs (stitchable seam)
m.assert_vertex_pair_distance_lt(v0, v4, 1e-9)  # v0 == v4 geometrically
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)  # v1 == v3 geometrically

# No shared triangle between coincident vertex pairs
m.assert_vertex_pair_no_shared_triangle(v0, v4)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Components are disconnected
m.assert_triangle_not_reachable_from(t1, t0)
