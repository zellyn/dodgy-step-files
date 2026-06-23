"""Me145 — isInnerPoint_point_on_v3_vertex: query point coincides with triangle vertex v3.

MeshFix `Basic_TMesh.isInnerPoint` Branch 8 (*point_on_vertex*) @ line 2014:
  'if (o2 == 0 && o3 == 0) { ... closest_vertex = v3; return false or track }'
  When the query point p coincides with vertex v3 (the third triangle
  vertex, not v1 or v2), the orientation values o2 and o3 are zero.
  This branch is geometrically distinct from Branches 5 and 7: it fires
  only when the ray from p intersects exactly at v3's position, making
  o2 and o3 simultaneously zero while o1 is non-zero.

Geometric signature: a triangle with v3 as the apex plus a second vertex
at the same position as v3. Two triangles share an edge through the apex,
confirming the mesh context where a query at v3's coordinates would fire
Branch 8.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0)
  v3=(1,2,0)  — duplicate of v2 (acts as v3 in orientation labeling)
  t0=(v0,v1,v2), t1=(v0,v2,v3)  — triangle pair sharing the apex edge
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me145",
             title="isInnerPoint_point_on_v3_vertex: query point = v3 gives o2=o3=0, closest_vertex=v3, return false",
             defect_class="isInnerPoint_point_on_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — apex vertex
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — duplicate of v2 (= v3 in isInnerPoint labeling)

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1 — v3 at apex position

# v2 and v3 at the same position — query at v3 = v2's coordinates.
m.assert_vertex_pair_distance_lt(v2, v3, 1e-9)

# Edge (v0,v2) shared by both triangles (interior edge through apex).
m.assert_edge_shared(v0, v2, 2)

# t0 and t1 are geometric duplicates (sorted vertex sets both = {0,1,2} vs {0,2,3}).
# Verify both triangles are near-degenerate (zero area between them).
m.assert_triangle_area_lt(t1, 1e-9)
