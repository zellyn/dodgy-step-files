"""Me079 — duplicate_singular_vertices: non-manifold vertex shared by a larger manifold patch.

Catalog claim: vertex 0 is a non-manifold (singular) vertex with 2 link CCs,
where one fan is a connected manifold quad-strip (4 triangles forming a
rectangular patch) and the other fan is a separate triangle. This is a
realistic scenario: a mostly-valid mesh where one bowtie point arises from
an incomplete weld between two patches.

This exercises Branch 12 (*polygon_index_replacement*): the 4 quad-strip
triangles all reference v0 and must have their vertex index updated to the new
duplicate. The polygon_index_replacement sub-pass must update 4 polygon entries
for the quad-strip CC, not just 1.

Layout:
  Quad-strip (4 triangles, all connected at v0):
    v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,1,0), v4=(0,2,0), v5=(1,2,0)
    t0=(v0,v1,v2), t1=(v1,v3,v2) ← lower quad
    t2=(v2,v3,v4), t3=(v3,v5,v4) ← upper quad
    → t0 uses v0; t1 does NOT use v0; t2 does NOT use v0; t3 does NOT use v0
    — so only 1 triangle in the strip directly uses v0! The edge (v0,v2) is
    shared by t0. Actually let me use a strip where v0 IS in multiple triangles:

Revised layout (v0 is a shared interior vertex of the patch):
    Strip sharing v0: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1)
      — but this forms a closed ring (Me076). Use open strip:
    Open strip: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4) — 3 triangles
    Isolated fan: t3=(v0,v5,v6) — separate.
    Already done in Me077 (3-triangle strip). Use 4 triangles for Me079.

Revised (4-triangle open strip + 1 isolated):
  v0=(0,0,0), outer ring: v1=(-2,1,0), v2=(-1,1,0), v3=(0,1.5,0), v4=(1,1,0), v5=(2,1,0)
  Strip: t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v5)
  Isolated: t4=(v0,v6,v7) — v6=(1,-1,0), v7=(-1,-1,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me079",
             title="duplicate_singular_vertices: 4-triangle open-strip fan plus isolated lower fan at bowtie vertex",
             defect_class="non_manifold_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — singular bowtie vertex

# Open-strip upper fan outer rim (5 vertices).
v1 = m.vertex(-2.0, 1.0, 0.0)   # 1 — leftmost
v2 = m.vertex(-1.0, 1.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.5, 0.0)    # 3 — top
v4 = m.vertex(1.0, 1.0, 0.0)    # 4
v5 = m.vertex(2.0, 1.0, 0.0)    # 5 — rightmost

# Isolated lower fan.
v6 = m.vertex(1.0, -1.0, 0.0)   # 6
v7 = m.vertex(-1.0, -1.0, 0.0)  # 7

# 4-triangle open strip — all sharing v0.
t0 = m.triangle(v0, v1, v2)   # (v0,v2) shared with t1
t1 = m.triangle(v0, v2, v3)   # (v0,v2) shared with t0; (v0,v3) shared with t2
t2 = m.triangle(v0, v3, v4)   # (v0,v3) shared with t1; (v0,v4) shared with t3
t3 = m.triangle(v0, v4, v5)   # (v0,v4) shared with t2

# Isolated lower fan.
t4 = m.triangle(v0, v6, v7)

# Interior shared edges within the upper strip.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# Boundary edges of upper strip.
m.assert_edge_shared(v0, v1, 1)   # left boundary
m.assert_edge_shared(v0, v5, 1)   # right boundary

# Boundary edges of lower fan.
m.assert_edge_shared(v0, v6, 1)
m.assert_edge_shared(v0, v7, 1)

# v0's link has 2 CCs: upper strip (t0–t3) and lower fan (t4).
m.assert_vertex_fan_disconnected(v0)
