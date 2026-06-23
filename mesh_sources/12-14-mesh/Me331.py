"""Me331 — pinch_non_manifold_vertex_boundary: two boundary edges share vertex, pinch merges them.

MeshFix `Basic_TMesh.pinch` Branch 2 (*NON_MANIFOLD_VERTEX_BOUNDARY*) @ line 926:
  'if (with_common_vertex) { ... if (e2->isOnBoundary()) { e1->merge(e2); return true; } }'
  When pinch is called with with_common_vertex=true, v1 of e1 must have a
  boundary edge e2 whose opposite endpoint matches v2 of e1. If found,
  the two coincident boundary edges are merged (stitched) in place.

Defect pattern: two triangle patches whose boundary edges meet at a shared
vertex but are not yet stitched. Edge (v0,v1) is the seam: patch A has
boundary edge (v0→v1) and patch B has boundary edge (v0→v1) as well —
two boundary edges at the same position that should be merged into a
single shared interior edge.

Geometry: two coplanar triangles sharing vertex v0 with coincident but
unstitched boundary edges (v0,v1) and (v0,v1).

  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0); boundary edge (v0,v1) n=1.
  Patch B: v3=v0=(0,0,0) [same coords], v4=v1=(1,0,0) [same coords],
           v5=(0.5,-1,0); boundary edge (v3,v4) n=1.

  Since v3 and v0 are distinct vertex entries at the same coordinates,
  the edge (v0,v1) and (v3,v4) are coincident but not yet merged.
  After pinch Branch 2 fires and merges them, they become n=2.

  We represent this pre-merge state: two triangles, each with their own
  near-coincident boundary edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me331",
             title="pinch_non_manifold_vertex_boundary: two coincident boundary edges at shared vertex, awaiting merge",
             defect_class="non_manifold_edge")

# Patch A
v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(1.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.5,  1.0, 0.0)   # 2

# Patch B — v3,v4 are near-coincident with v0,v1 (same coords, different indices)
v3 = m.vertex(0.0,  0.0, 0.0)   # 3 (coincident with v0)
v4 = m.vertex(1.0,  0.0, 0.0)   # 4 (coincident with v1)
v5 = m.vertex(0.5, -1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — patch A
t1 = m.triangle(v3, v4, v5)   # 1 — patch B

# Pre-merge state: each boundary edge appears on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)   # patch A seam — boundary
m.assert_edge_shared(v3, v4, 1)   # patch B seam — boundary (coincident with above)

# Coincident vertex pairs.
m.assert_vertex_pair_distance_lt(v0, v3, 1e-7)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-7)

# All other edges are also boundary.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)

# Two disconnected components before merge.
m.assert_triangle_not_reachable_from(t1, t0)
