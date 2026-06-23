"""Me213 — cutAndStitch_non_manifold_vertices: singular vertex requiring duplication.

MeshFix `Basic_TMesh.cutAndStitch` Branch 4 (*NON_MANIFOLD_VERTICES*) @ line 1004:
  'duplicateNonManifoldVertices()'
  After forceNormalConsistence(), the mesh may still contain singular vertices
  (bowtie configuration). cutAndStitch calls duplicateNonManifoldVertices() to
  split each such vertex into separate copies, one per fan component.

Defect pattern: a bowtie vertex where two triangle fans share a single vertex
but no edge. The vertex fan is disconnected — removing the vertex disconnects
the two fan components. duplicateNonManifoldVertices() targets exactly this.

Geometry: classic bowtie — two fans meeting only at vertex v0.
  v0=(0,0,0) — singular bowtie vertex
  Upper fan: v1=(1,1,0), v2=(-1,1,0), t0=(v0,v1,v2)
  Lower fan: v3=(1,-1,0), v4=(-1,-1,0), t1=(v0,v3,v4)
  No shared edge between t0 and t1 at v0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me213",
             title="cutAndStitch_non_manifold_vertices: bowtie vertex requiring duplicateNonManifoldVertices()",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex
v1 = m.vertex(1.0, 1.0, 0.0)   # 1 — upper fan
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2 — upper fan
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — lower fan
v4 = m.vertex(-1.0, -1.0, 0.0) # 4 — lower fan

t0 = m.triangle(v0, v1, v2)   # 0 — upper fan
t1 = m.triangle(v0, v3, v4)   # 1 — lower fan — shares only v0

# All four edges incident on v0 are boundary (each on exactly 1 triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)

# The vertex fan at v0 is disconnected: duplicateNonManifoldVertices() target.
m.assert_vertex_fan_disconnected(v0)
