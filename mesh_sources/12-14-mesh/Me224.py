"""Me224 — eulerUpdate_boundary_edge_detection: boundary edge triggers hasBoundary=true (Branch 5).

MeshFix `Basic_TMesh.eulerUpdate` Branch 5 (*boundary_edge_detection*) @ line 1765:
  'e->isOnBoundary()' — edge is on mesh boundary.
  'hasBoundary = true' — set the hasBoundary flag for post-loop processing.

When eulerUpdate walks each edge of every triangle, it checks whether that edge
is a boundary edge (incident on exactly 1 triangle). On the first such boundary
edge found, it sets hasBoundary=true. This triggers the boundary-loop processing
phase (Branches 6–7). Without a boundary edge, hasBoundary stays false.

Geometry: an open triangulated strip — three triangles forming a quad with one
interior edge and four boundary edges. The first edge found with n=1 (boundary)
sets hasBoundary=true.

  t0 = (v0, v1, v2)  — left triangle
  t1 = (v1, v3, v2)  — right triangle (shares (v1,v2) with t0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me224",
             title="eulerUpdate_boundary_edge_detection: open mesh has boundary edges; hasBoundary=true",
             defect_class="open_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v1, v3, v2)   # 1

# Interior edge — shared by both triangles.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges (n=1) — each on exactly one triangle.
# These are the edges that trigger 'e->isOnBoundary()' in eulerUpdate.
m.assert_edge_shared(v0, v1, 1)   # boundary
m.assert_edge_shared(v0, v2, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary

# Confirm hole boundary loop formed by the outer rim.
m.assert_hole_boundary([v0, v1, v3, v2])
