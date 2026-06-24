"""Me760 — retriangulateVT_triangle_normal_accumulation: vertex hub with multiple incident triangles, normals summed across fan (Branch 1).

MeshFix `holeFilling::retriangulateVT` Branch 1 (*TRIANGLE_NORMAL_ACCUMULATION*) @ line 399:
  'nor = nor + t->getNormal()'
  In retriangulateVT, for each vertex v, the algorithm walks the incident
  triangle fan and accumulates the geometric normal of each triangle into the
  'nor' accumulator. This fires for every triangle in the fan — i.e. Branch 1
  fires once per incident triangle around the vertex being retriangulated.

Defect pattern: a 5-triangle fan around a central hub vertex v0=(1,1,0) with
  5 outer vertices forming a pentagon. All triangles lie in the XY plane with
  consistent CCW winding → all normals point in the +Z direction. When
  retriangulateVT processes v0, it walks t0..t4 and accumulates each
  t->getNormal() into nor — Branch 1 fires 5 times.

Geometry: hub v0=(1,1,0), outer ring v1..v5 (pentagon).
  v0=(1,1,0), v1=(1,0,0), v2=(2,1,0), v3=(1.5,2,0), v4=(0.5,2,0), v5=(0,1,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v5), t4=(v0,v5,v1)
  Hub edges each shared by 2 triangles; outer rim edges each shared by 1.
  Adjacent normals all parallel (+Z) — confirms consistent normal accumulation.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me760",
    title="retriangulateVT_triangle_normal_accumulation: 5-triangle fan around hub v0; normals accumulated via nor=nor+t->getNormal() for each incident triangle (Branch 1)",
    defect_class="retriangulate_region_internal_vertex",
)

# Hub vertex at center
v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — hub vertex being retriangulated

# Outer pentagon ring
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 2.0, 0.0)   # 3
v4 = m.vertex(0.5, 2.0, 0.0)   # 4
v5 = m.vertex(0.0, 1.0, 0.0)   # 5

# 5-triangle fan — CCW winding gives +Z normal for all triangles.
# Each triangle contributes getNormal() to the accumulator in Branch 1.
t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2
t3 = m.triangle(v0, v4, v5)   # 3
t4 = m.triangle(v0, v5, v1)   # 4

# Hub edges — each shared by exactly 2 fan triangles.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)
m.assert_edge_shared(v0, v5, 2)

# Outer rim edges — each incident on exactly 1 triangle (open boundary).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v1, 1)

# All adjacent fan triangle pairs have consistent (+Z) normals (dot product > 0.99).
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, 0.99)
m.assert_adjacent_triangles_normal_dot_gt(t1, t2, 0.99)
m.assert_adjacent_triangles_normal_dot_gt(t2, t3, 0.99)
m.assert_adjacent_triangles_normal_dot_gt(t3, t4, 0.99)

# Euler: V=6, E=10 (5 hub + 5 rim), F=5, chi=1 (open disk).
m.assert_euler_characteristic(6, 10, 5, 1)
