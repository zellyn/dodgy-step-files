"""Me426 — checkAndRepair::removeOverlappingTriangles branch 7: UNRESOLVABLE_OVERLAP.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 7
(*UNRESOLVABLE_OVERLAP*) @ line 1021:
  `unlinkTriangle(t1); unlinkTriangle(t2); nr++;` — the overlapping edge could
  not be resolved by swapping (all swap attempts either failed to fix the
  overlap or created new problems). Both incident triangles are unlinked
  (removed from the mesh) and the removed-triangle counter is incremented.

This branch fires when:
  1. `e->swap()` fails (returns non-zero), OR
  2. After swap, one of branches 2-6 fires (side-effect detected and swap
     undone), AND the edge STILL overlaps after the undo.

The fixture models a degenerate overlapping configuration where a successful
swap is impossible or always creates cascading problems — representing the
"no clean resolution" state. The simplest such configuration is two coplanar
triangles with heavily nested overlap where the would-be swap vertices are
arranged to keep the overlap no matter what.

Specifically: three triangles forming a "nested" coplanar stack where:
  - t0 and t1 overlap via shared edge e=(v0,v1)
  - t1 and t2 also overlap via shared edge e'=(v0,v2)
  - The arrangement is such that swapping e always introduces the t1-t2 overlap
    as a new problem, and after undoing the swap, e still satisfies `overlaps()`

Geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(4,0,0) — shared overlapping edge e=(v0,v1)
  v2=(2,4,0) — apex of t0 (large outer triangle)
  v3=(2,2,0) — apex of t1; inside t0's area → t0-t1 overlap

  t0=(v0,v1,v2): large triangle covering (0,0)-(4,0)-(2,4)
  t1=(v0,v1,v3): medium triangle; v3=(2,2) inside t0 → overlap

  Additionally: t1 itself has a second overlap with a third triangle t2.
  Placing v4=(2,3,0) as apex of t2=(v0,v2,v4):
    t2 shares edge (v0,v2) with t0; v4=(2,3) inside t0's area → t0-t2 overlap.

  The unresolvable configuration: t0 overlaps t1 via (v0,v1), AND t0 overlaps
  t2 via (v0,v2). Whichever overlap we try to resolve by swapping, the other
  overlap persists. The healer must unlink both triangles of the first
  overlapping pair.

  For the as-built mesh: two self-intersecting pairs (t0,t1) and (t0,t2),
  both via coplanar overlapping.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me426",
    title="removeOverlappingTriangles UNRESOLVABLE_OVERLAP: multi-overlap tangle; both triangles unlinked (Branch 7)",
    defect_class="overlapping_triangles",
)

# Central large triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge base-left
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — shared edge base-right
v2 = m.vertex(2.0, 4.0, 0.0)   # 2 — apex of large outer triangle t0

# Interior overlapping triangles.
v3 = m.vertex(2.0, 2.0, 0.0)   # 3 — apex of t1; inside t0 via edge (v0,v1)
v4 = m.vertex(2.0, 3.0, 0.0)   # 4 — apex of t2; inside t0 via edge (v0,v2)

t0 = m.triangle(v0, v1, v2)    # 0: large outer triangle; normal +Z (CCW)
t1 = m.triangle(v0, v1, v3)    # 1: coplanar; v3 inside t0 → overlap via (v0,v1)
t2 = m.triangle(v0, v4, v2)    # 2: coplanar CCW; v4 inside t0 → overlap via (v0,v2)

# Two overlapping shared edges.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1 (first overlapping pair)
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t2 (second overlapping pair)

# Both pairs self-intersect (coplanar overlap).
m.assert_triangles_self_intersect(t0, t1)
m.assert_triangles_self_intersect(t0, t2)

# Coplanarity: all three triangles in the XY plane.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
m.assert_adjacent_triangles_normal_dot_gt(t0, t2, 0.99)
