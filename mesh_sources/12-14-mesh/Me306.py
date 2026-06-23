"""Me306 — retriangulateSelectedRegion_vertex_list_extraction: second element is internal vertex list.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 7 (*vertex_list_extraction*) @ line 982:
  `vl = ((List *)ms->head()->next()->data)` — the second element of the region's
  topology list `ms` is a List of internal (Steiner) vertices. These vertices were
  interior to the selected region before unlinking, and will be re-inserted into
  the new triangulation by `TriangulateHole(e, vl)`.

This branch exercises the case where the region had at least one internal vertex
that is not on the boundary. After the selected triangles are unlinked, this vertex
becomes a "floating" Steiner point referenced in `vl`.

Defect carrier: a pentagonal hole mesh where one Steiner point vs is interior
to the original selected region. After unlinking, vs is referenced by `vl`
(the vertex list) for use in Delaunay triangulation.

Geometry: hole with 4 boundary vertices and 1 Steiner point that was inside.
  Hole boundary: v0, v1, v2, v3 (quadrilateral)
  Steiner point: vs = (1.5, 1.5, 0) — was interior to the selected region
  Frame triangles surround the hole.

The Steiner point vs is geometrically inside the hole boundary rectangle,
confirming it's an internal vertex for re-triangulation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me306",
    title="retriangulateSelectedRegion_vertex_list_extraction: vl = internal vertex list (Branch 7)",
    defect_class="retriangulate_region_steiner_vertex",
)

# Hole boundary vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(3.0, 3.0, 0.0)   # 2
v3 = m.vertex(0.0, 3.0, 0.0)   # 3

# Steiner point — was internal vertex of selected region; now in vl.
vs = m.vertex(1.5, 1.5, 0.0)   # 4 — internal vertex, vl->head()->data

# Frame vertices.
vo0 = m.vertex(1.5, -2.0, 0.0)   # 5
vo1 = m.vertex(5.0, 1.5, 0.0)    # 6
vo2 = m.vertex(1.5, 5.0, 0.0)    # 7
vo3 = m.vertex(-2.0, 1.5, 0.0)   # 8

# Frame triangles (these were not selected; they remain in the mesh).
t0 = m.triangle(v0, v1, vo0)    # 0
t1 = m.triangle(v1, v2, vo1)    # 1
t2 = m.triangle(v2, v3, vo2)    # 2
t3 = m.triangle(v3, v0, vo3)    # 3

# The Steiner vertex vs is isolated — unreferenced by any remaining triangle,
# confirming it was inside the selected region that was unlinked.
m.assert_isolated_vertex(vs)

# Hole boundary is intact.
m.assert_hole_boundary([v0, v1, v2, v3])
m.assert_edge_shared(v0, v1, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary
m.assert_edge_shared(v3, v0, 1)   # boundary
