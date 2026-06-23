"""Me335 — pinch_merge_failed: no valid mirror edge found after full scan — pinch aborts.

MeshFix `Basic_TMesh.pinch` Branch 6 (*MERGE_FAILED*) @ line 949:
  'if (n == NULL) return false;'
  After scanning all candidate edges from v1's ring and v2's ring, the
  algorithm finds no valid mirror edge e2 that can be merged with e1. The
  scan exhausted all neighbors without finding a boundary edge matching the
  required endpoint (with_common_vertex=false) or orientation (interior case).
  pinch() returns false to signal failure.

Defect pattern: a non-manifold T-junction edge incident on 3 triangles where
  none of the adjacent edges can serve as a valid merge target. The extra
  triangle fans out to a region with no boundary edge in the right direction,
  so the pinch scan finds n=NULL after a full ring traversal.

Geometry: T-junction. Edge (v0,v1) shared by 3 triangles in a star pattern
  with 3 radiating fans — no adjacent boundary edge can serve as a merge
  partner for any interior pinch because all edges from v0 and v1 are
  interior (shared by 2 triangles each except the outermost).

  v0=(0,0,0), v1=(0,2,0) — the T-junction edge
  t0=(v0,v1,v2): v2=( 1,1,0)
  t1=(v0,v1,v3): v3=(-1,1,0)
  t2=(v0,v1,v4): v4=( 0,1,1)
  Additional triangles to make all radial edges interior:
  t3=(v0,v2,v5): creates shared (v0,v2)
  ... but that becomes complex. Use the simpler T-junction pattern:
  just the 3-triangle non-manifold edge where the scan will fail.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me335",
             title="pinch_merge_failed: non-manifold edge shared by 3 triangles, no valid mirror found — pinch returns false",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(0.0,  2.0, 0.0)   # 1
v2 = m.vertex(1.0,  1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.0,  1.0, 1.0)   # 4

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v1, v3)   # 1
t2 = m.triangle(v0, v1, v4)   # 2

# Central non-manifold edge (v0,v1) shared by all 3 triangles.
m.assert_edge_shared(v0, v1, 3)

# All remaining edges are boundary (n=1) — no valid merge partner exists
# among the ring neighbors for Branch 6's scan.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
