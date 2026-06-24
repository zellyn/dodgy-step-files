"""Me1030 — split_connected_components component_subdivision: each disconnected component extracted to its own mesh.

CGAL PMP `PMP.split_connected_components` Branch 1 (*component_subdivision*) @ line 945:
  'extract_to_new_mesh(cc_meshes[i], ...)'
  — after PMP.connected_components partitions the faces into labelled
  groups, split_connected_components iterates each label and calls
  extract_to_new_mesh to move the faces into a fresh output mesh.
  This branch fires whenever the input contains two or more connected
  components that must be separated into independent mesh objects.

Defect pattern: a polygon mesh with two disconnected triangle components.
  Component A: single triangle near the origin (CC label 0).
  Component B: single triangle 50 units away (CC label 1).
  The two components share no edges and no vertices.
  split_connected_components must iterate both CC labels and produce
  two independent output meshes, exercising the extract_to_new_mesh
  loop for each component.

Geometry:
  Component A — v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0); t0=(v0,v1,v2).
  Component B — v3=(50,0,0), v4=(51,0,0), v5=(50.5,1,0); t1=(v3,v4,v5).
  Total: V=6, E=6, F=2, chi=2 (two separate open disks, each chi=1).
  t1 is unreachable from t0 by shared-edge walk → two CCs confirmed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1030",
    title="split_connected_components component_subdivision: two disconnected triangles each extracted to a new mesh (Branch 1)",
    defect_class="disconnected_components",
)

# Component A: triangle near origin (CC label 0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)

# Component B: triangle 50 units away (CC label 1).
v3 = m.vertex(50.0, 0.0, 0.0)
v4 = m.vertex(51.0, 0.0, 0.0)
v5 = m.vertex(50.5, 1.0, 0.0)
t1 = m.triangle(v3, v4, v5)

# Two independent open triangles — each edge is boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# t1 unreachable from t0 — two separate connected components.
m.assert_triangle_not_reachable_from(t1, t0)

# Euler: V=6, E=6, F=2, chi=2 (two open disk components, each chi=1).
m.assert_euler_characteristic(6, 6, 2, 2)
