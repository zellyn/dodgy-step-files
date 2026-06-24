"""Me424 — checkAndRepair::removeOverlappingTriangles branch 5: SWAP_CREATES_T2_OVERLAP_NEXT.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 5
(*SWAP_CREATES_T2_OVERLAP_NEXT*) @ line 1012:
  `else if (e->t2->nextEdge(e)->overlaps())` — after swapping, the *next* edge
  of t2 (the second incident triangle of the overlapping edge) overlaps a
  neighbor. The swap is undone.

This branch is symmetric to Branch 3 but checks the SECOND triangle of the
edge (t2) rather than the first (t1). In MeshFix's half-edge structure, t2
is the triangle on the opposite side of the half-edge from t1.

The fixture needs 3 triangles:
  - t0 and t1: the initial overlapping pair (coplanar, sharing edge e)
  - t3: neighbor sharing t2's next-edge; positioned so that the swap would
    cause the post-swap t2's next-edge to overlap t3.

Geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(3,0,0) — shared overlapping edge e=(v0,v1)
  v2=(1.5,3,0) — apex of t0 (t0 is the "t1" in MeshFix terms; large triangle)
  v3=(1.5,1,0) — apex of t1 (t1 is the "t2" in MeshFix terms; inside t0)

  In MeshFix, t2 = the triangle accessed via e->t2. For the half-edge e=(v0,v1)
  in t0=(v0,v1,v2), the "t2" is t0 itself (the triangle on the other side).
  Actually the labeling depends on which half-edge is considered canonical.

  To keep this clear: t0 is the larger triangle; t1 is the smaller overlapping
  one. The overlapping edge e has two incident triangles. After the swap:
    - new triangle A = (v0, v2, v3)  [from old t0's perspective]
    - new triangle B = (v1, v3, v2)  [from old t1's perspective]

  Branch 5 fires on the NEXT edge of the second incident triangle (t2 in
  MeshFix code). Let's make this the next-edge of new triangle B=(v1,v3,v2).
  CCW edges of B: (v1,v3), (v3,v2), (v2,v1).
  The swap replaces edge (v0,v1) so in B the "next" edge after the old
  position would be (v3,v2).

  Neighbor t3 shares edge (v3,v2) = canonical (v2,v3) with the would-be B.
  We place t3 such that after the swap, B and t3 overlap.

  v4=(2,2,0) — apex of neighbor t3; shares edge (v3,v2) with post-swap B.
  t3=(v2,v3,v4): shares edge (v2,v3) canonical.

  For as-built assertions: the primary overlap (t0,t1) and the topology
  showing t3 shares the edge (v2,v3) that would be the next-edge of
  post-swap t2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me424",
    title="removeOverlappingTriangles SWAP_CREATES_T2_OVERLAP_NEXT: swap creates new overlap on t2->nextEdge (Branch 5)",
    defect_class="overlapping_triangles",
)

# Core overlapping pair.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(1.5, 3.0, 0.0)   # 2 — apex of t0 (large triangle)
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — apex of t1; inside t0's area

# Neighbor triangle for the t2-next-edge side effect.
# After swap: new t2-side = (v1,v3,v2); next-edge (v3,v2) = canonical (v2,v3).
# t3 shares this edge; v4 placed above (v2,v3) segment.
v4 = m.vertex(2.0, 2.0, 0.0)   # 4 — apex of neighbor t3 sharing edge (v2,v3)

t0 = m.triangle(v0, v1, v2)    # 0: large triangle (the "t1" in MeshFix edge terms)
t1 = m.triangle(v0, v1, v3)    # 1: overlapping triangle; v3 inside t0
t3 = m.triangle(v2, v3, v4)    # 2: neighbor sharing post-swap t2's next-edge (v2,v3)

# Shared overlapping edge: t0 and t1 share (v0,v1).
m.assert_edge_shared(v0, v1, 2)

# The post-swap t2's next-edge (v2,v3) is already shared by t3 in the as-built mesh.
# No other triangle shares (v2,v3) in the pre-swap state.
m.assert_edge_shared(v2, v3, 1)

# Primary defect: t0 and t1 overlap.
m.assert_triangles_self_intersect(t0, t1)

# Coplanarity of the overlapping pair.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
