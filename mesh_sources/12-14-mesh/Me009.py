"""Me009 — t_junction: vertex lies exactly on an adjacent triangle's edge.

Catalog claim: vertex 3 is located exactly on the edge between vertices 0
and 2, but triangle 0 uses edge (v0, v2) without listing v3. The mesh has a
topological crack: triangles 1 and 2 meet at v3, but triangle 0's edge (v0,v2)
passes through v3 without acknowledging it. Shading and CSG operations will
produce artefacts at this seam.

Defect carrier: triangle 0 uses vertices (v0, v1, v2); triangle 1 uses
(v0, v3, v1); triangle 2 uses (v3, v2, v1). Vertex v3 = (0.5, 0, 0) is
exactly the midpoint of the edge between v0=(0,0,0) and v2=(1,0,0) in
triangle 0's edge list, but (v0, v2) is still an unbroken edge in face 0.
CGAL Snapping::snap / MeshFix meshclean must detect and split this edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me009",
             title="T-junction: vertex 3 lies on edge (v0,v2) of triangle 0 but is not listed in it",
             defect_class="t_junction")

# Triangle 0: the "host" face whose edge harbors the T-junction.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(0.5, 1.0, 0.0)
v2 = m.vertex(1.0, 0.0, 0.0)
m.triangle(v0, v1, v2)   # face 0: edge (v0, v2) = segment from (0,0,0) to (1,0,0)

# v3 lies exactly on edge (v0, v2) at the midpoint.
v3 = m.vertex(0.5, 0.0, 0.0)

# Two triangles on the opposite side that "know about" v3.
v4 = m.vertex(0.5, -1.0, 0.0)
m.triangle(v0, v4, v3)   # face 1: lower-left, ends at v3
m.triangle(v3, v4, v2)   # face 2: lower-right, starts at v3

# Assert: v3 lies on the segment between v0 and v2 (T-junction evidence).
m.assert_vertex_on_edge(v3, v0, v2)
