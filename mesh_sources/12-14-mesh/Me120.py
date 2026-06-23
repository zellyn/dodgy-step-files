"""Me120 — inverse_collapse_right_triangle_e2: e2 has a right-side triangle (ta1 extraction).

Catalog claim: vertex v0 sits at the junction of a 4-triangle fan. Edge e2
(one boundary of the split sector) has an adjacent triangle ta1 on its right
side — this is the first piece of data extracted in MeshFix inverseCollapse.
Post-split, ta1 becomes the outer neighbor of new triangle t1.

This exercises MeshFix `Vertex.inverseCollapse` Branch 1 (*right_triangle_e2*):
`ta1 = e2->rightTriangle(this)` — the code extracts the triangle on the right
side of edge e2 with respect to vertex `this` (= v0).

Defect carrier: the mesh is a result of a prior vertex collapse — v0 has an
over-merged fan of 4 triangles where two should be peeled off to a new vertex
v_new. The geometry shows edge e2 = (v0, v2) as an interior edge so that its
rightTriangle(v0) is well-defined and non-NULL (= t0).

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0,1,0), v4=(-1,0,0)
  t0=(v0,v1,v2): right outer triangle (ta1 — right of e2)
  t1=(v0,v2,v3): first split-sector triangle
  t2=(v0,v3,v4): second split-sector triangle
  t3=(v0,v4,v1): left outer triangle (ta4 — left of e3)

The split boundary: e2=(v0,v2) interior; e3=(v0,v4) on the other side.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me120",
             title="inverse_collapse_right_triangle_e2: ta1 exists on right side of split edge e2",
             defect_class="inverse_collapse_split_vertex")

v0 = m.vertex( 0.0, 0.0, 0.0)   # 0 — over-merged vertex (to be split)
v1 = m.vertex( 2.0, 0.0, 0.0)   # 1 — right spoke
v2 = m.vertex( 1.0, 1.0, 0.0)   # 2 — e2 far endpoint
v3 = m.vertex( 0.0, 1.0, 0.0)   # 3 — inner spoke
v4 = m.vertex(-1.0, 0.0, 0.0)   # 4 — left spoke / e3 far endpoint

t0 = m.triangle(v0, v1, v2)   # 0 — ta1: right side of e2=(v0,v2)
t1 = m.triangle(v0, v2, v3)   # 1 — split sector upper
t2 = m.triangle(v0, v3, v4)   # 2 — split sector lower
t3 = m.triangle(v0, v4, v1)   # 3 — ta4 candidate: left side of e3=(v0,v4)

# e2 = (v0, v2) is interior: shared by t0 (ta1) and t1.
# This confirms rightTriangle(v0) of e2 is non-NULL.
m.assert_edge_shared(v0, v2, 2)   # e2 interior — ta1 on right side

# e3 = (v0, v4): also interior (shared by t2 and t3).
m.assert_edge_shared(v0, v4, 2)   # e3 interior — ta4 on left side

# Outer edges of the split sector are boundary edges.
m.assert_edge_shared(v2, v3, 1)   # sector edge (boundary)
m.assert_edge_shared(v3, v4, 1)   # sector edge (boundary)

# The four fan edges from v0 each share 2 triangles (interior).
m.assert_edge_shared(v0, v1, 2)   # right spoke
m.assert_edge_shared(v0, v3, 2)   # inner sector edge
