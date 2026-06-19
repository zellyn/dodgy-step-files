"""Me005 — self_intersection_face_pair: two triangles cross in space.

Catalog claim: triangles 0 and 1 lie in planes that intersect along a
line that cuts through both triangles' interiors. Common in CSG output
and digitized scans.

Defect carrier: triangle 0 lies in the XY plane (z=0); triangle 1 lies
in the XZ plane (y=0). Their planes intersect along the X axis, and
both triangles span the X axis between x=0 and x=1, so they cross.
Healer must detect via CGAL self_intersections / MeshFix
selectIntersectingTriangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me005",
             title="self-intersecting face pair: XY and XZ triangles crossing",
             defect_class="self_intersection_face_pair")

# Triangle 0: in XY plane, vertices at (0,0,0), (1,1,0), (1,-1,0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 1.0, 0.0)
v2 = m.vertex(1.0, -1.0, 0.0)
m.triangle(v0, v1, v2)

# Triangle 1: in XZ plane, vertices at (0,0,0), (1,0,1), (1,0,-1).
# Shares v0 with triangle 0; their planes intersect along the X axis.
v3 = m.vertex(1.0, 0.0, 1.0)
v4 = m.vertex(1.0, 0.0, -1.0)
m.triangle(v0, v3, v4)

m.assert_triangles_self_intersect(0, 1)
