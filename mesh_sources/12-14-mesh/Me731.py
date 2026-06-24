"""Me731 — checkAndRepair::meshclean branch 2: INTERSECTION_REMOVAL_FAILURE.

Source method: MeshFix `checkAndRepair::meshclean` Branch 2 @ line 1047.
Branch condition: `strongIntersectionRemoval(inner_loops)` returns false —
the max-iteration limit is exceeded without eliminating all self-intersections.
The repair loop sets `ni = false`; convergence check proceeds with partial repair.

Defect pattern: two coplanar overlapping triangles create a self-intersection
that strongIntersectionRemoval cannot resolve because any local collapse
creates a new degenerate face — the overlapping pair cycles the repair
attempts until iteration budget is exhausted.

Geometry:
  Two triangles in the XY plane that overlap across a shared strip. Triangle
  t0 and t1 are not connected by a shared edge but their interiors cross —
  the classic stubborn SI configuration where neither can be collapsed without
  creating a new degenerate face.

  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0) — t0: left-leaning triangle
  v3=(1,0,0), v4=(3,0,0), v5=(2,2,0) — t1: right-leaning triangle (overlaps t0)

  t0 and t1 share the strip between X=1 and X=2, Y=0..overlap, creating
  a genuine crossing interior (self-intersection).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me731",
    title="meshclean INTERSECTION_REMOVAL_FAILURE: overlapping coplanar triangle pair resists strongIntersectionRemoval (branch 2)",
    defect_class="self_intersection",
)

# Triangle t0: occupies the region X in [0,2], pointed upward.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 2.0, 0.0)  # 2 — apex

# Triangle t1: shifted right, overlapping t0 in the central strip.
v3 = m.vertex(1.0, 0.0, 0.0)  # 3
v4 = m.vertex(3.0, 0.0, 0.0)  # 4
v5 = m.vertex(2.0, 2.0, 0.0)  # 5 — apex

# The two coplanar triangles — not connected (no shared edge).
t0 = m.triangle(v0, v1, v2)   # 0 — left triangle
t1 = m.triangle(v3, v4, v5)   # 1 — right triangle, overlaps t0

# Self-intersection: the two coplanar triangles cross in their interiors.
m.assert_triangles_self_intersect(t0, t1)

# No shared edge between the crossing pair (they are independent CC fragments).
m.assert_edge_shared(v0, v1, 1)  # boundary edge of t0
m.assert_edge_shared(v3, v4, 1)  # boundary edge of t1
