"""Me423 — checkAndRepair::removeOverlappingTriangles branch 4: SWAP_CREATES_NEIGHBOR_OVERLAP_PREV.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 4
(*SWAP_CREATES_NEIGHBOR_OVERLAP_PREV*) @ line 1011:
  `else if (e->prevEdge(e)->overlaps())` — after swapping the overlapping edge,
  the *previous* edge of t1 (the first incident triangle) overlaps a neighbor.
  The swap is undone.

In MeshFix's half-edge structure, `prevEdge(e)` for t1 is the half-edge
preceding `e` around t1 in CCW order. This is the edge leading INTO the
start vertex of `e` in t1's traversal. After the swap, t1 is replaced by a
new triangle whose prev-edge now neighbors a triangle that causes overlap.

Difference from Branch 3: Branch 3 checks `nextEdge(e)` (the edge following
the shared edge in t1); Branch 4 checks `prevEdge(e)` (the edge before the
shared edge in t1).

The fixture needs 3 triangles:
  - t0 and t1: the initial overlapping pair (coplanar, sharing edge e)
  - t2: neighbor sharing t1's prev-edge; positioned so the swap would
    cause the post-swap t1's prev-edge to overlap t2.

Geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(3,0,0) — shared overlapping edge e=(v0,v1)
  v2=(1.5,3,0) — apex of t0 (large triangle)
  v3=(1.5,1,0) — apex of t1; inside t0's area → overlap

  In CCW t1=(v0,v1,v3), the edges in order are:
    e=(v0,v1) — the overlapping shared edge
    nextEdge=(v1,v3) — covered by Me422's branch 3
    prevEdge=(v3,v0) — the edge covered by THIS branch (4)

  Neighbor triangle t2 shares edge (v3,v0) = (v0,v3) with t1.
  v4 positioned as apex of t2, on the left side of (v0,v3):
    v4=(-0.5,0.5,0) — to the left of segment v0-v3

  After the swap, e becomes (v2,v3) and:
    new t1 = (v0,v2,v3): CCW edges = (v0,v2),(v2,v3),(v3,v0)
    new t1's prev-edge is (v3,v0), same edge as before.
    The new triangle (v0,v2,v3) with the same neighbor t2=(v0,v3,v4).
    Since the post-swap t1 has different shape, overlap with t2 may be created.

  For as-built oracle assertions: assert primary overlap (t0,t1) and topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me423",
    title="removeOverlappingTriangles SWAP_CREATES_NEIGHBOR_OVERLAP_PREV: swap creates new overlap on prevEdge(t1) (Branch 4)",
    defect_class="overlapping_triangles",
)

# Core overlapping pair.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(1.5, 3.0, 0.0)   # 2 — apex of t0 (large triangle)
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — apex of t1; inside t0's area

# Neighbor triangle sharing t1's prev-edge (v3,v0) = edge (v0,v3).
# v4 placed to the left of segment v0→v3 to make a valid triangle.
v4 = m.vertex(-0.5, 0.5, 0.0)  # 4 — apex of neighbor t2 (left of v0-v3 segment)

t0 = m.triangle(v0, v1, v2)    # 0: large triangle (apex far above)
t1 = m.triangle(v0, v1, v3)    # 1: overlapping triangle; v3 inside t0
t2 = m.triangle(v3, v0, v4)    # 2: neighbor sharing prev-edge (v3,v0) of t1

# Shared overlapping edge: t0 and t1 share (v0,v1).
m.assert_edge_shared(v0, v1, 2)

# t1's prev-edge (v3,v0) = canonical (v0,v3) is shared with neighbor t2.
m.assert_edge_shared(v0, v3, 2)

# Primary defect: t0 and t1 overlap.
m.assert_triangles_self_intersect(t0, t1)

# Coplanarity of the overlapping pair.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
