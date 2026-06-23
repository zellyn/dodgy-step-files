"""Me121 — inverse_collapse_left_triangle_e3: e3 has a left-side triangle (ta4 extraction).

Catalog claim: vertex v0 is an over-merged fan vertex. The split boundary edge
e3 (left edge of the split sector) has a triangle ta4 on its left side — the
second adjacency extraction in inverseCollapse. ta4 becomes the outer neighbor
of new triangle t2 after the split.

This exercises MeshFix `Vertex.inverseCollapse` Branch 2 (*left_triangle_e3*):
`ta4 = e3->leftTriangle(this)` — the code extracts the triangle on the LEFT side
of edge e3 with respect to vertex `this`. Combined with Branch 1, both outer
neighbors are captured before the new triangles are constructed.

Defect carrier: a 3-triangle fan at v0 where e3 = (v0, v3) is an interior edge
with a triangle ta4 on its left side. The split sector contains only t1 (one
triangle). After split, v0 retains t0+t1 and v_new takes t_new + ta4's side.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-1,0,0)
  t0=(v0,v1,v2): right outer triangle (ta1 side)
  t1=(v0,v2,v3): single split-sector triangle
  t2=(v0,v3,v1): left outer triangle (ta4 — left of e3=(v0,v3))

Here e2=(v0,v2) is the right split boundary and e3=(v0,v3) is the left.
ta4 = leftTriangle(v0) of e3 = t2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me121",
             title="inverse_collapse_left_triangle_e3: ta4 exists on left side of split edge e3",
             defect_class="inverse_collapse_split_vertex")

v0 = m.vertex( 0.0, 0.0, 0.0)   # 0 — over-merged vertex (to be split)
v1 = m.vertex( 1.0, 0.0, 0.0)   # 1 — right spoke
v2 = m.vertex( 0.5, 1.0, 0.0)   # 2 — e2 far endpoint
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3 — e3 far endpoint / left spoke

t0 = m.triangle(v0, v1, v2)   # 0 — ta1 (right outer)
t1 = m.triangle(v0, v2, v3)   # 1 — split sector
t2 = m.triangle(v0, v3, v1)   # 2 — ta4: left side of e3=(v0,v3)

# e3 = (v0, v3) is interior: shared by t1 (sector) and t2 (ta4).
# leftTriangle(v0) of e3 is non-NULL (= t2).
m.assert_edge_shared(v0, v3, 2)   # e3 interior — ta4 on left side

# e2 = (v0, v2) is interior: shared by t0 (ta1) and t1 (sector).
m.assert_edge_shared(v0, v2, 2)   # e2 interior — ta1 on right side

# All three edges from v0 are interior in this closed 3-triangle fan.
m.assert_edge_shared(v0, v1, 2)   # right spoke (shared by t0 and t2)

# Outer sector edge (v2, v3) is a boundary edge.
m.assert_edge_shared(v2, v3, 1)   # sector outer edge (boundary)
