"""Me216 — cutAndStitch_bounded_singular_chain: linked singular edge pinched with common vertex.

MeshFix `Basic_TMesh.cutAndStitch` Branch 7 (*BOUNDED_SINGULAR_CHAIN*) @ line 1018:
  'if (e1->isLinked()) pinch(e1, true)'
  After grouping, cutAndStitch iterates singular edges that still remain linked
  (not yet stitched). Linked singular edges whose endpoints both connect to other
  boundary edges form a bounded chain with endpoints; these are pinched using
  with_common_vertex=true, meaning the merge starts from a shared vertex.

Defect pattern: two boundary edges at the same geometric position but each
belonging to a different open mesh boundary. One edge's endpoint coincides with
the other's vertex, forming a bounded chain. A healer must pinch (merge) these
edges starting from the common vertex.

Geometry: a two-patch mesh with a T-shaped seam.
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  t0=(v0,v1,v2) — single triangle
  Patch B: v3=(0,0,0), v4=(1,0,0), v5=(0.5,-1,0)
  t1=(v3,v5,v4) — faces down

  Seam edge A: boundary (v0,v1) on t0
  Seam edge B: boundary (v3,v4) on t1, v3 coincident with v0, v4 coincident with v1.
  These two boundary edges form a bounded chain (finite open seam with endpoints).
  pinch(e_seam_A, true) merges from v0≡v3 common-vertex side.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me216",
             title="cutAndStitch_bounded_singular_chain: boundary seam pinched from common vertex (with_common_vertex=true)",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — patch A left endpoint
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — patch A right endpoint
v2 = m.vertex(0.5, 1.0, 0.0)    # 2 — patch A apex

v3 = m.vertex(0.0, 0.0, 0.0)    # 3 — patch B left endpoint (coincident with v0)
v4 = m.vertex(1.0, 0.0, 0.0)    # 4 — patch B right endpoint (coincident with v1)
v5 = m.vertex(0.5, -1.0, 0.0)   # 5 — patch B apex

t0 = m.triangle(v0, v1, v2)    # 0 — patch A
t1 = m.triangle(v3, v5, v4)    # 1 — patch B (CW)

# The seam boundary edges on both patches.
m.assert_edge_shared(v0, v1, 1)   # patch A seam — bounded chain first edge
m.assert_edge_shared(v3, v4, 1)   # patch B seam — bounded chain second edge

# Coincident endpoints confirm the chain is bounded (has identifiable vertices).
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)

# Other boundaries.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
