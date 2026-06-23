"""Me124 — inverse_collapse_vertex_redirection: intermediate edges redirected to v2.

Catalog claim: vertex v0 has a 5-triangle fan with a 2-triangle split sector.
The intermediate edge between e3 and e2 in the ring (the spokes that belong to
the new vertex v_new after the split) must be redirected: `f->replaceVertex(this, v2)`.
This branch fires for every edge f encountered between e3 and e2 in the ring.

This exercises MeshFix `Vertex.inverseCollapse` Branch 5
(*vertex_redirection_e2_to_e3*): the inner loop `while (f != e2) { f->replaceVertex(this,
v2); f = f->nextEdge(v2) }` — every edge in the split sector (not including e2
itself) is moved from v0 to the new v_new. With 2 triangles in the sector there
is exactly 1 intermediate edge to redirect.

Defect carrier: 5-triangle partially-open fan at v0 where the 2-triangle split
sector has one internal edge (v0, v3) that needs to be redirected to v_new.

Geometry (open boundary fan):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0,1,0), v4=(-0.5,1,0), v5=(-1,0,0)
  t0=(v0,v1,v2): right outer
  t1=(v0,v2,v3): sector start (e2=(v0,v2))
  t2=(v0,v3,v4): sector interior — the edge (v0,v3) is redirected
  t3=(v0,v4,v5): sector end (e3=(v0,v4))
  t4=(v0,v5,v1): left outer

The edge (v0, v3) between e2=(v0,v2) and e3=(v0,v4) is the intermediate edge
that gets redirected to v_new in the `replaceVertex` pass.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me124",
             title="inverse_collapse_vertex_redirection: 1 intermediate edge redirected from v0 to v_new",
             defect_class="inverse_collapse_split_vertex")

v0 = m.vertex( 0.0,  0.0, 0.0)   # 0 — vertex to split
v1 = m.vertex( 1.0,  0.0, 0.0)   # 1 — right spoke
v2 = m.vertex( 0.5,  1.0, 0.0)   # 2 — e2 far endpoint (split boundary right)
v3 = m.vertex( 0.0,  1.0, 0.0)   # 3 — sector interior spoke (TO BE REDIRECTED)
v4 = m.vertex(-0.5,  1.0, 0.0)   # 4 — e3 far endpoint (split boundary left)
v5 = m.vertex(-1.0,  0.0, 0.0)   # 5 — left spoke

t0 = m.triangle(v0, v1, v2)   # 0 — right outer (ta1)
t1 = m.triangle(v0, v2, v3)   # 1 — sector (e2=(v0,v2))
t2 = m.triangle(v0, v3, v4)   # 2 — sector (intermediate, redirected edge (v0,v3))
t3 = m.triangle(v0, v4, v5)   # 3 — sector (e3=(v0,v4))
t4 = m.triangle(v0, v5, v1)   # 4 — left outer (ta4)

# e2 = (v0, v2) interior: shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)
# e3 = (v0, v4) interior: shared by t3 and t4.
m.assert_edge_shared(v0, v4, 2)
# Intermediate sector edge (v0, v3) — shared by t1 and t2 — will be redirected.
m.assert_edge_shared(v0, v3, 2)

# All fan spoke edges are interior (this is a closed 5-fan).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v5, 2)

# Sector outer edges are boundary.
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
