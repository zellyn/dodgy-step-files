"""Me049 — compatible_orientations: boundary halfedge traversal (next_on_border).

Catalog claim: a mesh has a genuine boundary (open boundary loop) and the orientation
algorithm must correctly advance along the boundary cycle using next_on_border logic.
CGAL PMP.compatible_orientations Branch 4 @ line 1310 (*boundary_cycle_traversal*)
fires when the BFS encounters a halfedge on the mesh boundary: it calls
advance_halfedge / next_on_border to walk the boundary ring before continuing
orientation propagation on the opposite side.

Defect carrier: a U-shaped open mesh. Three triangles (0, 1, 2) form a connected
patch with an open boundary loop on three sides. Every boundary edge is incident on
exactly 1 triangle. The interior shared edges are manifold (shared by 2). The boundary
loop is: v0-v1-v2-v5-v4-v3-v0.

Layout (flat XY quad strip with centre triangle removed, leaving a U shape):
  v0=(0,0,0) v1=(1,0,0) v2=(2,0,0)
  v3=(0,1,0) v4=(1,1,0) v5=(2,1,0)
  tri0=(v0,v1,v3): left triangle
  tri1=(v1,v2,v5): right triangle
  tri2=(v1,v5,v4): top-right connector
  (the centre triangle (v1,v4,v3) is absent — creates the boundary)

The boundary loop (all boundary edges incident on exactly 1 triangle):
  v0-v1 (tri0), v1-v2 (tri1), v2-v5 (tri1), v5-v4 (tri2), v4-v1 (tri2), v1-v3 (???)

Let me recompute. Triangles:
  tri0: (v0,v1,v3)  edges: (v0,v1), (v1,v3), (v3,v0)
  tri1: (v1,v2,v5)  edges: (v1,v2), (v2,v5), (v5,v1)
  tri2: (v1,v5,v4)  edges: (v1,v5), (v5,v4), (v4,v1)

Shared edges: (v1,v5) — shared by tri1 and tri2.
Boundary edges (each on exactly 1 triangle):
  (v0,v1), (v1,v3), (v3,v0) from tri0;
  (v1,v2), (v2,v5) from tri1;
  (v5,v4), (v4,v1) from tri2.

Two boundary loops:
  Loop A: v0-v1-v3-v0  (from tri0 alone)
  Loop B: v1-v2-v5-v4-v1  (from tri1+tri2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me049",
             title="boundary halfedge traversal: next_on_border walk around open mesh boundary",
             defect_class="boundary_traversal")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1  — shared interior vertex
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v3)   # tri 0 — left
t1 = m.triangle(v1, v2, v5)   # tri 1 — right
t2 = m.triangle(v1, v5, v4)   # tri 2 — top-right connector; shares (v1,v5) with tri1

# Interior edge (v1,v5) shared by tri1 and tri2.
m.assert_edge_shared(v1, v5, 2)

# Boundary loop A: triangle 0's three boundary edges.
m.assert_hole_boundary([v0, v1, v3])

# Boundary loop B: combined boundary ring of tri1 + tri2.
m.assert_hole_boundary([v1, v2, v5, v4])
