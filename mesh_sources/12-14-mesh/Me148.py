"""Me148 — isInnerPoint_closest_is_edge_boundary: closest point is a boundary edge, return false.

MeshFix `Basic_TMesh.isInnerPoint` Branch 15 (*closest_is_edge*) @ line 2055:
  'if (closest_edge != NULL) { ... }'
  Branch 16 (*edge_on_boundary*) @ line 2057:
  'if (closest_edge->isOnBoundary()) return false'
  After the full triangle scan, if the closest ray-crossing point falls
  on an edge (not vertex, not triangle interior), isInnerPoint checks
  whether that edge is a mesh boundary edge (incident on exactly 1
  triangle). If so, the query point is on the surface boundary and
  isInnerPoint returns false without ambiguity.

Geometric signature: an open mesh (two triangles sharing an interior
edge) where the closest approach of a ray hits the shared interior edge.
The three boundary edges (incident on exactly 1 triangle) demonstrate
the mesh is open; if the query point projects onto a boundary edge,
Branch 16 fires.

Geometry (two triangles, open mesh):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0)
  t0=(v0,v2,v1)  — upper triangle
  t1=(v0,v1,v3)  — lower triangle
  Shared interior edge: (v0,v1). Boundary edges: (v0,v2),(v1,v2),(v0,v3),(v1,v3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me148",
             title="isInnerPoint_closest_is_edge_boundary: closest ray-hit is a boundary edge, isOnBoundary() true, return false",
             defect_class="isInnerPoint_edge_on_boundary")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(2.0,  0.0, 0.0)   # 1
v2 = m.vertex(1.0,  1.0, 0.0)   # 2 — upper apex
v3 = m.vertex(1.0, -1.0, 0.0)   # 3 — lower apex

t0 = m.triangle(v0, v2, v1)     # 0 — upper triangle
t1 = m.triangle(v0, v1, v3)     # 1 — lower triangle

# Interior edge shared by both triangles.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges (incident on exactly 1 triangle each).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# Open mesh: hole boundary at the outer perimeter.
m.assert_hole_boundary([v0, v2, v1, v3])
