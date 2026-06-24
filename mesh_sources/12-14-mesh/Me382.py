"""Me382 — isDoubleFlat_edge_convexity_triple: more than 2 non-coplanar edges; nne>2 → return false.

MeshFix `Vertex.isDoubleFlat` Branch 3 (*edge_convexity_triple*) @ line 331:
  'else if (nne > 2) return false;'
  When the 1-ring scan finds a third edge with non-zero convexity (nne exceeds 2),
  the vertex is too complex to be a DoubleFlat and the function immediately returns
  false. A DoubleFlat vertex has exactly 2 ridge edges; 3 or more means the 1-ring
  is a general saddle or multi-ridge vertex.

Geometric signature: vertex v0 is a peak/saddle with 6 incident triangles forming
a 3D fan. Three alternating edges of the fan are ridges (non-coplanar dihedral).
This makes nne reach 3, triggering Branch 3 and returning false.

Geometry: tent-like structure with v0 at origin, outer ring alternating between
raised (z=1) and flat (z=0) — giving 3 ridges around the fan.
  v0 = (0, 0, 0)   — center vertex
  v1 = (1, 0, 0)   — flat (z=0)
  v2 = (0.5, 0.87, 1.0)   — raised
  v3 = (-1, 0, 0)  — flat (z=0)
  v4 = (-0.5, -0.87, 1.0) — raised
  v5 = (0, -1, 0)  — flat (z=0)
  v6 = (0.5, 0.87, -1.0)  — raised (different direction)

Six triangles:
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v5), t4=(v0,v5,v6), t5=(v0,v6,v1)

Each ridge transition (flat→raised) creates a non-coplanar edge; with 3 raised
vertices alternating, there are 6 ridge edges around v0, so nne will reach 3+
very quickly and Branch 3 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me382",
             title="isDoubleFlat_edge_convexity_triple: 6-triangle fan around v0 with 3 raised outer vertices; nne exceeds 2 → Branch 3 returns false",
             defect_class="non_double_flat_vertex_multi_ridge")

v0 = m.vertex(0.0,   0.0,   0.0)   # 0 — center
v1 = m.vertex(1.0,   0.0,   0.0)   # 1 — flat
v2 = m.vertex(0.5,   0.87,  1.0)   # 2 — raised
v3 = m.vertex(-1.0,  0.0,   0.0)   # 3 — flat
v4 = m.vertex(-0.5, -0.87,  1.0)   # 4 — raised
v5 = m.vertex(0.0,  -1.0,   0.0)   # 5 — flat
v6 = m.vertex(0.87,  0.5,  -1.0)   # 6 — raised (different z direction)

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v0, v3, v4)    # 2
t3 = m.triangle(v0, v4, v5)    # 3
t4 = m.triangle(v0, v5, v6)    # 4
t5 = m.triangle(v0, v6, v1)    # 5

# All 6 fan edges at v0 are interior (each shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t5
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3
m.assert_edge_shared(v0, v5, 2)   # shared by t3 and t4
m.assert_edge_shared(v0, v6, 2)   # shared by t4 and t5

# The outer ring edges are each incident on exactly 1 triangle (boundary).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v1, 1)
