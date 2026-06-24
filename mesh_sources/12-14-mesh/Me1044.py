"""Me1044 — stitch_borders non-manifold-pair-filter: manifold_halfedge_pairs filter skips pairs that would create non-manifold edges.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 5 (*non-manifold-pair-filter*) @ line 470:
  'manifold_halfedge_pairs(pairs, mesh);'
  Before stitching, the dispatcher filters the collected halfedge pairs through
  manifold_halfedge_pairs to remove any candidate pair whose stitching would produce
  a non-manifold edge (an edge shared by more than 2 triangles). Branch 5 fires
  when at least one pair is rejected by the manifold filter.

Defect pattern: a mesh with a T-junction boundary configuration. Three triangles
  meet at a shared vertex, and two candidate boundary edges at that vertex would,
  if stitched, create an edge shared by 3 triangles (non-manifold). The manifold
  filter rejects this pair and retains only the safe stitchable pair.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0), v4=(-0.5,0,0)
  t0=(v0,v1,v2) — top triangle
  t1=(v0,v3,v1) — bottom triangle, shares (v0,v1) with t0 → ALREADY interior
  t2=(v4,v0,v2) — left triangle, shares (v0,v2) with t0 → ALREADY interior

  This gives the fan around v0 with (v0,v1) n=2 and (v0,v2) n=2.
  Boundary: (v1,v2) n=1, (v0,v3) n=1, (v1,v3) n=1, (v4,v0) n=1, (v4,v2) n=1.

  A candidate pair targeting (v1,v2) from t0 and (v4,v2) from t2 would stitch
  those boundary edges. However a "T-junction" arises from a near-coincident pair
  at v1/v3-side that if stitched would share edge with a third triangle.

  Use a simpler and more direct approach: two coincident boundary edges where
  stitching one would create a non-manifold edge (already shared by 2 triangles).

  Concrete layout:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  v3=(0,0,0)[=v0 coincident], v4=(1,0,0)[=v1 coincident], v5=(0.5,1,0)[=v2 coincident]
  v6=(0.5,-1,0) — extra vertex to create third triangle that shares (v0,v1)
  t0=(v0,v1,v2) — Triangle 0
  t1=(v3,v4,v5) — Triangle 1: fully coincident with t0 (duplicate face - non-manifold)
  t2=(v0,v1,v6) — Triangle 2: shares edge (v0,v1) with t0
  If stitching t1's boundary onto t0's boundary → edge (v0,v1) would be shared by 3 triangles
  → non-manifold pair filter must reject this.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1044",
    title="stitch_borders non-manifold-pair-filter: manifold_halfedge_pairs filter rejects candidate that would create edge shared by 3 triangles",
    defect_class="non_manifold_edge",
)

# Base triangle
v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2

# Coincident ghost triangle (nearly duplicate)
v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — coincident with v0
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — coincident with v1
v5 = m.vertex(0.5, 1.0, 0.0)    # 5 — coincident with v2

# Third triangle sharing (v0,v1) — already-occupied edge
v6 = m.vertex(0.5, -1.0, 0.0)   # 6

t0 = m.triangle(v0, v1, v2)     # 0
t1 = m.triangle(v3, v4, v5)     # 1 — coincident ghost
t2 = m.triangle(v0, v6, v1)     # 2 — shares (v0,v1) with t0

# (v0,v1) is already shared by t0 and t2 — stitching t1's (v3,v4) boundary
# onto (v0,v1) would create a non-manifold edge (n=3).
m.assert_edge_shared(v0, v1, 2)  # already interior — n=2

# Coincident vertex pairs — potential stitch candidates
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# All edges of t1 are boundary (n=1)
m.assert_edge_shared(v3, v4, 1)  # n=1 — candidate stitch that would become non-manifold
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# Edges of t0 that are boundary
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Edges of t2 that are boundary
m.assert_edge_shared(v0, v6, 1)
m.assert_edge_shared(v1, v6, 1)
