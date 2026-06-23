"""Me073 — duplicate_singular_vertices: bowtie with multi-triangle upper fan.

Catalog claim: vertex 0 is a non-manifold (singular) vertex with 2 link CCs.
The upper fan is a proper manifold triangle strip (3 triangles forming a wedge)
and the lower fan is a single triangle. This exercises Branch 7 (*link_traversal_cw*)
— the link-CC algorithm must traverse the **full closed ring** of 3 triangles in
the upper fan by walking clockwise around v0 before concluding that the upper fan
is a single CC. The contrast with Me070 (two single triangles) means the CW walk
makes 3 steps instead of 1 before returning to the start.

Layout (upper fan = 3-triangle wedge above v0; lower = single triangle below):
  v1=(0,1,0) v2=(1,1,0) v3=(2,0,0)   ← upper-fan outer vertices
  v0=(1,0,0)                          ← singular vertex
  v4=(0,-1,0) v5=(2,-1,0)            ← lower fan

Upper fan (CCW): t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v5) ← closed strip
Wait — these need to share edges at v0 to be connected within the fan.

Revised layout (3-triangle fan around v0 in the upper half):
  v1=(-1,1,0)  v2=(0,1,0)  v3=(1,1,0)  v4=(2,0,0) ← outer rim of upper fan
  v0=(0,0,0)                                         ← singular vertex
  Upper fan: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4)
    → edges (v0,v2) shared by t0/t1; (v0,v3) shared by t1/t2 → fully connected fan ring
  Lower fan: t3=(v0,v5,v6)  v5=(1,-1,0)  v6=(-1,-1,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me073",
             title="duplicate_singular_vertices: bowtie with 3-triangle upper fan and 1-triangle lower fan",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — singular bowtie vertex
# Upper fan outer rim
v1 = m.vertex(-1.0, 1.0, 0.0)  # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4
# Lower fan
v5 = m.vertex(1.0, -1.0, 0.0)  # 5
v6 = m.vertex(-1.0, -1.0, 0.0) # 6

# Upper fan — 3 triangles sharing edges at v0.
t0 = m.triangle(v0, v1, v2)   # shares (v0,v2) with t1
t1 = m.triangle(v0, v2, v3)   # shares (v0,v2) with t0; (v0,v3) with t2
t2 = m.triangle(v0, v3, v4)   # shares (v0,v3) with t1

# Lower fan — single triangle, no shared edge with upper fan.
t3 = m.triangle(v0, v5, v6)

# Interior edges in the upper fan (shared by 2 triangles).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Boundary edges on the outer rim of the upper fan.
m.assert_edge_shared(v0, v1, 1)   # boundary — only t0
m.assert_edge_shared(v0, v4, 1)   # boundary — only t2

# Lower fan — boundary edges.
m.assert_edge_shared(v0, v5, 1)   # boundary — only t3
m.assert_edge_shared(v0, v6, 1)   # boundary — only t3

# v0's link has 2 CCs: the connected upper fan (t0,t1,t2) and the isolated lower fan (t3).
m.assert_vertex_fan_disconnected(v0)
