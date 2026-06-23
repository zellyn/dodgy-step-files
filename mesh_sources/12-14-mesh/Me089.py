"""Me089 — connectivity_disconnected_edges: non-manifold vertex forming two disconnected fans.

Catalog claim: vertex v0 is a non-manifold (bowtie) vertex — its incident
triangle fan is split into two disconnected components with no shared edge
between them. MeshFix checkConnectivity Branch 13 (*DISCONNECTED_TRIANGLE_EDGES*)
fires when the three edges of a triangle do not share vertices as required
(e.g. edges (a,b), (c,d), (e,f) with all six indices distinct). In a
triangle-list mesh, the closest structural analog is a vertex whose edge
ring is topologically disconnected — traversing the fan from one side cannot
reach the other side without passing through the bowtie vertex itself. This
is distinct from the bowtie (Me011) in that here the two fans form a T-junction
at v0 with three arms rather than two.

Defect carrier: v0 has three disconnected fan components — an upper fan
(t0, t1), a right fan (t2), and a lower fan (t3). Each sub-fan is only
connected to the others through v0. Removing v0 splits the mesh into three
independent pieces — triple-bowtie topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me089",
             title="connectivity disconnected edges: triple-bowtie vertex v0 — 3 disconnected triangle fans",
             defect_class="non_manifold_vertex")

# Central bowtie vertex.
v0 = m.vertex(0.0, 0.0, 0.0)

# Upper fan vertices (two triangles sharing an interior edge).
v1 = m.vertex(0.0, 1.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(-1.0, 1.0, 0.0)

# Right fan vertex (single triangle).
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)

# Lower fan vertex (single triangle).
v6 = m.vertex(0.0, -1.0, 0.0)
v7 = m.vertex(1.0, -1.0, 0.0)

# Upper fan: two triangles sharing edge (v0, v2).
t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v0, v3, v1)

# Right fan: single triangle.
t2 = m.triangle(v0, v4, v5)

# Lower fan: single triangle.
t3 = m.triangle(v0, v6, v7)

# Upper interior edge shared by t0 and t1.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges of each arm.
m.assert_edge_shared(v0, v2, 1)   # upper fan boundary
m.assert_edge_shared(v0, v3, 1)   # upper fan boundary
m.assert_edge_shared(v0, v4, 1)   # right fan
m.assert_edge_shared(v0, v5, 1)   # right fan
m.assert_edge_shared(v0, v6, 1)   # lower fan
m.assert_edge_shared(v0, v7, 1)   # lower fan

# v0's triangle fan is split into (at least) 2 disconnected components.
m.assert_vertex_fan_disconnected(v0)
