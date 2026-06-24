"""Me425 — checkAndRepair::removeOverlappingTriangles branch 6: SWAP_CREATES_T2_OVERLAP_PREV.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 6
(*SWAP_CREATES_T2_OVERLAP_PREV*) @ line 1013:
  `else if (e->t2->prevEdge(e)->overlaps())` — after swapping, the *previous*
  edge of t2 (the second incident triangle of the overlapping edge) overlaps a
  neighbor. The swap is undone.

This branch is symmetric to Branch 4 but checks the PREV edge of the second
triangle (t2) rather than the first (t1). It fires when the post-swap
arrangement creates an overlap at the edge *before* the swap edge in t2's CCW
traversal.

The fixture needs 3 triangles:
  - t0 and t1: the initial overlapping pair (coplanar, sharing edge e)
  - t3: neighbor sharing t2's prev-edge; positioned so that the swap would
    cause the post-swap t2's prev-edge to overlap t3.

Geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(3,0,0) — shared overlapping edge e=(v0,v1)
  v2=(1.5,3,0) — apex of t0 (large triangle; the "t1" in MeshFix half-edge)
  v3=(1.5,1,0) — apex of t1 (inside t0; the "t2" in MeshFix half-edge)

  After swap: edge (v0,v1) becomes (v2,v3).
    New t2-side = (v1, v3, v2): CCW edges = (v1,v3), (v3,v2), (v2,v1)
    In CCW traversal from the position where edge (v1,v2) = (v2,v1) was:
    the prevEdge of (v2,v1) in new t2 is (v3,v2) → that's the next-edge.
    Actually, "prev" in MeshFix means the preceding half-edge in CCW.
    For t2=(v1,v3,v2): edges in order = (v1,v3),(v3,v2),(v2,v1).
    If the swap created the edge (v2,v3) and the t2-side triangle sees this
    as e'=(v2,v3) traversed as (v3,v2) in the new t2=(v1,v3,v2):
      prevEdge of (v3,v2) in (v1,v3,v2) = (v2,v1)
      nextEdge of (v3,v2) in (v1,v3,v2) = (v1,v3)
    prevEdge from t2's perspective on the NEW edge = (v2,v1).

  Neighbor t3 shares edge (v2,v1) = canonical (v1,v2) with t0 (the large
  triangle) in the pre-swap mesh. Wait — t0=(v0,v1,v2) includes edge (v1,v2).
  So for a DIFFERENT neighbor geometry: we should place t3 to share the
  edge that would become the prev-edge of the post-swap t2.

  Cleaner approach: the prev-edge of t2 is the edge (v1,v2) (in t0's case,
  the edge adjacent to v1). Let t3 share edge (v1,v2) in the as-built mesh.
  v4=(2.5,2,0) — apex of t3 sharing edge (v1,v2) on the right side.

  t3=(v1,v2,v4): shares edge (v1,v2) with t0 (canonical (v1,v2)).

  For as-built assertions: primary overlap (t0,t1); topology showing
  (v1,v2) edge is shared (t0 and t3 share it).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me425",
    title="removeOverlappingTriangles SWAP_CREATES_T2_OVERLAP_PREV: swap creates new overlap on t2->prevEdge (Branch 6)",
    defect_class="overlapping_triangles",
)

# Core overlapping pair.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(1.5, 3.0, 0.0)   # 2 — apex of t0 (large triangle)
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — apex of t1; inside t0's area

# Neighbor triangle for the t2-prev-edge side effect.
# After swap: new t2-side triangle includes edge (v2,v1) = prev-edge of t2.
# t3 shares this edge with t0 in the pre-swap mesh.
v4 = m.vertex(2.5, 2.0, 0.0)   # 4 — apex of neighbor t3 sharing edge (v1,v2)

t0 = m.triangle(v0, v1, v2)    # 0: large triangle (one side of overlapping edge)
t1 = m.triangle(v0, v1, v3)    # 1: overlapping triangle; v3 inside t0
t3 = m.triangle(v1, v2, v4)    # 2: neighbor sharing t0's edge (v1,v2) = post-swap t2 prev-edge

# Shared overlapping edge: t0 and t1 share (v0,v1).
m.assert_edge_shared(v0, v1, 2)

# The post-swap t2's prev-edge (v1,v2) is already shared between t0 and t3.
m.assert_edge_shared(v1, v2, 2)

# Primary defect: t0 and t1 overlap.
m.assert_triangles_self_intersect(t0, t1)

# Coplanarity of the overlapping pair.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
