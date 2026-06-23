"""Me075 — duplicate_singular_vertices: non-manifold vertex with isolated neighbor.

Catalog claim: vertex 0 is a non-manifold (singular) vertex (bowtie) AND
vertex 5 is an isolated vertex (referenced by no triangle). This exercises both
Branch 3 (*isolated_vertex_skip* — the algorithm skips v5 because its
incident-polygon list is empty) and Branch 5 (*non_manifold_vertex* — v0 is
marked for duplication because its fan has 2 link CCs).

Defect carrier:
  Bowtie at v0: upper fan (v0,v1,v2), lower fan (v0,v3,v4) — share only v0.
  Isolated vertex v5=(3,0,0) — not referenced by any triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me075",
             title="duplicate_singular_vertices: bowtie vertex plus isolated (unreferenced) neighbor vertex",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper fan
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2 — upper fan
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower fan
v4 = m.vertex(-1.0, -1.0, 0.0) # 4 — lower fan
v5 = m.vertex(3.0, 0.0, 0.0)   # 5 — isolated vertex (no incident polygons)

t0 = m.triangle(v0, v1, v2)   # upper fan
t1 = m.triangle(v0, v3, v4)   # lower fan

# Bowtie assertions.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_vertex_fan_disconnected(v0)

# Isolated vertex assertion.
m.assert_isolated_vertex(v5)
