"""Me074 — duplicate_singular_vertices: two non-manifold vertices in one mesh.

Catalog claim: vertices 0 and 7 are both non-manifold (singular) vertices,
each with a disconnected triangle fan (2 link CCs each). This exercises CGAL
PMP.Polygon_soup_orienter.duplicate_singular_vertices Branch 2 (*vertex_iteration*)
iterating over the full vertex list and detecting **two** distinct singularities,
and Branch 10 (*point_duplication_loop*) looping over both entries in the
vertices_to_duplicate collection.

Defect carrier:
  Bowtie at v0: upper fan (v0,v1,v2), lower fan (v0,v3,v4) — share only v0.
  Bowtie at v7: left fan (v7,v5,v6), right fan (v7,v8,v9) — share only v7.
  The two bowties are geometrically separated (one near origin, one near x=5).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me074",
             title="duplicate_singular_vertices: two separate bowtie vertices in one mesh",
             defect_class="non_manifold_vertex")

# Bowtie 1 — near origin.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular vertex #1
v1 = m.vertex(1.0, 1.0, 0.0)   # 1
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2
v3 = m.vertex(1.0, -1.0, 0.0)  # 3
v4 = m.vertex(-1.0, -1.0, 0.0) # 4

# Bowtie 2 — near x=5.
v5 = m.vertex(4.0, 1.0, 0.0)   # 5
v6 = m.vertex(6.0, 1.0, 0.0)   # 6
v7 = m.vertex(5.0, 0.0, 0.0)   # 7 — singular vertex #2
v8 = m.vertex(4.0, -1.0, 0.0)  # 8
v9 = m.vertex(6.0, -1.0, 0.0)  # 9

# Bowtie 1 triangles.
t0 = m.triangle(v0, v1, v2)   # upper fan
t1 = m.triangle(v0, v3, v4)   # lower fan

# Bowtie 2 triangles.
t2 = m.triangle(v7, v5, v6)   # left fan
t3 = m.triangle(v7, v8, v9)   # right fan

# Boundary edges for bowtie 1.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
# Boundary edges for bowtie 2.
m.assert_edge_shared(v7, v5, 1)
m.assert_edge_shared(v7, v8, 1)

# Both singular vertices have disconnected fans.
m.assert_vertex_fan_disconnected(v0)
m.assert_vertex_fan_disconnected(v7)
