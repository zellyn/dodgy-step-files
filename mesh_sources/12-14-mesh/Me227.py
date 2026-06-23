"""Me227 — eulerUpdate_euler_characteristic: V-E+F computed via Euler formula (Branch 8).

MeshFix `Basic_TMesh.eulerUpdate` Branch 8 (*euler_characteristic*) @ line 1779:
  'n_handles = (E.numels() - V.numels() - T.numels()) / 2 + n_shells - n_boundaries'
  Calculate n_handles (genus) from the Euler characteristic V-E+T.

eulerUpdate computes the Euler characteristic χ = V - E + F to derive the number
of topological handles (genus g). For a closed orientable surface: χ = 2(1 - g),
giving g = (2 - χ) / 2. For a closed mesh with one shell and no boundary:
n_handles = (E - V - T) / 2 + n_shells.

Geometry: a tetrahedron — the simplest closed manifold triangulation.
  V=4, E=6, F=4
  χ = V - E + F = 4 - 6 + 4 = 2   →  genus = 0 (sphere topology).
  n_handles = (E - V - T) / 2 + 1 = (6 - 4 - 4) / 2 + 1 = -1 + 1 = 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me227",
             title="eulerUpdate_euler_characteristic: tetrahedron V=4 E=6 F=4 chi=2 genus=0",
             defect_class="euler_update_characteristic")

# Tetrahedron vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, 0.5, 1.0)   # 3 — apex

# Four faces of the tetrahedron (consistent outward normals).
t0 = m.triangle(v0, v2, v1)   # 0 — bottom (normal pointing down)
t1 = m.triangle(v0, v1, v3)   # 1 — front
t2 = m.triangle(v1, v2, v3)   # 2 — right
t3 = m.triangle(v2, v0, v3)   # 3 — left

# Each edge shared by exactly 2 triangles (closed manifold — no boundary).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler characteristic: V=4, E=6, F=4 → chi=2.
m.assert_euler_characteristic(4, 6, 4, 2)
