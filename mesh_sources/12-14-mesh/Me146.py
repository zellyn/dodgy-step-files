"""Me146 — isInnerPoint_point_on_edge: query point lies on triangle edge interior.

MeshFix `Basic_TMesh.isInnerPoint` Branch 9 (*point_on_edge*) @ line 2019:
  'if (o1 == 0 || o2 == 0 || o3 == 0) { ... select edge, compute intersection }'
  When exactly one of the three orientation values is zero, the query
  point lies on one of the triangle's projected edges (not at a vertex).
  isInnerPoint selects that edge and computes a line-line intersection
  to find the X-coordinate of the boundary crossing.

Geometric signature: a T-junction where vertex v3 lies exactly on the
interior of edge (v0, v2) of triangle t0. The query point at v3's
position gives o_edge=0 for the edge containing v3. This is the same
mesh pattern as Me009 but now labeled as the isInnerPoint edge-interior
branch driver.

Geometry:
  v0=(0,0,0), v1=(0.5,1,0), v2=(1,0,0)  — host triangle t0
  v3=(0.5,0,0)  — midpoint of edge (v0,v2); query at v3 → o_edge=0
  v4=(0.5,-1,0) — opposite vertex; t1=(v0,v4,v3), t2=(v3,v4,v2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me146",
             title="isInnerPoint_point_on_edge: query at midpoint of edge gives one orientation=0, edge-intersection branch fires",
             defect_class="isInnerPoint_point_on_edge")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(0.5,  1.0, 0.0)   # 1
v2 = m.vertex(1.0,  0.0, 0.0)   # 2
v3 = m.vertex(0.5,  0.0, 0.0)   # 3 — midpoint of (v0,v2); T-junction
v4 = m.vertex(0.5, -1.0, 0.0)   # 4

m.triangle(v0, v1, v2)          # 0 — host face (edge v0-v2 contains v3)
m.triangle(v0, v4, v3)          # 1
m.triangle(v3, v4, v2)          # 2

# v3 lies exactly on the interior of edge (v0, v2) — T-junction proof.
m.assert_vertex_on_edge(v3, v0, v2)
