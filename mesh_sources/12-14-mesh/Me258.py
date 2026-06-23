"""Me258 — openToDisk_manifold_fixup: duplicateNonManifoldVertices called after disk cut (Branch 9).

MeshFix `Basic_TMesh.openToDisk` Branch 9 (*manifold_fixup*) @ line 1854:
  'duplicateNonManifoldVertices()' — after edge duplication to open the surface to
  a disk, non-manifold vertices may have been created at the cut seam; this call
  resolves them to restore vertex manifoldness.

When openToDisk duplicates interior edges to cut handles, vertices at the ends of
those edges can become non-manifold: the same vertex is now incident on triangles
from two topologically-disconnected fans. Branch 9 calls duplicateNonManifoldVertices
to split such bowtie vertices into distinct copies.

Geometry: a mesh with a non-manifold (bowtie) vertex — two triangle fans meeting at
a single shared vertex with no shared edge between them. This is exactly the result
that openToDisk produces after cutting an interior edge. The fixture demonstrates
the input pattern that requires duplicateNonManifoldVertices.

Topology: vertex v0 is incident on triangles {t0,t1} AND {t2,t3}, but the two
groups share ONLY the vertex v0, not any edge. v0's fan is disconnected.

  Group A: t0=(v0,v1,v2), t1=(v0,v2,v3)  — upper fan
  Group B: t2=(v0,v4,v5), t3=(v0,v5,v6)  — lower fan
  v0 appears in all four triangles but the two fans are edge-disjoint.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me258",
             title="openToDisk_manifold_fixup: bowtie vertex v0 — disconnected fan requires duplicateNonManifoldVertices",
             defect_class="open_to_disk_manifold_fixup")

# Bowtie/hourglass: v0 is the pinch point.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — pinch/bowtie vertex
v1 = m.vertex(1.0,  1.0, 0.0)   # 1 — upper fan A
v2 = m.vertex(0.0,  2.0, 0.0)   # 2 — upper fan A
v3 = m.vertex(-1.0, 1.0, 0.0)   # 3 — upper fan A
v4 = m.vertex(1.0, -1.0, 0.0)   # 4 — lower fan B
v5 = m.vertex(0.0, -2.0, 0.0)   # 5 — lower fan B
v6 = m.vertex(-1.0,-1.0, 0.0)   # 6 — lower fan B

# Upper fan A (2 triangles around v0, connected to each other).
t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1

# Lower fan B (2 triangles around v0, disconnected from fan A).
t2 = m.triangle(v0, v4, v5)   # 2
t3 = m.triangle(v0, v5, v6)   # 3

# Interior edges within each fan.
m.assert_edge_shared(v0, v2, 2)   # shared within fan A
m.assert_edge_shared(v0, v5, 2)   # shared within fan B

# All outer edges are boundary (each incident on 1 triangle only).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v0, v6, 1)

# v0's triangle fan is disconnected: the two groups {t0,t1} and {t2,t3} share
# no edge — they only share the vertex v0. This is the non-manifold vertex pattern
# that openToDisk creates after edge duplication and that Branch 9 must fix.
m.assert_vertex_fan_disconnected(v0)
