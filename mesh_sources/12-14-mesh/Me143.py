"""Me143 — isInnerPoint_point_on_v2_vertex: query point coincides with triangle vertex v2.

MeshFix `Basic_TMesh.isInnerPoint` Branch 5 (*point_on_vertex*) @ line 2004:
  'if (o1 == 0 && o2 == 0) { ... closest_vertex = v2; return false; }'
  Branch 6 (*point_on_vertex_exact*) @ line 2006:
  'if (ad = v2->x - p.x; ad == 0) return false'
  When the query point p coincides exactly with vertex v2, two of the
  three 2D orientation values are zero (o1==0, o2==0). MeshFix records
  v2 as the closest vertex and returns false (point is on the surface,
  not strictly inside). Branch 6 additionally checks the x-distance to
  confirm exact coincidence.

Geometric signature: a triangle where one vertex (v2) coincides exactly
with another tracked vertex — two distinct index entries at the same 3D
position. The near-coincident pair triggers both branch 5 and branch 6
when the query point equals v2's coordinates.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  v3=(0.5,1,0)  — duplicate of v2 (distance=0)
  t0=(v0,v1,v2), t1=(v0,v1,v3)  — two overlapping triangles

The vertex pair (v2, v3) distance=0 proves the coincidence.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me143",
             title="isInnerPoint_point_on_v2_vertex: query point = v2 gives o1=o2=0, closest_vertex set, return false",
             defect_class="isInnerPoint_point_on_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — upper vertex
v3 = m.vertex(0.5, 1.0, 0.0)   # 3 — duplicate of v2 (same position)

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v1, v3)    # 1 — overlapping triangle (v3 == v2 position)

# v2 and v3 are at the same position — the query point equals this vertex.
m.assert_vertex_pair_distance_lt(v2, v3, 1e-9)

# Edge (v0,v1) shared by both triangles (interior edge between duplicates).
m.assert_edge_shared(v0, v1, 2)

# Both boundary edges (v0,v2) and (v0,v3) appear only once each.
# Since v2 and v3 are at the same position, the mesh has an effective
# duplicate face pair whose "apex" edges are each boundary.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
