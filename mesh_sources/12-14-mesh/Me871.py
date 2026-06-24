"""Me871 — selectIntersectingTriangles cell-saturation threshold: DI_MAX_NUMBER_OF_CELLS
exceeded or tris-per-cell density limit triggers subdivision (Branch 2).

MeshFix `Basic_TMesh.selectIntersectingTriangles` Branch 2 (*Cell-saturation threshold*) @ line 167:
  'if (n_cells > DI_MAX_NUMBER_OF_CELLS || tris_per_cell > DI_MAX_TRIS_PER_CELL) { subdivide }'
  — when a spatial-partition cell contains more triangles than the per-cell density
  threshold (DI_MAX_TRIS_PER_CELL) OR the total cell count would exceed
  DI_MAX_NUMBER_OF_CELLS, the partitioner subdivides the cell rather than using it
  directly for intersection tests.

This fixture presents a dense cluster of triangles whose bounding boxes all
overlap in a very small region, forcing the spatial partitioner to create a
saturated cell. The cluster contains more triangles than DI_MAX_TRIS_PER_CELL
(typically 10–20 in MeshFix defaults), so the cell-saturation check fires and
the cell is queued for subdivision. A self-intersecting pair is embedded in the
cluster so the fixture carries genuine defect geometry.

Defect pattern: 'DI_MAX_NUMBER_OF_CELLS', 'tris_per_cell' — dense triangle
  clustering in one bounding-box region forces the cell-saturation branch.

Geometry:
  Tight cluster: 15 thin radial triangles all sharing the origin as apex, with
  outer vertices packed in a 0.1-radius disk in the XY plane (dense overlapping
  bounding boxes). A crossing pair (t0, t1) produces the SI defect. The remaining
  13 triangles fan around the origin within the same tiny bbox region.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(
    catalog_id="Me871",
    title="selectIntersectingTriangles cell-saturation: 15-triangle dense cluster forces DI_MAX_TRIS_PER_CELL subdivision; embedded SI pair (Branch 2)",
    defect_class="self_intersection_face_pair",
)

# Shared apex at origin.
apex = m.vertex(0.0, 0.0, 0.0)  # 0

# 15 outer vertices packed in a tiny 0.1-radius circle — all bounding boxes
# heavily overlap, saturating a single spatial cell.
N = 15
outer = []
for i in range(N):
    angle = 2.0 * math.pi * i / N
    x = 0.1 * math.cos(angle)
    y = 0.1 * math.sin(angle)
    outer.append(m.vertex(x, y, 0.0))

# One extra vertex lifted in Z to create the crossing triangle (SI pair).
# v_up at (0.05, 0.0, 0.1) — inside the cluster's XY footprint but above it.
v_up = m.vertex(0.05, 0.0, 0.1)   # 16

# Triangle list: 15 flat radial triangles in XY plane + 1 crossing triangle.
# t0: flat triangle (apex, outer[0], outer[1]) — in XY plane.
# t_cross: oblique triangle (apex, outer[0], v_up) — crosses the XY plane cluster.
tris = []
for i in range(N):
    j = (i + 1) % N
    tris.append(m.triangle(apex, outer[i], outer[j]))

# Crossing triangle sharing apex and outer[0] but rising in Z.
t_cross = m.triangle(apex, outer[0], v_up)

# The crossing triangle pierces through the flat fan.
# t0 (flat, in XY) and t_cross (oblique, rising in Z) intersect near outer[0].
m.assert_triangles_self_intersect(tris[0], t_cross)

# Adjacent flat triangles share edges but do not geometrically intersect.
m.assert_triangles_do_not_intersect(tris[1], tris[2])
