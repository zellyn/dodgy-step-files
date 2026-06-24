"""Me653 — Basic_TMesh.removeEdges edge_removal: E.removeCell + delete e removes orphaned edge (Branch 4).

MeshFix `Basic_TMesh.removeEdges` Branch 4 (*edge_removal*) @ line 587:
  'E.removeCell(e); delete e;' — once an edge is flagged (v1==NULL or v2==NULL),
  it is unlinked from the doubly-linked edge list via removeCell and then freed.
  This branch represents the actual deletion step; the traversal advances via
  the already-saved next-pointer 'n' so the walk continues after removal.

Geometric proxy: the to-be-removed edge is modelled as a fully-collapsed
  degenerate triangle where BOTH endpoints of the critical edge coincide —
  the edge (v0, v1) has zero length because v0==v1. This makes the triangle
  area zero and the edge itself a zero-span segment, capturing the structural
  situation where E.removeCell would excise such an edge from the list.

Geometry:
  v0 = (1, 1, 0)  — base coordinate (shared with v1)
  v1 = (1, 1, 0)  — coincident with v0 (orphaned-edge endpoint)
  v2 = (3, 0, 0)
  v3 = (3, 2, 0)
  v4 = (5, 1, 0)
  t0 = (v0, v1, v2)   — degenerate (v0==v1): contains the orphaned edge
  t1 = (v2, v3, v4)   — well-formed (distant, separate mesh region)
  t2 = (v2, v4, v0)   — well-formed connector triangle
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me653",
    title="removeEdges edge_removal: zero-length edge (v0==v1 at (1,1,0)) in degenerate triangle; E.removeCell+delete path (Branch 4)",
    defect_class="orphaned_edge",
)

v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — coincident with v1 (orphaned-edge endpoint a)
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — coincident with v0 (orphaned-edge endpoint b)
v2 = m.vertex(3.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 2.0, 0.0)   # 3
v4 = m.vertex(5.0, 1.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: v0==v1 → zero-length orphaned edge
t1 = m.triangle(v2, v3, v4)    # 1 — well-formed triangle
t2 = m.triangle(v2, v4, v0)    # 2 — well-formed connector

# v0 and v1 are coincident: the zero-length edge that E.removeCell will excise.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# Triangle t0 has zero area (two coincident vertices).
m.assert_triangle_area_lt(t0, 1e-9)

# Interior edges of the well-formed region.
m.assert_edge_shared(v2, v4, 2)   # shared by t1 and t2

# Collapsed edge in t0 — boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
