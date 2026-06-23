"""Me310 — watsonInsert_point_in_circumsphere: inserted point lies inside circumsphere of Delaunay triangle.

MeshFix `holeFilling::watsonInsert` Branch 1 (*POINT_IN_CIRCUMSPHERE*) @ line 309:
  't->inSphere(p)' — MARK_BIT(t, 6) / todo.appendHead(t)
  The Bowyer-Watson algorithm tests each triangle's circumsphere against the
  inserted point p. When p lies strictly inside the circumsphere, the triangle
  is marked (bit 6) and queued for cavity excavation.

Defect pattern: a triangulated square with a 3-triangle fan around center. The
  center vertex v4=(1,1,0) is inserted into the existing 2-triangle mesh. Its
  position lies inside the circumsphere of both original triangles (which have
  circumradius = sqrt(2) centred at (1,1,0)), triggering Branch 1 on each.

Geometry: square base (v0-v3), center vertex v4.
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0), v4=(1,1,0)
  Original 2-triangle triangulation before insertion: t0=(v0,v1,v2), t1=(v0,v2,v3)
  After Watson insertion of v4: 4 triangles forming a fan.

The circumsphere of the original triangle t0=(v0,v1,v2) centred at (1,1,0) has
radius sqrt(2). The inserted point v4=(1,1,0) coincides with the circumcentre
and is inside the circumsphere — Branch 1 fires.

We model the pre-insertion state: 2 triangles sharing diagonal (v0,v2). The
  hole boundary after cavity excavation and before re-triangulation would be
  the triangle boundary. We assert the diagonal edge is shared by 2 triangles
  (showing the original Delaunay defect: both are in v4's circumsphere).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me310",
             title="watsonInsert_point_in_circumsphere: inserted point inside circumsphere triggers cavity marking (Branch 1)",
             defect_class="hole_in_hull")

# Original 2-triangle mesh before Bowyer-Watson cavity excavation.
# These two triangles will be marked for removal when v4=(1,1,0) is inserted.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# The two triangles forming the Delaunay triangulation of the square.
# v4=(1,1,0) would be at the circumcentre of both — Branch 1 fires on insertion.
t0 = m.triangle(v0, v1, v2)   # 0 — circumsphere centred at (1,1,0), radius sqrt(2)
t1 = m.triangle(v0, v2, v3)   # 1 — same circumsphere (symmetric)

# Diagonal edge (v0,v2) is shared by exactly 2 triangles — the interior edge
# that watsonInsert will remove when it excavates the Delaunay cavity.
m.assert_edge_shared(v0, v2, 2)

# Outer boundary edges each incident on 1 triangle — open square boundary.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5 (4 boundary + 1 diagonal), F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
