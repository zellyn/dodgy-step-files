"""Me160 — stitch_boundary_edge_requirement: interior edge rejected for stitching.

MeshFix `Edge.stitch` Branch 1 (*BOUNDARY_EDGE_REQUIREMENT*) @ line 369:
  'if (!isOnBoundary()) return 0'
  Edge.stitch() immediately returns false if the edge is interior (has two
  incident triangles). Only boundary edges (incident on exactly one triangle)
  are eligible for boundary stitching.

Defect pattern: two adjacent triangles share a common edge; that edge is
interior (shared by 2 triangles) and therefore cannot serve as a stitch target.
A healer calling Edge.stitch() on this edge hits Branch 1 and aborts.

Geometry: a simple two-triangle patch in the XY plane.
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-0.5,1,0)
  t0 = (v0, v1, v2)   — lower-right triangle
  t1 = (v0, v2, v3)   — upper-left triangle, shares edge (v0,v2) with t0

Edge (v0,v2) is interior — incident on t0 and t1. Calling stitch on it fails
Branch 1 ('if (!isOnBoundary()) return 0').
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me160",
             title="stitch_boundary_edge_requirement: interior edge (two incident triangles) rejected for boundary stitching",
             defect_class="stitch_interior_edge_rejected")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.5, 1.0, 0.0)    # 2 — shared interior apex
v3 = m.vertex(-0.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)     # 0
t1 = m.triangle(v0, v2, v3)     # 1

# The candidate stitch edge is interior — shared by both triangles.
m.assert_edge_shared(v0, v2, 2)  # interior; stitch Branch 1 rejects this

# Outer boundary edges each incident on exactly one triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
