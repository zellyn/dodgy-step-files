"""Me422 — checkAndRepair::removeOverlappingTriangles branch 3: SWAP_CREATES_NEIGHBOR_OVERLAP_NEXT.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 3
(*SWAP_CREATES_NEIGHBOR_OVERLAP_NEXT*) @ line 1010:
  `else if (e->nextEdge(e)->overlaps())` — after swapping the overlapping edge,
  the *next* edge of t1 (the first incident triangle in MeshFix's half-edge
  structure) now overlaps a neighbor. The swap is immediately undone.

In MeshFix's half-edge structure, `nextEdge(e)` for t1 is the half-edge
following `e` around t1 in CCW order. After the swap, t1 is replaced by a
new triangle whose next-edge now sees a new neighbor — and that neighbor
creates an overlap with the post-swap triangle.

The fixture needs 3 triangles in the as-built mesh:
  - t0 and t1: the initial overlapping pair (coplanar, sharing edge e)
  - t2: neighbor sharing t1's next-edge; positioned so that after the swap
    the post-swap t1 overlaps t2.

The primary oracle-detectable defect is the overlap between t0 and t1.
The side-effect geometry is documented in the docstring and captured by
asserting the topology (edge sharing) that enables the branch.

Geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(3,0,0) — shared overlapping edge e=(v0,v1)
  v2=(1.5,3,0) — apex of t0 (large triangle)
  v3=(1.5,1,0) — apex of t1; inside t0 → overlap

  Pre-swap t1 = (v0, v1, v3); CCW next-edge of t1 after e=(v0,v1) is
  the edge (v1,v3). After the swap, e becomes (v2,v3) and:
    new t1 = (v0, v2, v3) with next-edge (v2,v3)→(v3,v0)
    new t2 = (v1, v3, v2) with next-edge (v3,v2)→(v2,v1)

  Neighbor triangle t2 shares edge (v1,v3) with pre-swap t1. We place its
  apex v4=(2,1,0) such that:
    - Pre-swap: t2=(v1,v3,v4)=(3,0)-(1.5,1)-(2,1) does NOT overlap t1
    - Post-swap: new t2=(v1,v3,v2)=(3,0)-(1.5,1)-(1.5,3), the next-edge
      of new t1=(v0,v2,v3) (edge (v3,v0)) would see the neighbor that was
      formerly t2's partner — creating overlap.

  For the as-built mesh assertions, we verify:
    1. t0 and t1 self-intersect (the primary defect)
    2. The shared edges show the topology correctly
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me422",
    title="removeOverlappingTriangles SWAP_CREATES_NEIGHBOR_OVERLAP_NEXT: swap creates new overlap on nextEdge(t1) (Branch 3)",
    defect_class="overlapping_triangles",
)

# Core overlapping pair.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(1.5, 3.0, 0.0)   # 2 — apex of t0 (large triangle)
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — apex of t1; inside t0's area

# Neighbor triangle sharing t1's next-edge (v1,v3).
# v4 positioned near (2,1) — between v1 and v3 direction but offset.
v4 = m.vertex(2.5, 1.0, 0.0)   # 4 — apex of neighbor t2; outside pre-swap overlap zone

t0 = m.triangle(v0, v1, v2)    # 0: large triangle (apex far above shared edge)
t1 = m.triangle(v0, v1, v3)    # 1: overlapping triangle; v3=(1.5,1) inside t0
t2 = m.triangle(v1, v3, v4)    # 2: neighbor sharing t1's next-edge (v1,v3)

# Shared overlapping edge: t0 and t1 share (v0,v1).
m.assert_edge_shared(v0, v1, 2)

# t1's next-edge (v1,v3) is shared with neighbor t2.
m.assert_edge_shared(v1, v3, 2)

# Primary defect: t0 and t1 overlap.
m.assert_triangles_self_intersect(t0, t1)

# Coplanarity of the overlapping pair.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
