"""Me421 — checkAndRepair::removeOverlappingTriangles branch 2: SWAP_CREATES_DEGENERACY.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 2
(*SWAP_CREATES_DEGENERACY*) @ line 1009:
  `else if (e->t1->isExactlyDegenerate() || e->t2->isExactlyDegenerate())`
  — after swap, one of the two new triangles is exactly degenerate (zero area).
  The swap is undone with `e->swap(1)` (fast undo). This branch fires because
  the post-swap triangle has all three vertices collinear.

Geometry setup: two coplanar triangles sharing edge (v0,v1) that overlap.
After the swap, the replacement edge would be (v2,v3) — but v2 and v3 are
collinear with one of the original vertices, making a post-swap triangle
degenerate.

Specifically: v2=(0,2,0), v3=(1,0,0) is placed collinear with v0=(0,0,0)
and v1=(2,0,0) (both on the x-axis? No: v3=(1,0,0) sits on segment v0-v1,
making the post-swap triangle (v0,v2,v3) degenerate if v3 is on edge v0-v1).

Re-design: place v3 exactly on the line from v0 to v1 (the shared edge).
v0=(0,0,0), v1=(3,0,0), v3=(1.5,0,0) — midpoint of shared edge.
t0=(v0,v1,v2) with v2=(1.5,2,0); t1=(v0,v1,v3) with v3=(1.5,0,0) on edge.

t1 itself is degenerate (v3 on v0-v1) and overlaps t0. The swap would
produce t_new1=(v0,v2,v3)=(v0=(0,0,0), v2=(1.5,2,0), v3=(1.5,0,0)) —
valid — and t_new2=(v1,v3,v2)=(v1=(3,0,0), v3=(1.5,0,0), v2=(1.5,2,0))
— also valid. But actually we want the post-swap triangle to be degenerate.

Better design: place v2 and v3 such that after the swap (edge becomes v2-v3),
the new triangle (v0,v2,v3) has zero area because v0, v2, v3 are collinear.

v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(3,1,0):
  t0=(v0,v1,v2): vertices (0,0),(2,0),(1,1) — valid area
  t1=(v0,v1,v3): vertices (0,0),(2,0),(3,1) — overlapping with t0? Let's check.

Actually for overlap: t1's apex v3 must be inside t0's area. (3,1) is outside t0.

Simplest approach: use 3 triangles to create the side-effect degeneracy.
The overlapping pair is t0 and t1 sharing edge (v0,v1). A third vertex v4
sits colinear with v2 and v3 (the non-shared vertices) so the post-swap
triangle becomes degenerate.

Concrete geometry (all in XY plane, z=0):
  v0=(0,0,0), v1=(2,0,0) — shared edge
  v2=(1,2,0) — apex of t0 (large triangle)
  v3=(1,1,0) — apex of t1 (inside t0, coplanar; overlapping)

After swap: edge becomes (v2,v3)=(1,2)-(1,1) — both at x=1.
  New triangle A = (v0,v2,v3) = (0,0)-(1,2)-(1,1): area = 0.5 * |det| = 0.5*|1*1-1*2|=0.5 ≠ 0
  New triangle B = (v1,v3,v2) = (2,0)-(1,1)-(1,2): area = 0.5*|1*2-1*1|... not degenerate.

To make a post-swap triangle degenerate, we need v0, v2, v3 collinear:
  If v2=(0,2,0) and v3=(0,1,0), then (v0=(0,0), v2=(0,2), v3=(0,1)) are all on x=0 → collinear!
  Check overlap: t0=(v0,v1,v2)=(0,0)-(2,0)-(0,2); t1=(v0,v1,v3)=(0,0)-(2,0)-(0,1)
  t1's apex v3=(0,1) is inside t0's triangle? t0 has vertices (0,0),(2,0),(0,2).
  Point (0,1): on the edge from (0,0) to (0,2) — actually ON the boundary of t0.
  That's degenerate overlap. Let's use v3=(0.1,0.8,0) — not collinear with v0,v2 for the pre-swap.

Actually: we want the PRE-swap triangles to overlap (t0,t1 are the overlapping pair),
and the POST-swap result to have a degenerate triangle.

Let v2=(0,2,0) and v3=(0,1,0):
  Pre-swap: t0=(v0,v1,v2), t1=(v0,v1,v3)
  - v3=(0,1) is on edge v0-v2 (x=0 line) → inside t0?
    Barycentric check for (0,1) in triangle (0,0)-(2,0)-(0,2):
    lambda1=1-0/2-1/2=1-0-0.5=0.5, lambda2=0, lambda3=0.5 → yes, inside t0.
  Post-swap edge becomes (v2,v3)=(0,2)-(0,1). Both at x=0.
  New triangles: A=(v0,v2,v3)=(0,0)-(0,2)-(0,1) → collinear! Area=0. DEGENERATE ✓
  New triangle B=(v1,v3,v2)=(2,0)-(0,1)-(0,2) → area>0. OK.

So the post-swap produces one degenerate triangle → Branch 2 fires.

Final geometry:
  v0=(0,0,0), v1=(2,0,0) — shared edge (overlapping)
  v2=(0,2,0) — apex of t0; lies on y-axis
  v3=(0,1,0) — apex of t1; inside t0 AND collinear with v0 and v2 (x=0 line)
  t0=(v0,v1,v2): large triangle
  t1=(v0,v1,v3): smaller coplanar triangle; v3 inside t0 → overlap

Post-swap: (v2,v3) new edge; triangle (v0,v2,v3) is degenerate (collinear on x=0).
Branch 2 fires: `e->t1->isExactlyDegenerate()` → undo swap.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me421",
    title="removeOverlappingTriangles SWAP_CREATES_DEGENERACY: post-swap triangle degenerate; undo swap (Branch 2)",
    defect_class="overlapping_triangles",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start (on y-axis)
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(0.0, 2.0, 0.0)   # 2 — apex of t0; on y-axis (x=0)
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — apex of t1; collinear with v0,v2 (all x=0)

t0 = m.triangle(v0, v1, v2)    # 0: large triangle; apex at (0,2,0)
t1 = m.triangle(v0, v1, v3)    # 1: small triangle; apex v3=(0,1,0) inside t0

# Shared overlapping edge (v0,v1).
m.assert_edge_shared(v0, v1, 2)

# The two coplanar triangles overlap.
m.assert_triangles_self_intersect(t0, t1)

# Post-swap triangle (v0,v2,v3) = (0,0,0)-(0,2,0)-(0,1,0) is degenerate:
# all three vertices have x=0 → collinear → zero area.
# Assert the area of this would-be triangle is zero by checking v0,v2,v3 collinear:
# vertex_on_edge(v3, v0, v2): v3=(0,1) lies on segment v0=(0,0) to v2=(0,2).
m.assert_vertex_on_edge(v3, v0, v2)

# Coplanarity of t0 and t1.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
