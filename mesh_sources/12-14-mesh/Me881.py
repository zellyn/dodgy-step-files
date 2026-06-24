"""Me881 — duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V2: edge v2 missing from VE list.

MeshFix `checkAndRepair::duplicateNonManifoldVertices` Branch 2
(*NONMANIFOLD_VERTEX_AT_V2*) @ line 156:
  'if (e->v2->VE()->containsNode(e) == NULL) { ... }'
  — analogous to Branch 1 but checks the other endpoint of each edge.
  When v2 is a non-manifold bowtie vertex, an edge e in its second fan
  component is absent from v2's VE list so containsNode(e) returns NULL
  and Branch 2 fires. The repair duplicates v2 so each fan receives its
  own vertex copy.

Defect pattern: vertex v0 is the bowtie pinch vertex playing the role of
  e->v2. Two triangle fans meet at v0 but share no edge through it. Edge
  (v1,v0) belongs to the right fan; v0 is absent from the VE list of
  edges in the left fan — Branch 2 fires for those edges.

Geometry (6 triangles, 7 vertices):
  v0=(0,0,0)   — bowtie vertex (plays role of e->v2)
  Right fan: v1=(2,1,0), v2=(2,-1,0), v3=(3,0,0)
    t0=(v1,v0,v3), t1=(v3,v0,v2)  — right fan around v0
  Left fan:  v4=(-2,1,0), v5=(-2,-1,0), v6=(-3,0,0)
    t2=(v4,v6,v0), t3=(v0,v6,v5)  — left fan around v0
  The right and left fans share only v0; no edge connects them.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me881",
    title="duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V2: bowtie vertex v0 missing from edge VE list as v2 (Branch 2)",
    defect_class="non_manifold_vertex",
)

# Bowtie vertex — plays the role of e->v2 in Branch 2 check.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — non-manifold pinch vertex

# Right fan vertices.
v1 = m.vertex(2.0,  1.0, 0.0)   # 1
v2 = m.vertex(2.0, -1.0, 0.0)   # 2
v3 = m.vertex(3.0,  0.0, 0.0)   # 3

# Left fan vertices.
v4 = m.vertex(-2.0,  1.0, 0.0)  # 4
v5 = m.vertex(-2.0, -1.0, 0.0)  # 5
v6 = m.vertex(-3.0,  0.0, 0.0)  # 6

# Right fan: two triangles sharing interior edge (v0, v3).
t0 = m.triangle(v1, v0, v3)   # 0: right-upper
t1 = m.triangle(v3, v0, v2)   # 1: right-lower

# Left fan: two triangles sharing interior edge (v0, v6).
t2 = m.triangle(v4, v6, v0)   # 2: left-upper
t3 = m.triangle(v0, v6, v5)   # 3: left-lower

# Interior edges within each fan (shared by 2 triangles).
m.assert_edge_shared(v0, v3, 2)   # right fan interior edge
m.assert_edge_shared(v0, v6, 2)   # left fan interior edge

# Boundary edges of the right fan.
m.assert_edge_shared(v0, v1, 1)   # right boundary
m.assert_edge_shared(v0, v2, 1)   # right boundary

# Boundary edges of the left fan.
m.assert_edge_shared(v0, v4, 1)   # left boundary
m.assert_edge_shared(v0, v5, 1)   # left boundary

# v0's triangle fan is split into 2 disconnected components — the
# structural signature causing containsNode(e)==NULL for edges in the
# second fan component when v0 is checked as e->v2 (Branch 2).
m.assert_vertex_fan_disconnected(v0)
