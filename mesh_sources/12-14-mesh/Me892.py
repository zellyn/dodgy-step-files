"""Me892 — merge_duplicated_vertices_in_boundary_cycles merge_delegation/closed_mesh_noop: closed tetrahedron; extract_boundary_cycles returns empty cycles vector; function is no-op (Branch 3).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycles` Branch 3 (*merge_delegation*) @ line 354:
  'merge_duplicated_vertices_in_boundary_cycle(h, pm, np);'
  — The multi-cycle dispatcher only calls the single-cycle merge for
  cycles found in the cycles vector. When the mesh is closed (every edge
  is incident on exactly 2 triangles), extract_boundary_cycles returns
  an empty vector and the for-loop body never executes. Branch 3 is the
  no-op path: the function returns without invoking any merge.

Defect pattern: a valid closed tetrahedron — four triangles, four
  vertices, all edges shared by exactly 2 triangles, no boundary, Euler
  characteristic chi=2 (genus-0 closed surface). This is the reference
  "healthy" mesh for the merge_duplicated_vertices_in_boundary_cycles
  no-op path: extract_boundary_cycles returns empty cycles → the for-loop
  over cycles never executes → no merge is performed.

Geometry (regular tetrahedron):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5, sqrt(3)/2, 0), v3=(0.5, sqrt(3)/6, sqrt(6)/3)
  All four faces: (v0,v1,v2), (v0,v3,v1), (v0,v2,v3), (v1,v3,v2).
  All six edges each shared by exactly 2 triangles — closed mesh.
  V=4, E=6, F=4, chi=2.
"""
import math
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me892",
    title="merge_duplicated_vertices_in_boundary_cycles merge_delegation/closed_mesh_noop: closed tetrahedron; all edges n=2; extract_boundary_cycles returns empty; for-loop never executes (Branch 3)",
    defect_class="hole_in_hull",
)

# Closed tetrahedron vertices.
v0 = m.vertex(0.0, 0.0, 0.0)                                              # 0
v1 = m.vertex(1.0, 0.0, 0.0)                                              # 1
v2 = m.vertex(0.5, math.sqrt(3.0) / 2.0, 0.0)                            # 2
v3 = m.vertex(0.5, math.sqrt(3.0) / 6.0, math.sqrt(6.0) / 3.0)          # 3

# Four faces of the closed tetrahedron (CCW winding from outside).
m.triangle(v0, v1, v2)  # 0: base face
m.triangle(v0, v3, v1)  # 1: front-left face
m.triangle(v0, v2, v3)  # 2: left face
m.triangle(v1, v3, v2)  # 3: right face

# All six edges must be shared by exactly 2 triangles (closed mesh).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler: V=4, E=6, F=4, chi=2 (closed genus-0 surface — sphere topology).
m.assert_euler_characteristic(4, 6, 4, 2)
