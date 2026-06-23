"""Me300 — retriangulateSelectedRegion_insufficient_triangles: region has fewer than 2 triangles, abort.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 1 (*insufficient_triangles*) @ line 959:
  `if (ttbr.numels() < 2) { ... return; }` — the selected region has fewer than
  2 triangles, so retriangulation is aborted with a warning.

The retriangulation algorithm requires at least 2 triangles to define a region
with a meaningful boundary loop. A single-triangle "region" cannot be
re-triangulated — its boundary is the triangle itself and there is nothing to
improve.

Defect carrier: a mesh with one selected triangle (the "region") plus two
boundary triangles. The marked region contains only 1 triangle (< 2), so
`retriangulateSelectedRegion` aborts immediately.

Geometry (flat XY plane):
  t0 = (v0, v1, v2) — the single selected region triangle
  t1 = (v1, v3, v2) — adjacent mesh triangle (not in selection)
  t2 = (v0, v2, v4) — adjacent mesh triangle (not in selection)

The region's trivially-small size (1 triangle) is the defect condition.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me300",
    title="retriangulateSelectedRegion_insufficient_triangles: region < 2 triangles, abort (Branch 1)",
    defect_class="retriangulate_region_trivial",
)

# Vertices of a minimal mesh with a 1-triangle "selected region".
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(3.0, 2.0, 0.0)   # 3
v4 = m.vertex(-1.0, 2.0, 0.0)  # 4

# Triangle 0: the single "selected region" triangle (ttbr.numels() == 1 < 2).
t0 = m.triangle(v0, v1, v2)   # 0 — the sole selected region member
# Adjacent triangles (not selected).
t1 = m.triangle(v1, v3, v2)   # 1
t2 = m.triangle(v0, v2, v4)   # 2

# The selected triangle t0 has boundary edges (incident on exactly 1 triangle each).
# These confirm the region boundary; since there is only 1 region triangle,
# retriangulateSelectedRegion fires the < 2 guard.
m.assert_edge_shared(v0, v1, 1)   # boundary edge — not shared with any other triangle
m.assert_edge_shared(v1, v2, 2)   # interior: shared by t0 and t1
m.assert_edge_shared(v0, v2, 2)   # interior: shared by t0 and t2

# Triangle areas are non-degenerate (the abort is due to count, not geometry).
m.assert_triangle_area_lt(t0, 5.0)   # t0 area = 2.0 — finite, non-zero
