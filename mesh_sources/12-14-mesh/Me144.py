"""Me144 — isInnerPoint_point_on_v1_vertex: query point coincides with triangle vertex v1.

MeshFix `Basic_TMesh.isInnerPoint` Branch 7 (*point_on_vertex*) @ line 2009:
  'if (o1 == 0 && o3 == 0) { ... closest_vertex = v1; return false or track }'
  When the query point p coincides with vertex v1 (not v2), the two
  orientation values o1 and o3 are simultaneously zero. This branch
  is distinct from Branch 5 (which fires for v2 coincidence, giving
  o1==0 && o2==0). isInnerPoint records v1 as closest and returns false.

Geometric signature: a triangle in the XY-plane plus a second vertex
placed at the same position as v1, demonstrating that the query point
sitting at v1 causes the o1==0, o3==0 pattern. Two triangles share
the v1-position vertex to create the mesh context.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0)
  v3=(2,0,0)  — duplicate of v1
  t0=(v0,v1,v2), t1=(v1,v2,v3)  — fan sharing the v1-vertex
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me144",
             title="isInnerPoint_point_on_v1_vertex: query point = v1 gives o1=o3=0, closest_vertex=v1, return false",
             defect_class="isInnerPoint_point_on_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — the v1 vertex in question
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(2.0, 0.0, 0.0)   # 3 — duplicate of v1 (same position)

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v1, v2, v3)    # 1 — v3 at same coords as v1

# v1 and v3 are at the same position — the query point equals v1's position.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)

# Edge (v1,v2) is shared by both triangles.
m.assert_edge_shared(v1, v2, 2)

# v3 lies on the edge (v1, v2) collapsed to a point — zero-distance proof.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
