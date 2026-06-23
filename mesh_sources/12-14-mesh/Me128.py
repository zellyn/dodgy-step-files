"""Me128 — inverse_collapse_triangle_t1_setup: new triangle t1 uses edges e, e1, e2.

Catalog claim: after vertex split, new triangle t1 is formed by three edges:
the central split edge e = (v0, v_new), the new edge e1 = (v_new, apex2), and
the original right-boundary edge e2 = (v0, apex2). These three edges form a
closed triangle. The t1 edge assignment `t1->e1=e; t1->e2=e1; t1->e3=e2` is
Branch 8 of inverseCollapse.

This exercises MeshFix `Vertex.inverseCollapse` Branch 8 (*triangle_t1_setup*):
`t1->e1 = e; t1->e2 = e1; t1->e3 = e2` — the three edges that bound new
triangle t1 on the v0 side of the split are assigned.

Defect carrier: a triangle with vertices v0, v_new, apex2 where:
  - (v0, v_new) is the split edge e (interior to the split pair, shared with t2)
  - (v_new, apex2) is the new edge e1 (boundary)
  - (v0, apex2) is e2 (shared with an outer triangle ta1)

All three edges of t1 are tracked by assertions; the triangle is validated as
having the correct three edges via edge incidence checks.

Geometry:
  v0=(0,0,0), v_new=(0.5e-4,0,0), apex2=(1,1,0), apex3=(1,-1,0)
  t1=(v0, v_new, apex2) — new triangle with edges {e, e1, e2}
  t2=(v0, apex3, v_new) — partner new triangle with edges {e, e3, e4}
  outer_t1=(v0, apex2, apex4=(2,0,0)) — ta1 outer right
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me128",
             title="inverse_collapse_triangle_t1_setup: t1 bounded by edges e, e1, e2",
             defect_class="inverse_collapse_split_vertex")

v0    = m.vertex(0.0,    0.0,  0.0)   # 0 — original vertex (this)
vnew  = m.vertex(5e-5,   0.0,  0.0)   # 1 — new split vertex v2
apex2 = m.vertex(1.0,    1.0,  0.0)   # 2 — e2's far endpoint (opposite vertex)
apex3 = m.vertex(1.0,   -1.0,  0.0)   # 3 — e3's far endpoint
apex4 = m.vertex(2.0,    0.0,  0.0)   # 4 — outer right far vertex (ta1)
apex5 = m.vertex(2.0,   -2.0,  0.0)   # 5 — outer left far vertex (ta4)

# The two new triangles from the split.
t1_new = m.triangle(v0, vnew, apex2)     # 0 — t1: {e=(v0,vnew), e1=(vnew,apex2), e2=(v0,apex2)}
t2_new = m.triangle(v0, apex3, vnew)     # 1 — t2: {e=(v0,vnew), e3=(v0,apex3), e4=(apex3,vnew)}
# Outer triangles (ta1, ta4) that were already present.
ta1 = m.triangle(v0, apex2, apex4)       # 2 — ta1: outer right (shares e2=(v0,apex2))
ta4 = m.triangle(v0, apex5, apex3)       # 3 — ta4: outer left (shares e3=(v0,apex3))

# Central split edge e = (v0, vnew): shared by t1_new and t2_new.
m.assert_edge_shared(v0, vnew, 2)        # e: interior to split pair

# New edge e1 = (vnew, apex2): boundary (only t1_new).
m.assert_edge_shared(vnew, apex2, 1)     # e1: boundary

# e2 = (v0, apex2): interior (t1_new and ta1).
m.assert_edge_shared(v0, apex2, 2)       # e2: interior

# Near-coincident pair.
m.assert_vertex_pair_distance_lt(v0, vnew, 1e-3)

# e3 and e4 for t2.
m.assert_edge_shared(v0, apex3, 2)       # e3: interior (t2_new and ta4)
m.assert_edge_shared(vnew, apex3, 1)     # e4: boundary (only t2_new)
