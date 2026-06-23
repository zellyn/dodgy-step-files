"""Me126 — inverse_collapse_edge_e_update: central edge e connects this to v_new.

Catalog claim: after vertex split, a new interior edge e is established between
the original vertex v0 (= `this`) and the new vertex v_new (= v2 in MeshFix code).
Edge e is the backbone of the split — it's shared by exactly 2 triangles (t1 and
t2) in the post-split mesh. The pre-split geometry shows the would-be split seam.

This exercises MeshFix `Vertex.inverseCollapse` Branch 6 (*edge_e_update*):
`e->v1 = this; e->v2 = v2` — the central new edge is assigned to connect the
original vertex and the freshly-created split vertex. In the output mesh, this
edge would be interior (shared by exactly 2 triangles: t1 and t2).

Defect carrier: a mesh with a near-coincident vertex pair (v0 at origin, v_new
at 1e-4 offset) already present. The edge between them is an interior seam shared
by 2 triangles. This models the intended post-split topology where e is the spine
of the two new triangles.

Geometry (two-triangle "bowtie base"):
  v0=(0,0,0)  — original vertex (this)
  v_new=(1e-4,0,0) — new split vertex (v2 in MeshFix, near-coincident with v0)
  v_left=(0,1,0)  — left apex
  v_right=(0,-1,0) — right apex
  t0=(v0, v_new, v_left): triangle t1 (uses edge e)
  t1=(v0, v_right, v_new): triangle t2 (uses edge e reversed)

The near-coincident pair (v0, v_new) models the new edge e; both share it.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me126",
             title="inverse_collapse_edge_e_update: central edge e between this and v_new",
             defect_class="inverse_collapse_split_vertex")

v0    = m.vertex(0.0,    0.0,  0.0)   # 0 — original vertex (this)
vnew  = m.vertex(1e-4,   0.0,  0.0)   # 1 — new split vertex v2 (near-coincident)
vleft = m.vertex(0.0,    1.0,  0.0)   # 2 — left apex
vright= m.vertex(0.0,   -1.0,  0.0)   # 3 — right apex

t0 = m.triangle(v0, vnew, vleft)    # 0 — t1: shares edge e=(v0,vnew)
t1 = m.triangle(v0, vright, vnew)   # 1 — t2: shares edge e=(v0,vnew) reversed

# The central edge e = (v0, v_new) is interior (shared by both t0 and t1).
m.assert_edge_shared(v0, vnew, 2)   # edge e: the spine of the split

# Near-coincident pair demonstrates that v_new is a freshly-split vertex.
m.assert_vertex_pair_distance_lt(v0, vnew, 1e-3)

# Outer edges are boundary.
m.assert_edge_shared(v0,    vleft,  1)
m.assert_edge_shared(vnew,  vleft,  1)
m.assert_edge_shared(v0,    vright, 1)
m.assert_edge_shared(vnew,  vright, 1)
