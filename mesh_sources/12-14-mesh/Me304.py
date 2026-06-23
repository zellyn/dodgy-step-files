"""Me304 — retriangulateSelectedRegion_triangle_unlink: selected triangles removed before re-triangulation.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 5 (*triangle_unlink*) @ line 980:
  `FOREACHVTTRIANGLE((&ttbr), u, n) unlinkTriangle(u);` — each triangle in the
  selected region is unlinked (removed) from the mesh data structure in preparation
  for re-triangulation. After unlinking, the region boundary becomes an open hole
  ready for hole-filling.

The defect carrier shows the post-unlink state: the selected region triangles have
been removed, leaving a hole in the mesh bounded by edges each incident on exactly
1 triangle (boundary). The remaining triangles form the "frame" around the hole.

Geometry: six triangles arranged as a hexagonal ring around a central hole.
The ring's inner edges are all boundary (n=1) after the center triangles
were unlinked. This represents the mesh just after `unlinkTriangle` runs on
each selected triangle.

Vertices: outer hexagon + two center triangles, after unlink → hole.

We model the post-unlink state directly:
  Outer triangles t0..t5 remain; inner triangles (forming the central hole)
  have been removed. The inner boundary loop (v0..v2) is the hole boundary.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me304",
    title="retriangulateSelectedRegion_triangle_unlink: selected triangles unlinked, hole exposed (Branch 5)",
    defect_class="retriangulate_region_unlinked",
)

# Six vertices forming a triangle + outer ring.
# After unlinking, the inner 2 triangles (the selected region) are gone.
# We model the remaining mesh: 3 outer triangles sharing the inner boundary.

# Inner triangle boundary (the hole that was left after unlinking).
vi0 = m.vertex(0.0, 0.0, 0.0)   # 0 — inner boundary vertex
vi1 = m.vertex(2.0, 0.0, 0.0)   # 1 — inner boundary vertex
vi2 = m.vertex(1.0, 2.0, 0.0)   # 2 — inner boundary vertex

# Outer vertices.
vo0 = m.vertex(-1.0, -1.0, 0.0)   # 3
vo1 = m.vertex(3.0, -1.0, 0.0)    # 4
vo2 = m.vertex(1.0, 4.0, 0.0)     # 5

# Three outer triangles that frame the hole.
t0 = m.triangle(vo0, vi1, vi0)   # 0 — bottom-left frame
t1 = m.triangle(vo0, vo1, vi1)   # 1 — bottom frame
t2 = m.triangle(vo1, vi2, vi1)   # 2 — bottom-right frame
t3 = m.triangle(vo1, vo2, vi2)   # 3 — right frame
t4 = m.triangle(vo2, vi0, vi2)   # 4 — top frame
t5 = m.triangle(vo2, vo0, vi0)   # 5 — left frame

# Inner boundary: each hole edge is incident on exactly 1 triangle.
# This is the key post-unlink condition: the selected triangles have been removed,
# leaving a triangular hole with 3 boundary edges.
m.assert_hole_boundary([vi0, vi1, vi2])

# Outer boundary edges (connecting outer vertices) are each incident on 1 triangle.
m.assert_edge_shared(vo0, vo1, 1)   # outer boundary
m.assert_edge_shared(vo1, vo2, 1)   # outer boundary
m.assert_edge_shared(vo0, vo2, 1)   # outer boundary
