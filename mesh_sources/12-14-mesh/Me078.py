"""Me078 — duplicate_singular_vertices: 3-way fan (2 new duplicate points needed).

Catalog claim: vertex 0 is a non-manifold (singular) vertex with **3** link
connected components (three disjoint triangle fans). CGAL
duplicate_singular_vertices Branch 10 (*point_duplication_loop*) must create
2 new duplicate points (Branch 11, *new_point_creation*: points.push_back for
each extra fan), and update polygon references in 2 groups of triangles
(Branch 12, *polygon_index_replacement*). The first fan keeps the original
vertex index; the second and third fans receive newly appended indices.

Defect carrier (3 fans at different heights in Z):
  Fan A (z=0): t0=(v0,v1,v2)   v1=(1,1,0)  v2=(-1,1,0)
  Fan B (z=2): t1=(v0,v3,v4)   v3=(1,1,2)  v4=(-1,1,2)
  Fan C (z=4): t2=(v0,v5,v6)   v5=(1,1,4)  v6=(-1,1,4)
  All three share only v0=(0,0,0); three separate link CCs.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me078",
             title="duplicate_singular_vertices: 3-fan vertex requiring 2 new duplicate points",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — triple-bowtie vertex

# Fan A (z=0 plane).
v1 = m.vertex(1.0, 1.0, 0.0)   # 1
v2 = m.vertex(-1.0, 1.0, 0.0)  # 2

# Fan B (z=2 plane).
v3 = m.vertex(1.0, 1.0, 2.0)   # 3
v4 = m.vertex(-1.0, 1.0, 2.0)  # 4

# Fan C (z=4 plane).
v5 = m.vertex(1.0, 1.0, 4.0)   # 5
v6 = m.vertex(-1.0, 1.0, 4.0)  # 6

t0 = m.triangle(v0, v1, v2)   # fan A
t1 = m.triangle(v0, v3, v4)   # fan B
t2 = m.triangle(v0, v5, v6)   # fan C

# Every edge at v0 is a boundary edge (one per fan, two per fan = 2 per triangle).
m.assert_edge_shared(v0, v1, 1)   # fan A boundary
m.assert_edge_shared(v0, v2, 1)   # fan A boundary
m.assert_edge_shared(v0, v3, 1)   # fan B boundary
m.assert_edge_shared(v0, v4, 1)   # fan B boundary
m.assert_edge_shared(v0, v5, 1)   # fan C boundary
m.assert_edge_shared(v0, v6, 1)   # fan C boundary

# v0's fan is disconnected (3 link CCs).
m.assert_vertex_fan_disconnected(v0)
