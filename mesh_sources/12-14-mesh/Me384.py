"""Me384 — isDoubleFlat_flat_vertex_case: zero non-coplanar edges; nne==0 → return true (completely flat).

MeshFix `Vertex.isDoubleFlat` Branch 5 (*flat_vertex_case*) @ line 336:
  'if (nne == 0) return true;'
  After the 1-ring scan completes with nne==0 (no edges with non-zero convexity),
  the vertex is completely flat — every pair of adjacent triangles in its fan is
  coplanar. isDoubleFlat returns true immediately at Branch 5.

Geometric signature: vertex v0 at the center of a 4-triangle flat fan. All
triangles lie in the z=0 plane. Every dihedral angle between adjacent triangles
is 180° (flat), so every edge has zero convexity. After a full scan, nne==0 and
Branch 5 fires.

This is essentially the same geometric condition as a truly flat interior vertex
— the vertex lies in a single plane with all its neighbors. All fan edges are
interior (n=2), all outer edges are boundary (n=1).

Geometry (all z=0):
  v0 = (0.0, 0.0, 0.0)   — center flat vertex
  v1 = (-1.0, 0.0, 0.0)
  v2 = (0.0, 1.0, 0.0)
  v3 = (1.0, 0.0, 0.0)
  v4 = (0.0, -1.0, 0.0)

  t0 = (v0, v1, v2)
  t1 = (v0, v2, v3)
  t2 = (v0, v3, v4)
  t3 = (v4, v1, v0)

All coplanar → all dihedral angles flat → nne==0 → Branch 5 → return true.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me384",
             title="isDoubleFlat_flat_vertex_case: all fan triangles of v0 coplanar (z=0); nne==0 triggers Branch 5 return true",
             defect_class="flat_vertex_coplanar_fan")

v0 = m.vertex(0.0,  0.0,  0.0)   # 0 — center flat vertex
v1 = m.vertex(-1.0, 0.0,  0.0)   # 1
v2 = m.vertex(0.0,  1.0,  0.0)   # 2
v3 = m.vertex(1.0,  0.0,  0.0)   # 3
v4 = m.vertex(0.0, -1.0,  0.0)   # 4

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v0, v3, v4)    # 2
t3 = m.triangle(v4, v1, v0)    # 3

# All fan edges at v0 are interior (each shared by exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t3
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# The outer boundary edges are each incident on exactly 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# All adjacent fan triangle pairs share the same (z=0) plane — coplanar normals.
# All normals point in the same (−z) direction, so dot product > 0 (consistent winding).
# Euler: V=5, E=8, F=4, chi=1 (flat disk with hole boundary)
m.assert_euler_characteristic(5, 8, 4, 1)
