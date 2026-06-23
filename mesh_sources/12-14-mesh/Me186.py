"""Me186 — split_edge_new_triangle_t1: t1 exists, create nt1 with new edges and update adjacency.

Catalog claim: after ne1=(vn,v3) is created, a new triangle nt1 is created
covering one half of the original t1. The original triangle t1 is trimmed to the
other half. New topology: nt1=(vn, v2, v3) sharing ne1 with the trimmed t1.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 7 (*new_triangle_t1*):
`if (e->t1 != NULL) nt1 = newTriangle(v, e->v1, v3)` (or equivalent) — a new
triangle is allocated and wired into the mesh on the t1 side of the split.

The post-split topology on the t1 side:
  Original t1=(v0,v1,v2) splits into:
    Trimmed t1 = (v0, vn, v2)   — keeps original t1 slot
    nt1        = (vn, v1, v2)   — new triangle, shares ne1=(vn,v2) with trimmed t1

The fixture shows the post-split boundary-edge case (t2=NULL, only t1 side).

Geometry (post-split, boundary edge case):
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,2,0), vn=(1.5,0,0) — midpoint
  t0=(v0,vn,v2): trimmed t1
  t1=(vn,v1,v2): nt1 — the new triangle created by Branch 7
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me186",
             title="split_edge_new_triangle_t1: nt1 created on t1 side after boundary edge split",
             defect_class="split_edge_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left endpoint of original edge
v1 = m.vertex(3.0, 0.0, 0.0)   # 1 — right endpoint of original edge
v2 = m.vertex(1.5, 2.0, 0.0)   # 2 — v3: apex vertex (opposite in t1)
vn = m.vertex(1.5, 0.0, 0.0)   # 3 — new split vertex at midpoint

t0 = m.triangle(v0, vn, v2)   # 0 — trimmed original t1
t1 = m.triangle(vn, v1, v2)   # 1 — nt1: new triangle (Branch 7)

# ne1=(vn,v2): interior edge shared by trimmed t1 and nt1.
m.assert_edge_shared(vn, v2, 2)   # ne1: interior — shared by t0 (trimmed t1) and t1 (nt1)

# Edge halves are boundary (only t1 side; t2=NULL).
m.assert_edge_shared(v0, vn, 1)   # left half of original edge — boundary
m.assert_edge_shared(vn, v1, 1)   # right half — boundary

# Outer boundary spokes.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)

# New vertex vn lies on the original edge.
m.assert_vertex_on_edge(vn, v0, v1)
