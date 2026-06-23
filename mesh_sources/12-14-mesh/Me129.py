"""Me129 — inverse_collapse_edge_triangle_adjacency: e2 and e3 triangle refs updated to t1/t2.

Catalog claim: after vertex split, the split-boundary edges e2 and e3 must have
their triangle-adjacency references updated: e2 replaces its reference to ta1
with t1 (the new triangle on v0's side), and e3 replaces its reference to ta4
with t2. This is the adjacency-propagation step that makes the mesh consistent.

This exercises MeshFix `Vertex.inverseCollapse` Branch 10
(*edge_triangle_adjacency*): `e2->replaceTriangle(ta1, t1)` and
`e3->replaceTriangle(ta4, t2)` — the two boundary edges of the sector update
their neighbor pointers from the old outer triangles to the new ones.

Defect carrier: a completed inverse-collapse configuration where edges e2 and
e3 each are shared by two triangles — one is the new split triangle (t1 or t2)
and the other is the outer triangle (ta1 or ta4). The assertion confirms both
e2 and e3 are interior (n=2) so the replaceTriangle call is meaningful.

This fixture also confirms Branch 9 (*triangle_t2_setup*): t2 uses edges
{e, e3, e4} where e4=(v_new, apex3). Both t2 setup and adjacency propagation
are captured in the same topology.

Geometry (post-split configuration):
  v0=(0,0,0), v_new=(0,2e-4,0), apex2=(1,0,0), apex3=(-1,0,0),
  outer_apex=(0,2,0)

  t1=(v0, v_new, apex2): new t1 bounded by e, e1, e2
  t2=(v0, apex3, v_new): new t2 bounded by e, e3, e4 (Branch 9 + Branch 10)
  ta1=(v0, apex2, outer_apex): outer right (e2 was adjacent to ta1; now to t1)
  ta4=(v0, outer_apex, apex3): outer left (e3 was adjacent to ta4; now to t2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me129",
             title="inverse_collapse_edge_triangle_adjacency: e2/e3 refs updated to t1/t2 (Branch 9+10)",
             defect_class="inverse_collapse_split_vertex")

v0         = m.vertex( 0.0,  0.0,  0.0)   # 0 — original vertex (this)
vnew       = m.vertex( 0.0,  2e-4, 0.0)   # 1 — new split vertex v2
apex2      = m.vertex( 1.0,  0.0,  0.0)   # 2 — e2 far endpoint
apex3      = m.vertex(-1.0,  0.0,  0.0)   # 3 — e3 far endpoint
outer_apex = m.vertex( 0.0,  2.0,  0.0)   # 4 — outer far vertex (shared by ta1, ta4)

t1_new = m.triangle(v0, vnew,  apex2)      # 0 — new t1: edges {e, e1=(vnew,apex2), e2=(v0,apex2)}
t2_new = m.triangle(v0, apex3, vnew)       # 1 — new t2: edges {e, e3=(v0,apex3), e4=(apex3,vnew)}
ta1    = m.triangle(v0, apex2, outer_apex) # 2 — ta1: outer right, shares e2=(v0,apex2)
ta4    = m.triangle(v0, outer_apex, apex3) # 3 — ta4: outer left, shares e3=(v0,apex3)

# Central edge e = (v0, vnew): interior, shared by t1_new and t2_new.
m.assert_edge_shared(v0, vnew, 2)          # e: spine of split

# e2 = (v0, apex2): interior, shared by t1_new and ta1.
# replaceTriangle(ta1, t1) updates e2 so t1_new replaces ta1 here.
m.assert_edge_shared(v0, apex2, 2)         # e2: interior after adjacency update

# e3 = (v0, apex3): interior, shared by t2_new and ta4.
# replaceTriangle(ta4, t2) updates e3 so t2_new replaces ta4 here.
m.assert_edge_shared(v0, apex3, 2)         # e3: interior after adjacency update

# New boundary edges e1 and e4.
m.assert_edge_shared(vnew, apex2, 1)       # e1: boundary (only t1_new)
m.assert_edge_shared(apex3, vnew, 1)       # e4: boundary (only t2_new)

# Near-coincident pair indicates split vertex.
m.assert_vertex_pair_distance_lt(v0, vnew, 1e-3)
