"""Me420 — checkAndRepair::removeOverlappingTriangles branch 1: OVERLAPPING_EDGE_SWAPPABLE.

MeshFix `checkAndRepair::removeOverlappingTriangles` Branch 1
(*OVERLAPPING_EDGE_SWAPPABLE*) @ line 1007:
  `if (!e->swap()) { ... }` — the swap attempt succeeds immediately and the
  overlapping edge is resolved. No post-swap checks are needed because
  `swap()` returns 0 (success). The repaired edge now has its two incident
  triangles arranged non-coplanarly (or at least non-overlappingly).

The fixture models the minimal overlapping-triangle configuration: two
coplanar triangles in the XY plane sharing edge (v0, v1). Triangle t0 has
apex v2=(0,2,0) and triangle t1 has apex v3=(1,1,0) which lies strictly
inside t0's area. The shared edge (v0,v1) is the overlapping edge detected
by `e->overlaps()`.

An edge swap would replace the shared edge (v0,v1) with the diagonal (v2,v3),
producing triangles (v0,v2,v3) and (v1,v3,v2). Since v3 is inside the
original triangle t0, the swap produces non-overlapping triangles — Branch 1
fires (swap succeeds).

Geometry:
  v0=(0,0,0), v1=(2,0,0) — shared edge
  v2=(0,2,0) — apex of t0 (large coplanar triangle)
  v3=(1,1,0) — apex of t1 (inside t0's area; coplanar)
  t0=(v0,v1,v2): large triangle
  t1=(v0,v1,v3): smaller coplanar triangle; interior overlaps t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me420",
    title="removeOverlappingTriangles OVERLAPPING_EDGE_SWAPPABLE: two coplanar triangles, shared edge swappable (Branch 1)",
    defect_class="overlapping_triangles",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — shared edge start
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — shared edge end
v2 = m.vertex(0.0, 2.0, 0.0)   # 2 — apex of large triangle t0
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — apex of t1; inside t0's area (coplanar)

t0 = m.triangle(v0, v1, v2)    # 0: large coplanar triangle
t1 = m.triangle(v0, v1, v3)    # 1: smaller coplanar triangle sharing edge (v0,v1)

# Shared edge (v0,v1) is incident on exactly 2 triangles (the overlapping pair).
m.assert_edge_shared(v0, v1, 2)

# Both triangles are coplanar and their interiors overlap (self-intersection).
m.assert_triangles_self_intersect(t0, t1)

# After swap, (v0,v1) becomes (v2,v3); each new triangle occupies a non-overlapping region.
# The adjacent_triangles_normal_dot_gt confirms coplanarity (dot product near 1.0).
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
