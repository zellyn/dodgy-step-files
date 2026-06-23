"""Me302 — retriangulateSelectedRegion_non_simple_selection: selection is topologically non-simple, abort.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 3 (*non_simple_selection*) @ line 972:
  `if (!isSelectionSimple()) { ... return; }` — the selected region forms a
  topologically non-simple polygon (e.g. has a hole, or is multiply-connected).
  Retriangulation requires a simple (disk-topology) region; the algorithm aborts.

A region is non-simple if its boundary forms more than one closed loop —
for example, a ring-shaped selection with a hole in the middle, or two
disconnected triangle groups both marked as selected. `isSelectionSimple`
returns false in this case.

Defect carrier: six triangles arranged as two separate groups (two disjoint
triangular patches, both "selected"). The selection boundary has two disconnected
loops — the outer boundary of patch A and the outer boundary of patch B —
so `isSelectionSimple` returns false.

Geometry (flat XY plane, two separate triangles far apart):
  Patch A: t0=(v0,v1,v2) — left triangle, isolated (all edges boundary n=1)
  Patch B: t1=(v3,v4,v5) — right triangle, isolated (all edges boundary n=1)

Both are in the "selected" region. The selection boundary has two disjoint
loops → non-simple → Branch 3 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me302",
    title="retriangulateSelectedRegion_non_simple_selection: two disconnected selected patches, abort (Branch 3)",
    defect_class="retriangulate_region_non_simple",
)

# Patch A — left triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Patch B — right triangle, completely disjoint from Patch A.
v3 = m.vertex(5.0, 0.0, 0.0)   # 3
v4 = m.vertex(6.0, 0.0, 0.0)   # 4
v5 = m.vertex(5.5, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — Patch A: isolated triangle
t1 = m.triangle(v3, v4, v5)   # 1 — Patch B: isolated triangle

# All edges of both triangles are boundary (n=1): confirming two separate patches.
m.assert_edge_shared(v0, v1, 1)   # Patch A boundary
m.assert_edge_shared(v1, v2, 1)   # Patch A boundary
m.assert_edge_shared(v0, v2, 1)   # Patch A boundary
m.assert_edge_shared(v3, v4, 1)   # Patch B boundary
m.assert_edge_shared(v4, v5, 1)   # Patch B boundary
m.assert_edge_shared(v3, v5, 1)   # Patch B boundary

# t0 and t1 are unreachable from each other (disconnected components).
# This confirms the non-simple / multiply-connected topology of the selection.
m.assert_triangle_not_reachable_from(target=t1, source=t0)
