"""Me880 — duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V1: edge v1 missing from VE list.

MeshFix `checkAndRepair::duplicateNonManifoldVertices` Branch 1
(*NONMANIFOLD_VERTEX_AT_V1*) @ line 139:
  'if (e->v1->VE()->containsNode(e) == NULL) { ... }'
  — for every edge e the algorithm checks whether e appears in v1's
  edge-valence (VE) list. When v1 is a non-manifold "bowtie" vertex its
  fan is split into two disconnected components; the edge e that belongs
  to the second fan component is absent from v1's VE list, so
  containsNode(e) returns NULL and Branch 1 fires. The repair duplicates
  v1 so that each fan component receives its own copy.

Defect pattern: vertex v0 is the bowtie pinch at v1's role. Two triangle
  fans meet at v0 but share no edge through it — the upper fan (t0, t1)
  and the lower fan (t2, t3) are connected only through v0. Edge (v0,v1)
  belongs to the upper fan; v0 is absent from the VE list of edges in
  the lower fan because the fans are topologically disconnected.

Geometry (6 triangles, 7 vertices):
  v0=(0,0,0)   — bowtie / non-manifold vertex (plays role of e->v1)
  Upper fan: v1=(1,1,0), v2=(-1,1,0), v3=(0,2,0)
    t0=(v0,v1,v3), t1=(v0,v3,v2)  — upper left and right triangles
  Lower fan: v4=(1,-1,0), v5=(-1,-1,0), v6=(0,-2,0)
    t2=(v0,v6,v4), t3=(v0,v5,v6)  — lower right and left triangles
  The upper and lower fans share only v0; no edge connects them.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me880",
    title="duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V1: bowtie vertex v0 missing from edge VE list (Branch 1)",
    defect_class="non_manifold_vertex",
)

# Bowtie vertex — plays the role of e->v1 in Branch 1 check.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — non-manifold pinch vertex

# Upper fan vertices.
v1 = m.vertex(1.0,  1.0, 0.0)   # 1
v2 = m.vertex(-1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0,  2.0, 0.0)   # 3

# Lower fan vertices.
v4 = m.vertex(1.0, -1.0, 0.0)   # 4
v5 = m.vertex(-1.0, -1.0, 0.0)  # 5
v6 = m.vertex(0.0, -2.0, 0.0)   # 6

# Upper fan: two triangles sharing interior edge (v0, v3).
t0 = m.triangle(v0, v1, v3)   # 0: upper-right
t1 = m.triangle(v0, v3, v2)   # 1: upper-left

# Lower fan: two triangles sharing interior edge (v0, v6).
t2 = m.triangle(v0, v6, v4)   # 2: lower-right
t3 = m.triangle(v0, v5, v6)   # 3: lower-left

# Interior edges within each fan (shared by 2 triangles).
m.assert_edge_shared(v0, v3, 2)   # upper fan interior edge
m.assert_edge_shared(v0, v6, 2)   # lower fan interior edge

# Boundary edges of the upper fan.
m.assert_edge_shared(v0, v1, 1)   # upper boundary
m.assert_edge_shared(v0, v2, 1)   # upper boundary

# Boundary edges of the lower fan.
m.assert_edge_shared(v0, v4, 1)   # lower boundary
m.assert_edge_shared(v0, v5, 1)   # lower boundary

# v0's triangle fan is split into 2 disconnected components — the
# defining structural signature that makes containsNode(e)==NULL fire
# for edges in the second fan component (Branch 1).
m.assert_vertex_fan_disconnected(v0)
