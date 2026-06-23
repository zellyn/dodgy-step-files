"""Me127 — inverse_collapse_edge_e1_update: new edge e1 connects v_new to e2's opposite vertex.

Catalog claim: after vertex split, a second new edge e1 is created connecting
the new vertex v_new to the opposite vertex of e2 (the right split-boundary
edge). Edge e1 = (v_new, v_apex2) forms the third side of new triangle t1.

This exercises MeshFix `Vertex.inverseCollapse` Branch 7 (*edge_e1_update*):
`e1->v1 = v2; e1->v2 = e2->oppositeVertex(this)` — v2 is the new split vertex
and `e2->oppositeVertex(this)` is the far endpoint of the right split-boundary
edge as seen from v0.

Defect carrier: near-coincident vertex pair (v0, v_new) plus the triangle
geometry that results after the split. The edge (v_new, v_apex2) is a new
boundary edge shared by exactly 1 triangle (t1_new), while the edge (v0, v_apex2)
retains its interior role.

Geometry:
  v0=(0,0,0), v_new=(0,1e-4,0), v_apex2=(1,0,0), v_apex3=(-1,0,0)
  Also outer_right=(0.5,-1,0), outer_left=(-0.5,-1,0)

  t0=(v0, v_apex2, v_new): triangle t1 in post-split — edge e1=(v_new,v_apex2)
  t1=(v0, v_new, v_apex3):  triangle t2 in post-split — edge (v_new,v_apex3)
  t2=(v0, outer_right, v_apex2): outer right triangle (ta1)
  t3=(v0, v_apex3, outer_left):  outer left triangle (ta4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me127",
             title="inverse_collapse_edge_e1_update: edge e1 connects v_new to e2 opposite vertex",
             defect_class="inverse_collapse_split_vertex")

v0          = m.vertex( 0.0,   0.0,  0.0)   # 0 — original vertex (this)
vnew        = m.vertex( 0.0,   1e-4, 0.0)   # 1 — new split vertex v2
v_apex2     = m.vertex( 1.0,   0.0,  0.0)   # 2 — e2's opposite vertex (e2 far endpoint)
v_apex3     = m.vertex(-1.0,   0.0,  0.0)   # 3 — e3's opposite vertex
outer_right = m.vertex( 0.5,  -1.0,  0.0)   # 4 — outer right (ta1 side)
outer_left  = m.vertex(-0.5,  -1.0,  0.0)   # 5 — outer left (ta4 side)

t0 = m.triangle(v0, v_apex2, vnew)       # 0 — t1: e=(v0,vnew), e1=(vnew,v_apex2)
t1 = m.triangle(v0, vnew, v_apex3)       # 1 — t2: e=(v0,vnew), e3=(v0,v_apex3)
t2 = m.triangle(v0, outer_right, v_apex2)# 2 — ta1: outer right
t3 = m.triangle(v0, v_apex3, outer_left) # 3 — ta4: outer left

# Central edge e = (v0, vnew) is interior (shared by t0 and t1).
m.assert_edge_shared(v0, vnew, 2)

# New edge e1 = (vnew, v_apex2) — shared only by t0.
m.assert_edge_shared(vnew, v_apex2, 1)   # e1: boundary in current topology

# e2 = (v0, v_apex2) — interior (t0 and t2 share it).
m.assert_edge_shared(v0, v_apex2, 2)     # e2 interior

# e3 = (v0, v_apex3) — interior (t1 and t3 share it).
m.assert_edge_shared(v0, v_apex3, 2)     # e3 interior

# Near-coincident pair demonstrates split-vertex origin.
m.assert_vertex_pair_distance_lt(v0, vnew, 1e-3)
