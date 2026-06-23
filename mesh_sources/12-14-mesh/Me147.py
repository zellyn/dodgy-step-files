"""Me147 — isInnerPoint_point_in_triangle: query point strictly inside triangle, ray hits interior.

MeshFix `Basic_TMesh.isInnerPoint` Branch 12 (*point_in_triangle*) @ line 2029:
  'if (o1 > 0 && o2 > 0 && o3 > 0) { linePlaneIntersection(...); ... }'
  When all three orientation values are strictly positive, the query
  point's 2D projection falls inside the triangle. isInnerPoint calls
  linePlaneIntersection to find where the vertical ray through p crosses
  the triangle's plane, then records this crossing as the closest
  intersection and updates the crossing count.

Geometric signature: a closed tetrahedron (4 triangles forming a
watertight mesh). A query point at the centroid would have all three
orientations positive for the bottom face. The triangles all share edges
pairwise (interior edges, n=2) except for the base, confirming a closed,
manifold mesh where isInnerPoint would count crossings correctly.

Geometry (tetrahedron):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,0.67,1.5)
  t0=(v0,v2,v1)  — base (CCW from below)
  t1=(v0,v1,v3)  — front face
  t2=(v1,v2,v3)  — right face
  t3=(v2,v0,v3)  — left face
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me147",
             title="isInnerPoint_point_in_triangle: all orientations positive for query inside triangle, linePlaneIntersection fires",
             defect_class="isInnerPoint_point_in_triangle")

v0 = m.vertex(0.0, 0.0,  0.0)   # 0
v1 = m.vertex(2.0, 0.0,  0.0)   # 1
v2 = m.vertex(1.0, 2.0,  0.0)   # 2
v3 = m.vertex(1.0, 0.67, 1.5)   # 3 — apex above the base

t0 = m.triangle(v0, v2, v1)     # 0 — base (outward normal points down)
t1 = m.triangle(v0, v1, v3)     # 1 — front
t2 = m.triangle(v1, v2, v3)     # 2 — right
t3 = m.triangle(v2, v0, v3)     # 3 — left

# All lateral edges are interior (shared by 2 triangles).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)
