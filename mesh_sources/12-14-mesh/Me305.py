"""Me305 — retriangulateSelectedRegion_boundary_edge_extraction: first element is boundary edge of region.

MeshFix `Basic_TMesh.retriangulateSelectedRegion` Branch 6 (*boundary_edge_extraction*) @ line 981:
  `e = ((Edge *)ms->head()->data)` — the first element of the region's topology
  list `ms` is the boundary edge of the region. This edge serves as the starting
  point for `TriangulateHole`.

After unlinking the selected triangles, the region topology `ms` is a List whose
first element is an Edge on the boundary of the hole. Branch 6 captures the moment
this boundary edge is retrieved to drive the hole-fill algorithm.

Defect carrier: a mesh with a quadrilateral hole (4 boundary edges), representing
a simple region whose boundary was extracted. The boundary edge (v0, v1) is the
starting edge for TriangulateHole.

Geometry (flat XY plane):
  Hole boundary: v0=(0,0,0), v1=(3,0,0), v2=(3,3,0), v3=(0,3,0)
  Frame triangles surround the hole.
  The boundary edge e = (v0, v1) is the `ms->head()` item — start of TriangulateHole.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me305",
    title="retriangulateSelectedRegion_boundary_edge_extraction: boundary edge e = ms->head() (Branch 6)",
    defect_class="retriangulate_region_boundary_edge",
)

# Hole boundary vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — start of boundary edge e
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — end of boundary edge e
v2 = m.vertex(3.0, 3.0, 0.0)   # 2
v3 = m.vertex(0.0, 3.0, 0.0)   # 3

# Outer frame vertices.
vo0 = m.vertex(1.5, -2.0, 0.0)   # 4 — bottom frame apex
vo1 = m.vertex(5.0, 1.5, 0.0)    # 5 — right frame apex
vo2 = m.vertex(1.5, 5.0, 0.0)    # 6 — top frame apex
vo3 = m.vertex(-2.0, 1.5, 0.0)   # 7 — left frame apex

# Frame triangles surrounding the quadrilateral hole.
t0 = m.triangle(v0, v1, vo0)    # 0 — bottom frame
t1 = m.triangle(v1, v2, vo1)    # 1 — right frame
t2 = m.triangle(v2, v3, vo2)    # 2 — top frame
t3 = m.triangle(v3, v0, vo3)    # 3 — left frame

# The hole boundary loop: all 4 inner edges are incident on exactly 1 triangle.
# The first of these, (v0, v1), is `e = ms->head()->data` — the boundary edge
# that TriangulateHole uses as its starting point.
m.assert_hole_boundary([v0, v1, v2, v3])

# Confirm boundary edge (v0, v1) is incident on exactly 1 frame triangle.
m.assert_edge_shared(v0, v1, 1)   # boundary edge e = ms->head()
m.assert_edge_shared(v1, v2, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary
m.assert_edge_shared(v3, v0, 1)   # boundary
